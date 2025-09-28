# recognizer.py

import librosa
import numpy as np
from scipy.signal import correlate
import warnings

warnings.filterwarnings('ignore')

# Just gives a rough estimate
def find_whole_song_in_mix(song_chroma, mix_chroma, sr, hop_length=512):
    """
    Finds the start and end time of a song within a mix using cross-correlation.
    """
    print("Searching for song in mix...")
    
    song_norm = (song_chroma - np.mean(song_chroma)) / np.std(song_chroma)
    mix_norm = (mix_chroma - np.mean(mix_chroma)) / np.std(mix_chroma)

    correlation = correlate(mix_norm, song_norm, mode='valid', method='fft')
    time_correlation = np.sum(correlation, axis=0)
    best_match_frame = np.argmax(time_correlation)
    best_match_score = time_correlation[best_match_frame]

    # Heuristic: set a minimum confidence threshold (tune as needed)
    CONFIDENCE_THRESHOLD = 10000  # You may need to tune this value
    print(f"Best match score: {best_match_score:.2f}")
    if best_match_score < CONFIDENCE_THRESHOLD:
        print("No real match found: best match score below threshold.")
        return None, None

    start_time = librosa.frames_to_time(best_match_frame, sr=sr, hop_length=hop_length)

    song_duration_frames = song_chroma.shape[1]
    song_duration_secs = librosa.frames_to_time(song_duration_frames, sr=sr, hop_length=hop_length)
    end_time = start_time + song_duration_secs
    
    print(f"Match found! Estimated start: {start_time:.2f}s, Estimated end: {end_time:.2f}s")

    # Add it to some data structure to later find transitions

    return start_time, end_time


# This is completely deprecated now
def refine_whole_match(song_chroma, mix_chroma, rough_start_time, sr, hop_length=512, threshold=0.8, chunk_size=10):
    """
    Refine the rough alignment by checking chunk similarity.
    Returns the (refined_start_frame, refined_end_frame).
    """
    rough_start_frame = librosa.time_to_frames(rough_start_time, sr=sr, hop_length=hop_length)

    n_chunks = song_chroma.shape[1] // chunk_size
    start_chunk, end_chunk = None, None

    # Ensure rough_start_frame is an integer index for slicing
    rough_start_idx = int(np.floor(rough_start_frame))

    for i in range(n_chunks):
        song_chunk = song_chroma[:, i*chunk_size:(i+1)*chunk_size]
        mix_start = rough_start_idx + i*chunk_size
        mix_end = rough_start_idx + (i+1)*chunk_size
        mix_chunk = mix_chroma[:, mix_start:mix_end]
        if mix_chunk.shape[1] != chunk_size:
            break  # End of mix

        # Cosine similarity
        sim = np.dot(song_chunk.flatten(), mix_chunk.flatten()) / (
            np.linalg.norm(song_chunk.flatten()) * np.linalg.norm(mix_chunk.flatten()) + 1e-8
        )
        if sim > threshold:
            if start_chunk is None:
                start_chunk = i
            end_chunk = i

    if start_chunk is not None and end_chunk is not None:
        refined_start = librosa.frames_to_time(rough_start_frame + start_chunk * chunk_size, sr=sr, hop_length=hop_length)
        refined_end = librosa.frames_to_time(rough_start_frame + (end_chunk + 1) * chunk_size, sr=sr, hop_length=hop_length)
        print(f"Refined match! Start: {refined_start}, End: {refined_end}")
        return refined_start, refined_end
    else:
        return None, None



# This is where the useful newish stuff is
def find_isometric_chunk_matches(song_chroma, mix_chroma, sr, hop_length=512, chunk_seconds=5, n_chunks=30):
    """
    For each of n_chunks (evenly spaced) in the song, use cross-correlation to find the best match in the mix (like find_whole_song_in_mix).
    Returns a list of (chunk_idx, song_start_frame, best_mix_start_frame, best_match_score).
    """
    from scipy.signal import correlate
    chunk_size = librosa.time_to_frames(chunk_seconds, sr=sr, hop_length=hop_length)
    song_len = song_chroma.shape[1]
    mix_len = mix_chroma.shape[1]
    chunk_indices = np.linspace(0, song_len - chunk_size, n_chunks, dtype=int)
    matches = []
    for i, chunk_start in enumerate(chunk_indices):
        song_chunk = song_chroma[:, chunk_start:chunk_start+chunk_size]
        # Normalize
        song_chunk_norm = (song_chunk - np.mean(song_chunk)) / (np.std(song_chunk) + 1e-8)
        mix_norm = (mix_chroma - np.mean(mix_chroma)) / (np.std(mix_chroma) + 1e-8)
        # Cross-correlation along time axis
        correlation = correlate(mix_norm, song_chunk_norm, mode='valid', method='fft')
        time_correlation = np.sum(correlation, axis=0)
        best_match_frame = np.argmax(time_correlation)
        best_match_score = time_correlation[best_match_frame]
        matches.append((i, chunk_start, best_match_frame, best_match_score))

    return matches

def find_largest_isometry(matches, chunk_size, tol=100):
    """
    Given matches: (i, song_start, mix_best_start, sim), find the largest subset where f(b)-f(a) == b-a (within tol frames).
    Returns (anchor_song_start, anchor_mix_start, anchor_indices)
    """
    n = len(matches)
    best_count = 0
    best_indices = []
    anchor_song_start = None
    anchor_mix_start = None
    for i in range(n):
        indices = [i]
        a_song, a_mix = matches[i][1], matches[i][2]
        for j in range(n):
            if i == j:
                continue
            b_song, b_mix = matches[j][1], matches[j][2]
            if b_mix is None or a_mix is None:
                continue
            # Check isometry: (b_mix - a_mix) == (b_song - a_song) within tol
            if abs((b_mix - a_mix) - (b_song - a_song)) <= tol:
                indices.append(j)
        if len(indices) > best_count:
            best_count = len(indices)
            best_indices = indices
            anchor_song_start = a_song
            anchor_mix_start = a_mix
    return anchor_song_start, anchor_mix_start, best_indices

def expand_isometry(song_chroma, mix_chroma, first_chunk_start, first_mix_start, last_chunk_start, last_mix_start, chunk_size, sim_threshold=0.6):
    """
    Expand only before the first matched chunk and after the last matched chunk, checking bounds.
    Returns (refined_song_start, refined_mix_start, refined_song_end, refined_mix_end)
    """
    song_len = song_chroma.shape[1]
    mix_len = mix_chroma.shape[1]
    # Expand backwards from first matched chunk
    s, m = first_chunk_start, first_mix_start
    while s - chunk_size >= 0 and m - chunk_size >= 0:
        song_chunk = song_chroma[:, s-chunk_size:s]
        mix_chunk = mix_chroma[:, m-chunk_size:m]
        sim = np.dot(song_chunk.flatten(), mix_chunk.flatten()) / (
            np.linalg.norm(song_chunk.flatten()) * np.linalg.norm(mix_chunk.flatten()) + 1e-8
        )
        if sim < sim_threshold:
            break
        s -= chunk_size
        m -= chunk_size
    refined_song_start, refined_mix_start = s, m
    # Expand forwards from last matched chunk
    
    s, m = last_chunk_start, last_mix_start
    
    while s + chunk_size <= song_len and m + chunk_size <= mix_len:
        song_chunk = song_chroma[:, s:s+chunk_size]
        mix_chunk = mix_chroma[:, m:m+chunk_size]
        sim = np.dot(song_chunk.flatten(), mix_chunk.flatten()) / (
            np.linalg.norm(song_chunk.flatten()) * np.linalg.norm(mix_chunk.flatten()) + 1e-8
        )
        if sim < sim_threshold:
            break
        s += chunk_size
        m += chunk_size
    
    refined_song_end, refined_mix_end = s, m
    

    return refined_song_start, refined_mix_start, refined_song_end, refined_mix_end



# Loser helper function
def chunk_sim(song_idx, mix_idx, song_len, mix_len, song_chroma, mix_chroma, size):
    if song_idx < 0 or mix_idx < 0 or song_idx + size > song_len or mix_idx + size > mix_len:
        return -1  # Out of bounds
    song_chunk = song_chroma[:, song_idx:song_idx+size]
    mix_chunk = mix_chroma[:, mix_idx:mix_idx+size]
    sim = np.dot(song_chunk.flatten(), mix_chunk.flatten()) / (
        np.linalg.norm(song_chunk.flatten()) * np.linalg.norm(mix_chunk.flatten()) + 1e-8
    )
    return sim




def refine_outer_chunks(song_chroma, mix_chroma, song_start, mix_start, song_end, mix_end, sr, hop_length=512, initial_chunk_size=0, min_chunk_factor=4, sim_threshold=0.8):
    """
    Refine the outer boundaries of the matched region by recursively adding or removing smaller chunks.
    - initial_chunk_size: the chunk size used in expand_isometry (in frames)
    - min_chunk_factor: the minimum chunk size is initial_chunk_size divided by 2**min_chunk_factor
    Returns refined (song_start, mix_start, song_end, mix_end) in frames.
    """
    # Calculate minimum chunk size based on min_chunk_factor
    min_chunk_size = max(1, initial_chunk_size // (2 ** min_chunk_factor))

    song_len = song_chroma.shape[1]
    mix_len = mix_chroma.shape[1]
    chunk_size = initial_chunk_size if initial_chunk_size > 0 else librosa.time_to_frames(2, sr=sr, hop_length=hop_length)


    # Try to expand and trim at each scale
    temp = chunk_size
    while temp >= min_chunk_size:
        # Try to trim from start
        sim_trim_start = chunk_sim(song_start, mix_start, song_len, mix_len, song_chroma, mix_chroma, temp)
        if sim_trim_start < sim_threshold:
            song_start += temp
            mix_start += temp
        # Try to trim from end
        sim_trim_end = chunk_sim(song_end - temp, mix_end - temp, song_len, mix_len, song_chroma, mix_chroma, temp)
        if sim_trim_end < sim_threshold:
            song_end -= temp
            mix_end -= temp
        temp //= 2

    temp = chunk_size
    while temp >= min_chunk_size:
        # Try to expand backwards
        sim_back = chunk_sim(song_start - temp, mix_start - temp, song_len, mix_len, song_chroma, mix_chroma, temp)
        if sim_back > sim_threshold:
            song_start -= temp
            mix_start -= temp
        # Try to expand forwards
        sim_forward = chunk_sim(song_end, mix_end, song_len, mix_len, song_chroma, mix_chroma, temp)
        if sim_forward > sim_threshold:
            song_end += temp
            mix_end += temp
        temp //= 2

    

    # Clamp to valid range
    song_start = max(0, song_start)
    mix_start = max(0, mix_start)
    song_end = min(song_len, song_end)
    mix_end = min(mix_len, mix_end)
    return song_start, mix_start, song_end, mix_end





def chunk_match(song_chroma, mix_chroma, sr, hop_length=512, chunk_seconds=5, n_chunks=30, buffer_seconds=30, min_chunk_factor=4):
    """
    Use find_whole_song_in_mix for a rough estimate, then run chunk-based matching within a buffer zone around the rough match.
    Returns refined start/end times for both song and mix.
    """
    # Step 1: Rough estimate
    rough_start, _ = find_whole_song_in_mix(song_chroma, mix_chroma, sr, hop_length=hop_length)
    if rough_start is None:
        print("No rough match found, cannot proceed with chunk-based matching.")
        return []
    # Step 2: Convert buffer to frames
    buffer_frames = librosa.time_to_frames(buffer_seconds, sr=sr, hop_length=hop_length)
    rough_start_frame = librosa.time_to_frames(rough_start, sr=sr, hop_length=hop_length)
    # Step 3: Limit mix chroma to buffer zone
    mix_start = max(0, rough_start_frame - buffer_frames)
    mix_end = min(mix_chroma.shape[1], rough_start_frame + buffer_frames + song_chroma.shape[1])
    mix_chroma_buffer = mix_chroma[:, mix_start:mix_end]
    # Step 4: Run chunk-based matching on this region
    matches = find_isometric_chunk_matches(song_chroma, mix_chroma_buffer, sr, hop_length=hop_length, chunk_seconds=chunk_seconds, n_chunks=n_chunks)
    # Adjust mix indices to global frame indices
    adjusted_matches = []
    for (i, chunk_start, best_mix_start, best_match_score) in matches:
        adjusted_matches.append((i, chunk_start, best_mix_start + mix_start, best_match_score))

    # Step 5: Find largest isometry block
    chunk_size = librosa.time_to_frames(chunk_seconds, sr=sr, hop_length=hop_length)
    anchor_song_start, anchor_mix_start, best_indices = find_largest_isometry(adjusted_matches, chunk_size)
    if not best_indices:
        print("No isometric block found.")
        return None, None, None, None
    # Get first and last chunk in the isometry block
    sorted_indices = sorted(best_indices)
    # Ensure strictly increasing order for contiguous block
    sorted_indices = sorted(sorted_indices, key=lambda idx: (adjusted_matches[idx][1], adjusted_matches[idx][2]))
    first = adjusted_matches[sorted_indices[0]]
    last = adjusted_matches[sorted_indices[-1]]
    first_song_start, first_mix_start = first[1], first[2]
    last_song_start, last_mix_start = last[1], last[2]

    # Step 6: Expand before/after the block
    refined_song_start, refined_mix_start, refined_song_end, refined_mix_end = expand_isometry(
        song_chroma, mix_chroma, first_song_start, first_mix_start, last_song_start, last_mix_start, chunk_size)


    # Step 6.5: Print partial results
    print(f"Partial refined match: Song Start: {librosa.frames_to_time(refined_song_start, sr=sr, hop_length=hop_length)}, Song End: {librosa.frames_to_time(refined_song_end, sr=sr, hop_length=hop_length)}")
    print(f"    Mix Start: {librosa.frames_to_time(refined_mix_start, sr=sr, hop_length=hop_length)}, Mix End: {librosa.frames_to_time(refined_mix_end, sr=sr, hop_length=hop_length)}")

    # Step 7: Refine the outer chunks with smaller and smaller chunks
    refined_song_start, refined_mix_start, refined_song_end, refined_mix_end = refine_outer_chunks(
        song_chroma, mix_chroma, refined_song_start, refined_mix_start, refined_song_end, refined_mix_end,
        sr, hop_length=hop_length, initial_chunk_size=chunk_size, min_chunk_factor=min_chunk_factor
    )

    # Convert to seconds
    song_start_sec = librosa.frames_to_time(refined_song_start, sr=sr, hop_length=hop_length)
    song_end_sec = librosa.frames_to_time(refined_song_end, sr=sr, hop_length=hop_length)
    mix_start_sec = librosa.frames_to_time(refined_mix_start, sr=sr, hop_length=hop_length)
    mix_end_sec = librosa.frames_to_time(refined_mix_end, sr=sr, hop_length=hop_length)

    return song_start_sec, song_end_sec, mix_start_sec, mix_end_sec


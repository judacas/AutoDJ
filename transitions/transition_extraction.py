

# **Local** extraction: slice the mix around the boundary.
#- **Preemptive crossfades**:
#  - Fade-in from the original **previous** track into the mix snippet.
#  - Fade-out from the snippet into the original **next** track.
#- Save transition chunks to Blob; store metadata in DB.
# MVP: local slcie 

# INput: transition bounds time from step 6: detection phase
#prev_track_path (original Song A file)
#	•	mix_path (the DJ mix file that contains A→B)
#	•	next_track_path (original Song B file)

# Output: mp3 of transition clip
# uplaods to azure blob storage?
# create metadata json

#improt 
import subprocess, shlex
from pathlib import Path
OUT_DIR = Path("out/transitions")
OUT_DIR.mkdir(parents=True, exist_ok=True)

#shell runner 
def run(cmd: str):
    """Run a shell command and raise an error if it fails."""
    print("→", cmd)
    subprocess.run(shlex.split(cmd), check=True)

def duration(path: str) -> float:
    """Return audio duration in seconds using ffprobe."""
    out = subprocess.check_output([
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        path
    ])
    return float(out.strip())

# extract transition fn (slice and crossfade)
def extract_segments(prev_path, mix_path, next_path, boundary_s, pre_tail=1.0, mix_before=0.5, mix_after=0.5, post_head=1.0):
    # trasntions "window"
    # pre tail: how much of prev track tail to grab
    # mix before: how many s before transition to start cut
    # mix after: how far adter transition to include
    # post head: how much of next head to grab
    """
    Writes 3 WAVs:
    - prev_tail.wav (last bit of previous song)
    - mix_mid.wav   (region around the transition)
    - next_head.wav (first bit of next song)
    """
    p_tail = OUT_DIR / "prev_tail.wav"
    m_mid  = OUT_DIR / "mix_mid.wav"
    n_head = OUT_DIR / "next_head.wav"

    # prev track tail
    dur_prev = duration(prev_path)
    start_prev = max(0.0, dur_prev - pre_tail)
    # -ss tells ffmpeg where to begin,
    # -t tells it how long to cut
    # -ac 2 -ar 44100 consistent format
    run(f'ffmpeg -y -ss {start_prev} -t {pre_tail} -i "{prev_path}" -ac 2 -ar 44100 -vn "{p_tail}"')

    # middle part of mix around bounds
    start_mix = max(0.0, boundary_s - mix_before)
    length_mix = mix_before + mix_after
    run(f'ffmpeg -y -ss {start_mix} -t {length_mix} -i "{mix_path}" -ac 2 -ar 44100 -vn "{m_mid}"')

    # next track head
    run(f'ffmpeg -y -ss 0 -t {post_head} -i "{next_path}" -ac 2 -ar 44100 -vn "{n_head}"')

    return p_tail, m_mid, n_head

# Helper fn to deal with small or diff size audios
def safe_crossfade_duration(a_path: Path, b_path: Path, desired_cross: float) -> float:
    """
    Returns a safe crossfade duration that won't exceed the length
    of either audio file.
    """
    len_a = duration(str(a_path))
    len_b = duration(str(b_path))

    # pick the shortest file’s length * 0.8 to stay safe
    max_possible = min(len_a, len_b) * 0.8
    if desired_cross > max_possible:
        print(f"⚠️ Crossfade {desired_cross:.2f}s too long for clip pair "
              f"({len_a:.2f}s, {len_b:.2f}s). Using {max_possible:.2f}s instead.")
        return max_possible
    return desired_cross

# crossfade fn
def crossfade(a_path: Path, b_path: Path, out_path: Path, cross=0.3):
    # Crossfade two audio clips (A → B) 
    # cross = fade duration (s)
    # used across fade filter
    # Use helper to determine best crossfade
    cross = safe_crossfade_duration(a_path, b_path, cross)
    run(
        f'ffmpeg -y -i "{a_path}" -i "{b_path}" '
        f'-filter_complex "[0:a][1:a]acrossfade=d={cross}:curve1=tri:curve2=tri" '
        f'-ar 44100 -ac 2 "{out_path}"'
    )

# helper crossfades prev_plus_mix and next_head
# final - saves as mp3 instead of wav file
def stitch_to_final(step1: Path, next_head: Path, mp3_out: Path, cross=0.3):
    # cross prev mix to next track head
    # save as mp3
    # -c:a libmp3lame = encode as MP3
    # -b:a 192k = use 192 kbps bitrate (good quality, small file size)
    cross = safe_crossfade_duration(step1, next_head, cross)
    run(
        f'ffmpeg -y -i "{step1}" -i "{next_head}" '
        f'-filter_complex "[0:a][1:a]acrossfade=d={cross}:curve1=tri:curve2=tri" '
        f'-c:a libmp3lame -b:a 192k "{mp3_out}"'
    )
# testing!!
def main():
    boundary = 1.0  # pretend transition time (s)

    # Extract your three clips
    p_tail, m_mid, n_head = extract_segments(
        "audio/test/prev.mp3",
        "audio/test/mix.mp3",
        "audio/test/next.mp3",
        boundary_s=boundary,
        pre_tail=1.0,
        mix_before=0.5,
        mix_after=0.5,
        post_head=1.0
    )

    # 1️⃣ Crossfade prev → mix
    step1 = OUT_DIR / "prev_plus_mix.wav"
    crossfade(p_tail, m_mid, step1, cross=0.3)

    # 2️⃣ Crossfade (prev+mix) → next
    final_mp3 = OUT_DIR / "transition_demo.mp3"
    stitch_to_final(step1, n_head, final_mp3, cross=0.3)

    print("🎧 Final transition saved as:", final_mp3)

if __name__ == "__main__":
    main()



# upload to azure fn

# create transition metadata


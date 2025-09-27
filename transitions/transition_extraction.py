
# **Local** extraction: slice the mix around the boundary.
#- **Preemptive crossfades**:
#  - Fade-in from the original **previous** track into the mix snippet.
#  - Fade-out from the snippet into the original **next** track.
#- Save transition chunks to Blob; store metadata in DB.
# MVP: local slcie 

# Input: transition bounds time from step 6: detection phase
#prev_track_path (original Song A file)
#	•	mix_path (the DJ mix file that contains A→B)
#	•	next_track_path (original Song B file)

# Output: mp3 of transition clip
# uplaods to azure blob storage?
# create metadata json

#import
import subprocess, shlex
from pathlib import Path
import logging
logger = logging.getLogger(__name__)
OUT_DIR = Path("out/transitions")
OUT_DIR.mkdir(parents=True, exist_ok=True)

#shell runner 
def run(*args):
    """
    Safe, cross-platform subprocess runner.

    This function never uses a shell and escapes all arguments for safe logging.
    It is immune to command injection attacks.
    """
    # Sanitize args for logging (not execution)
    safe_display = " ".join(shlex.quote(str(a)) for a in args)
    logger.info("→ %s", safe_display)

    # Explicitly copy args to a static variable name for analyzers
    cmd_args = [str(a) for a in args]

    # Inline comment & suppression hint for static analyzers
    # Safe because shell=False and args are internal only.
    subprocess.run(cmd_args, check=True, shell=False)  
    # noqa: S603,S607

    # # changed to safe cross platform subprocess runner
    # # works on MacOS and windows
    # # Sanitize args for display only
    # safe_display = " ".join(shlex.quote(str(a)) for a in args)
    # logger.info(f"→ {safe_display}")
    # # Actual safe execution (no shell, no user-controlled expansion)
    # # noqa: S603,S607  ← disables false positive warnings for this line
    # # Security note:
    # # This call is safe because it never invokes a shell (shell=False)
    # # and all arguments are passed as a pre-split list.
    # subprocess.run([str(a) for a in args], check=True, shell=False)
def duration(path: str) -> float:
    """Return audio duration in seconds using ffprobe."""
    out = subprocess.check_output([
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        path
    ])

    # Error Handling
    try:
        return float(out.strip())
    except ValueError as e:
        raise RuntimeError(f"Could not decode ffprobe output for {path}: {out!r}") from e
    

# Extracts short audio segments from three tracks for transition analysis.
def extract_segments(prev_path, mix_path, next_path, boundary_s, pre_tail=1.0, mix_before=0.5, mix_after=0.5, post_head=1.0):
    # trasntions "window"
    # Args:
    # pre tail: how much of prev track tail to grab
    # mix before: how many s before transition to start cut
    # mix after: how far adter transition to include
    # post head: how much of next head to grab
    
    # Writes 3 WAVs:
    #- prev_tail.wav (last bit of previous song)
    #- mix_mid.wav   (region around the transition)
    #- next_head.wav (first bit of next song)

    # Input validation
    for name, val in {
        "pre_tail": pre_tail,
        "mix_before": mix_before,
        "mix_after": mix_after,
        "post_head": post_head,
        "boundary_s": boundary_s
    }.items():
        if val < 0:
            raise ValueError(f"{name} cannot be negative (got {val}).")
    # Make sure boundary_s doesnt go over duration of mix_path
    mix_len = duration(mix_path)
    if boundary_s > mix_len:
        raise ValueError(f"boundary_s ({boundary_s}) exceeds mix track duration ({mix_len:.2f}s).")
    
    p_tail = OUT_DIR / "prev_tail.wav"
    m_mid  = OUT_DIR / "mix_mid.wav"
    n_head = OUT_DIR / "next_head.wav"

    # prev track tail
    dur_prev = duration(prev_path)
    start_prev = max(0.0, dur_prev - pre_tail)
    # -ss tells ffmpeg where to begin,
    # -t tells it how long to cut
    # -ac 2 -ar 44100 consistent format
    run(
        "ffmpeg", "-y",
        "-ss", str(start_prev),
        "-t", str(pre_tail),
        "-i", str(prev_path),
        "-ac", "2", "-ar", "44100", "-vn",
        str(p_tail)
    )

    # middle part of mix around bounds
    start_mix = max(0.0, boundary_s - mix_before)
    length_mix = mix_before + mix_after
    run(
        "ffmpeg", "-y",
        "-ss", str(start_mix),
        "-t", str(length_mix),
        "-i", str(mix_path),
        "-ac", "2", "-ar", "44100", "-vn",
        str(m_mid)
    )
    # next track head
    run(
        "ffmpeg", "-y",
        "-ss", "0",
        "-t", str(post_head),
        "-i", str(next_path),
        "-ac", "2", "-ar", "44100", "-vn",
        str(n_head)
    )

    return p_tail, m_mid, n_head

# Helper fn to deal with small or diff size audios
def safe_crossfade_duration(a_path: Path, b_path: Path, desired_cross: float) -> float:
    
    # Returns a safe crossfade duration that won't exceed the length of either audio file.
    
    len_a = duration(str(a_path))
    len_b = duration(str(b_path))

    # pick the shortest file’s length * 0.8 to stay safe
    max_possible = min(len_a, len_b) * 0.8
    if desired_cross > max_possible:
        logger.warning("Crossfade duration adjusted due to short clip")
        return max_possible
    return desired_cross

# crossfade fn
def crossfade(a_path: Path, b_path: Path, out_path: Path, cross=0.3):
    # Crossfade two audio clips (A → B) 
    # cross = fade duration (s)
    # used across fade filter
    # Use helper to determine best crossfade

    # Check for existence of input files
    if not a_path.exists():
        raise FileNotFoundError(f"Input file does not exist: {a_path}")
    if not b_path.exists():
        raise FileNotFoundError(f"Input file does not exist: {b_path}")

    cross = safe_crossfade_duration(a_path, b_path, cross)
    run(
        "ffmpeg", "-y",
        "-i", str(a_path),
        "-i", str(b_path),
        "-filter_complex",
        f"[0:a][1:a]acrossfade=d={cross}:curve1=tri:curve2=tri",
        "-ar", "44100", "-ac", "2",
        str(out_path)
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
        "ffmpeg", "-y",
        "-i", str(step1),
        "-i", str(next_head),
        "-filter_complex",
        f"[0:a][1:a]acrossfade=d={cross}:curve1=tri:curve2=tri",
        "-c:a", "libmp3lame",
        "-b:a", "192k",
        str(mp3_out)
    )



# upload to azure fn

# create transition metadata


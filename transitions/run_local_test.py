from transitions.transition_extraction import extract_segments, crossfade, stitch_to_final, OUT_DIR

def main():
    boundary = 1.0
    p_tail, m_mid, n_head = extract_segments(
        "audio/test/prev.mp3",
        "audio/test/mix.mp3",
        "audio/test/next.mp3",
        boundary_s=boundary
    )

    step1 = OUT_DIR / "prev_plus_mix.wav"
    crossfade(p_tail, m_mid, step1, cross=0.3)
    final_mp3 = OUT_DIR / "transition_demo.mp3"
    stitch_to_final(step1, n_head, final_mp3, cross=0.3)

if __name__ == "__main__":
    main()
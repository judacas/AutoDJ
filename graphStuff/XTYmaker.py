import pydantic
import random
from XTpair import XT_PAIR
from XTYpair import XTY_PAIR
from typing import List, Dict

def group_xt_by_mix(xt_pairs: List[XT_PAIR]) -> Dict[str, List[XT_PAIR]]:
    """
    Groups XT_PAIRs by mix_song_path.
    """
    mix_dict = {}
    for xt in xt_pairs:
        key = xt.mix_song_path
        mix_dict.setdefault(key, []).append(xt)
    return mix_dict

def find_xty_pairs_from_mix_groups(xt_pairs: List[XT_PAIR], tol: float = 45) -> List[XTY_PAIR]:
    """
    Finds all XTY_PAIRs by grouping XT_PAIRs by mix_song_path and pairing all (X, Y) 
    where X.cross_out ≈ Y.cross_in within the same mix.
    """
    mix_dict = group_xt_by_mix(xt_pairs)
    xty_pairs = []
    for mix, xt_list in mix_dict.items():
        for x in xt_list:
            for y in xt_list:
                if x.source_song_path != y.source_song_path and 5 < y.cross_in - x.cross_out < tol:
                    xty = XTY_PAIR(
                        X_song_path=x.source_song_path,
                        Y_song_path=y.source_song_path,
                        mix_song_path=x.mix_song_path,
                        Xoffset=x.offset,
                        Yoffset=y.offset,
                        Xcross_out=x.cross_out,
                        Ycross_in=y.cross_in,
                    )
                    xty_pairs.append(xty)
    return xty_pairs



"""
if __name__ == "__main__":
    # Create 6 random XT_PAIRs, all with the same mix song
    mix_song = "mix_song_1.mp3"
    xt_pairs = []
    cross_in = 0
    for i in range(6):
        cross_out = cross_in + random.uniform(10, 20)
        pair = XT_PAIR(
            source_song_path=f"source_song_{i}.mp3",
            mix_song_path=mix_song,
            offset=round(random.uniform(-5, 5), 2),
            cross_in=round(cross_in, 2),
            cross_out=round(cross_out, 2),
        )
        xt_pairs.append(pair)
        cross_in = cross_out + random.uniform(10, 20)

    print("XT pairs:")
    for p in xt_pairs:
        print(p)

    xty_pairs = find_xty_pairs_from_mix_groups(xt_pairs)
    print("\nXTY pairs:")
    for p in xty_pairs:
        print(p)
"""
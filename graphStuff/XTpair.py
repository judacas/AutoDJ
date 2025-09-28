import random
from pydantic import BaseModel


class XT_PAIR(BaseModel):
    source_song_path: str
    mix_song_path: str
    offset: float
    cross_in: float
    cross_out: float

    def _str_(self) -> str:
        """
        Returns a two-line string representation of this XT_PAIR.
        First line: source and mix song paths.
        Second line: offset, cross_in, cross_out.
        """
        line1 = f"Source: {self.source_song_path} | Mix: {self.mix_song_path}"
        line2 = (
            f"Offset: {self.offset} | Cross In: {self.cross_in} | Cross Out: {self.cross_out}"
        )
        return f"{line1}\n{line2}"




"""
pairs = []
for i in range(5):
    cross_in = round(random.uniform(0, 100), 2)
    cross_out = round(random.uniform(cross_in + 0.01, cross_in + 20), 2)
    pair = XT_PAIR(
        source_song_path=f"source_song_{i}.mp3",
        mix_song_path=f"mix_song_{i}.mp3",
        offset=round(random.uniform(-5, 5), 2),
        cross_in=cross_in,
        cross_out=cross_out,
    )
    pairs.append(pair)

for p in pairs:
    print("--------------------------------")
    print(p.offset)
"""
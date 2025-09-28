from pydantic import BaseModel


class XTY_PAIR(BaseModel):
    X_song_path: str
    Y_song_path: str
    mix_song_path: str
    Xoffset: float
    Yoffset: float
    Xcross_out: float
    Ycross_in: float

    def _str_(self) -> str:
        """
        Returns a two-line string representation of this XT_PAIR.
        First line: source and mix song paths.
        Second line: offset, cross_in, cross_out.
        """
        line1 = f"X: {self.X_song_path} | Y: {self.Y_song_path} | Mix: {self.mix_song_path}"
        line2 = (
            f"X Offset: {self.Xoffset} | Y Offset: {self.Yoffset} | X Cross Out: {self.Xcross_out} | Y Cross In: {self.Ycross_in}"
        )
        return f"{line1}\n{line2}"



# lorem
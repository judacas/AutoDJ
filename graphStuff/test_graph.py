# Just used to test graph.py

from graph import DirectedSongGraph
from XTYpair import XTY_PAIR
from XTpair import XT_PAIR


# No longer works
"""
def test_graph():
    graph = DirectedSongGraph()
    # Add songs
    graph.add_song('song1', {'title': 'Song One'})
    graph.add_song('song2', {'title': 'Song Two'})
    graph.add_song('song3', {'title': 'Song Three'})

    # Add transitions (using time objects for duration, sourceEnd, targetStart)
    from datetime import time
    graph.add_transition('song1', 'song2', 10, 100, 40, '1 to 2', 0.9)
    graph.add_transition('song1', 'song3', 15, 180, 120, '1 to 3', 0.8)
    graph.add_transition('song2', 'song3', 20, 120, 105, '2 to 3', 0.95)

    # Test get_neighbors
    neighbors1 = graph.get_neighbors('song1')
    print('Neighbors of song1:', [n.song_id for n in neighbors1])

    # Test get_out_edges
    out_edges1 = graph.get_out_edges('song1')
    print('Out edges of song1:')
    for edge in out_edges1:
        print(f"  {edge.source} -> {edge.target} | duration: {edge.duration}, sourceEnd: {edge.sourceEnd}, targetStart: {edge.targetStart} (mix: {edge.mix_id}, conf: {edge.confidence})")

    # Test get_song
    song2 = graph.get_song('song2')
    print('Song2 metadata:', song2.metadata if song2 else None)

    # Test get_neighbors for song2
    neighbors2 = graph.get_neighbors('song2')
    print('Neighbors of song2:', [n.song_id for n in neighbors2])
"""



def make_dummy_xt_pairs():
    # Create a chain: songA -> songB -> songC -> songD

    xt1 = XT_PAIR(
        source_song_path="songA.mp3",
        mix_song_path="mix1.mp3",
        offset=0.0,
        cross_in=0.0,      # Start of songA in mix
        cross_out=20.0     # End of songA's segment (transition out)
    )
    xt2 = XT_PAIR(
        source_song_path="songB.mp3",
        mix_song_path="mix1.mp3",
        offset=10.0,
        cross_in=30.0,     # Start of songB in mix (transition in)
        cross_out=50.0     # End of songB's segment (transition out)
    )
    xt3 = XT_PAIR(
        source_song_path="songC.mp3",
        mix_song_path="mix1.mp3",
        offset=20.0,
        cross_in=60.0,     # Start of songC in mix (transition in)
        cross_out=70.0     # End of songC's segment (transition out)
    )
    xt4 = XT_PAIR(
        source_song_path="songD.mp3",
        mix_song_path="mix1.mp3",
        offset=30.0,
        cross_in=80.0,     # Start of songD in mix (transition in)
        cross_out=80.0     # End of songD's segment (unknown, so set to cross_in)
    )

    xt_pairs = [xt1, xt2, xt3, xt4]
    return xt_pairs

def main():
    graph = DirectedSongGraph()
    xt_pairs = make_dummy_xt_pairs()
    # Add transitions to the graph
    graph.make_edges(xt_pairs)

    # Try to build a path from songA.mp3 to songD.mp3
    path = graph.get_ATB_pairs()

    print("XTY pairs: ")
    for p in path:
        print(p)
        print("   ")

if __name__ == "__main__":
    main()

"""
if __name__ == '__main__':
    test_graph()
"""
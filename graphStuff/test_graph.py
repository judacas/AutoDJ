# Just used to test graph.py

from datetime import datetime
from graph import DirectedSongGraph

def test_graph():
    graph = DirectedSongGraph()
    # Add songs
    graph.add_song('song1', {'title': 'Song One'})
    graph.add_song('song2', {'title': 'Song Two'})
    graph.add_song('song3', {'title': 'Song Three'})

    # Add transitions (using time objects for duration, sourceEnd, targetStart)
    from datetime import time
    graph.add_transition('song1', 'song2', time(0, 0, 10), time(0, 2, 50), time(0, 0, 40), '1 to 2', 0.9)
    graph.add_transition('song1', 'song3', time(0, 0, 15), time(0, 3, 0), time(0, 2, 0), '1 to 3', 0.8)
    graph.add_transition('song2', 'song3', time(0, 0, 20), time(0, 2, 0), time(0, 1, 45), '2 to 3', 0.95)

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

if __name__ == '__main__':
    test_graph()

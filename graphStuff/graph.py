# 0 integration with the actual database whenever thats made
# AI will actually coordinate with the DB

# CURRENT STATE: Tested, works so far

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from XTpair import XT_PAIR
from XTYpair import XTY_PAIR
from XTYmaker import find_xty_pairs_from_mix_groups

@dataclass
class SongNode:
    song_id: str
    metadata: dict = field(default_factory=dict)

@dataclass
class TransitionEdge:
    source: str  # song_id
    target: str  # song_id
    sourceEnd : float
    targetStart : float
    mix_id: str
    xty: XTY_PAIR
    extra: dict = field(default_factory=dict)

class DirectedSongGraph:
    def __init__(self):
        self.nodes: Dict[str, SongNode] = {}
        self.edges: Dict[str, List[TransitionEdge]] = {}  # source song_id -> list of edges

    def add_song(self, song_id: str, metadata: Optional[dict] = None):
        if song_id not in self.nodes:
            self.nodes[song_id] = SongNode(song_id, metadata or {})

    def add_transition(self, source: str, target: str, sourceEnd: float, targetStart: float, mix_id: str, xty: XTY_PAIR, extra: Optional[dict] = None):
        edge = TransitionEdge(source, target, sourceEnd, targetStart, mix_id, xty, extra or {})
        if source not in self.edges:
            self.edges[source] = []
        self.edges[source].append(edge)
        # Ensure both nodes exist
        self.add_song(source)
        self.add_song(target)

    def get_neighbors(self, song_id: str) -> List[SongNode]:
        """Return SongNode objects that are direct targets from this song."""
        return [self.nodes[edge.target] for edge in self.edges.get(song_id, [])]

    def get_out_edges(self, song_id: str) -> List[TransitionEdge]:
        """Return all outgoing TransitionEdge objects from this song."""
        return self.edges.get(song_id, [])

    def get_song(self, song_id: str) -> Optional[SongNode]:
        return self.nodes.get(song_id)

    def get_decent_path(self) -> List[str]:
        return beam_search(self, k=5)

    # THIS IS THE IMPORTANT FUNCTION
    def get_ATB_pairs(self, XTpairs: [XT_PAIR]) -> List[XTY_PAIR]:
        self.make_edges(XTpairs)
        return self.get_ATB_pairs_partial()

    def get_ATB_pairs_partial(self) -> List[XTY_PAIR]:
        edges = self.get_decent_path()
        pairs = []
        for edge in edges:
            pairs.append(edge.xty)
        return pairs

    def make_edges(self, XTpairs: [XT_PAIR], crossfade_length: float = 5):
        XTYpairs = find_xty_pairs_from_mix_groups(XTpairs)
        for pair in XTYpairs:
            self.add_transition(
                source=pair.X_song_path,
                target=pair.Y_song_path,
                sourceEnd=pair.Xcross_out + crossfade_length,
                targetStart=pair.Ycross_in,
                mix_id=pair.mix_song_path,
                xty=pair,
                extra={}
            )



def beam_search(graph, k):
    # k=1 gives greedy, k=inf gives brute force
	
	best_path = []
	for start_id in graph.nodes:
		# Each element in the beam is (path_so_far, visited_set)
		beam = [([start_id], set([start_id]))]
		while beam:
			new_beam = []
			for path, visited in beam:
				last = path[-1]
				neighbors = graph.get_neighbors(last)
				extended = False
				for neighbor in neighbors:
					if neighbor.song_id not in visited:
						new_path = path + [neighbor.song_id]
						new_visited = visited | {neighbor.song_id}
						# Heuristic: remaining outdegree (number of unused outgoing edges from neighbor)
						remaining_outdegree = len([e for e in graph.get_out_edges(neighbor.song_id) if e.target not in new_visited])
						new_beam.append((new_path, new_visited, remaining_outdegree))
						extended = True
				if not extended:
					# No extension possible, consider for best
					if len(path) > len(best_path):
						best_path = path
			# Keep only top-k paths with highest remaining outdegree at the end
			new_beam.sort(key=lambda x: x[2], reverse=True)
			# Remove the heuristic value for the next round
			beam = [(p, v) for (p, v, h) in new_beam[:k]]
	return songs_to_edges(graph, best_path)

def songs_to_edges(
	
	graph: DirectedSongGraph,
	song_path: List[str],
	edge_selector: str = None
) -> List[object]:
	"""
	Given a path of song_ids, select edges between each pair using edge_selector.
	edge_selector: function that takes a list of candidate edges and returns the chosen edge.
	If not provided, defaults to maximizing previous song's play time (sourceEnd).
	"""
	edges = []
	prev_target_start = None
	for i in range(len(song_path) - 1):
		source = song_path[i]
		target = song_path[i + 1]
		out_edges = [e for e in graph.get_out_edges(source) if e.target == target]

		# Filter out edges that would overlap with the previous transition
		if prev_target_start is not None:
			out_edges = [e for e in out_edges if e.sourceEnd >= prev_target_start]

		if not out_edges:
			raise ValueError(f"No valid non-overlapping edge found from {source} to {target}")

		# Use custom edge selector if provided
		if edge_selector is not None:
			edge = edge_selector(out_edges)
			if edge is None:
				raise ValueError(f"Edge selector did not return an edge for {source} to {target}")
		else:
			# Default: maximize previous song's play time (sourceEnd)
			edge = max(out_edges, key=lambda e: e.sourceEnd)

		edges.append(edge)
		prev_target_start = edge.targetStart

	return edges



# Example usage (to be removed or adapted when connecting to DB):
# graph = DirectedSongGraph()
# graph.add_song('song1', {'title': 'Song One'})
# graph.add_song('song2', {'title': 'Song Two'})
# graph.add_transition('song1', 'song2', 0, 'mix123', 0.95)
# neighbors = graph.get_neighbors('song1')
# out_edges = graph.get_out_edges('song1')

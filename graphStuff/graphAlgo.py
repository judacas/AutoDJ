# Brute force and beam search algos

from graph import DirectedSongGraph, SongNode
from typing import Callable, List, Optional

def bf(graph: DirectedSongGraph):
	return beam_search(graph, k=9999)

#ts is so peak
def beam_search(graph, k):
	"""
	Beam search for a long path in the graph.
	k: beam width (number of partial paths to keep at each step)
	Returns the longest path found (list of song_ids).
    k=1 gives greedy, k=inf gives brute force
	"""
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
	edge_selector: Optional[Callable[[List], Optional[object]]] = None
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


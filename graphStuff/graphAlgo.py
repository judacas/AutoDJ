
from graph import DirectedSongGraph, SongNode

def bf_fixed_start(graph: DirectedSongGraph, start_id: str):
	"""
	Finds the longest path (by number of nodes) from start_id without repeating any vertices.
	Returns the list of song_ids in the longest path.
	"""
	def dfs(current_id, visited):
		visited.add(current_id)
		max_path = [current_id]
		for neighbor in graph.get_neighbors(current_id):
			if neighbor.song_id not in visited:
				path = dfs(neighbor.song_id, visited.copy())
				if len(path) + 1 > len(max_path):
					max_path = [current_id] + path
		return max_path

	return dfs(start_id, set())

def bf_any_start(graph: DirectedSongGraph):
	"""
	Finds the longest path (by number of nodes) from any starting node without repeating any vertices.
	Returns the list of song_ids in the longest path.
	"""
	longest_path = []
	for song_id in graph.nodes.keys():
		path = bf_fixed_start(graph, song_id)
		if len(path) > len(longest_path):
			longest_path = path
	return longest_path

#ts is so peak
def beam_search_longest_path(graph, k):
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
						new_beam.append((new_path, new_visited))
						extended = True
				if not extended:
					# No extension possible, consider for best
					if len(path) > len(best_path):
						best_path = path
			# Keep only top-k longest paths in the beam
			new_beam.sort(key=lambda x: len(x[0]), reverse=True)
			beam = new_beam[:k]
	return best_path
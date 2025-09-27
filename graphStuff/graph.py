# 0 integration with the actual database whenever thats made
# AI will actually coordinate with the DB

# CURRENT STATE: Good enough for a while as of 11pm 9/26

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class SongNode:
    song_id: str
    metadata: dict = field(default_factory=dict)


@dataclass
class TransitionEdge:
    source: str  # song_id
    target: str  # song_id
    timestamp: datetime
    mix_id: str
    confidence: float
    extra: dict = field(default_factory=dict)


class DirectedSongGraph:
    def __init__(self):
        self.nodes: Dict[str, SongNode] = {}
        self.edges: Dict[
            str, List[TransitionEdge]
        ] = {}  # source song_id -> list of edges

    def add_song(self, song_id: str, metadata: Optional[dict] = None):
        if song_id not in self.nodes:
            self.nodes[song_id] = SongNode(song_id, metadata or {})

    def add_transition(
        self,
        source: str,
        target: str,
        timestamp: datetime,
        mix_id: str,
        confidence: float,
        extra: Optional[dict] = None,
    ):
        edge = TransitionEdge(
            source, target, timestamp, mix_id, confidence, extra or {}
        )
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


# Example usage (to be removed or adapted when connecting to DB):
# graph = DirectedSongGraph()
# graph.add_song('song1', {'title': 'Song One'})
# graph.add_song('song2', {'title': 'Song Two'})
# graph.add_transition('song1', 'song2', datetime.now(), 'mix123', 0.95)
# neighbors = graph.get_neighbors('song1')
# out_edges = graph.get_out_edges('song1')

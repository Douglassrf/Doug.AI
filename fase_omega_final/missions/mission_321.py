# ============================================================
# MISSÃO 321 — AI DIGITAL GENOME
# Fase Ômega Final — Doug.AI v1.0
# ============================================================

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass
class GenomeNode:
    """Nó do genoma."""

    id: str = field(default_factory=lambda: f"gn_{uuid.uuid4().hex[:12]}")
    type: str = ""
    name: str = ""
    parent_id: Optional[str] = None
    children: List[str] = field(default_factory=list)
    dna: Dict[str, Any] = field(default_factory=dict)
    mutation_history: List[Dict[str, Any]] = field(default_factory=list)
    version: str = "1.0.0"
    fitness: float = 0.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "name": self.name,
            "parent_id": self.parent_id,
            "children": self.children,
            "dna": self.dna,
            "mutation_history": self.mutation_history[-10:],
            "version": self.version,
            "fitness": self.fitness,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
        }


class AIDigitalGenome:
    """
    Genoma digital do Doug.AI.

    Implementa registry, evolution tree, mutation e busca.
    """

    def __init__(self):
        self._nodes: Dict[str, GenomeNode] = {}
        self._root_id: Optional[str] = None
        self._type_index: Dict[str, List[str]] = {}

    def create_genome(
        self,
        name: str,
        genome_type: str,
        dna: Dict[str, Any],
        parent_id: Optional[str] = None,
        fitness: float = 0.0,
    ) -> GenomeNode:
        """Cria novo nó genoma."""
        node = GenomeNode(
            type=genome_type,
            name=name,
            parent_id=parent_id,
            dna=dna,
            fitness=fitness,
        )

        self._nodes[node.id] = node

        if genome_type not in self._type_index:
            self._type_index[genome_type] = []
        self._type_index[genome_type].append(node.id)

        if parent_id and parent_id in self._nodes:
            self._nodes[parent_id].children.append(node.id)

        if not self._root_id:
            self._root_id = node.id

        if parent_id:
            node.mutation_history.append(
                {
                    "parent_id": parent_id,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "type": "creation",
                }
            )

        return node

    def mutate(
        self,
        node_id: str,
        mutation: Dict[str, Any],
        mutation_type: str = "modification",
    ) -> GenomeNode:
        """Muta um nó existente."""
        node = self._nodes.get(node_id)
        if not node:
            raise ValueError(f"Node {node_id} not found")

        new_dna = node.dna.copy()
        new_dna.update(mutation)
        new_fitness = min(node.fitness + 0.1, 1.0)

        child = self.create_genome(
            name=f"{node.name}_M{len(node.mutation_history) + 1}",
            genome_type=node.type,
            dna=new_dna,
            parent_id=node_id,
            fitness=new_fitness,
        )

        child.mutation_history = node.mutation_history + [
            {
                "type": mutation_type,
                "changes": mutation,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        ]
        return child

    def get_evolution_path(self, node_id: str) -> List[str]:
        """Retorna caminho evolutivo."""
        path: List[str] = []
        current: Optional[str] = node_id

        while current:
            path.append(current)
            node = self._nodes.get(current)
            if not node or not node.parent_id:
                break
            current = node.parent_id

        return path[::-1]

    def get_evolution_tree(self, node_id: str) -> Dict[str, Any]:
        """Retorna árvore evolutiva."""
        node = self._nodes.get(node_id)
        if not node:
            return {}

        return {
            node.id: {
                "name": node.name,
                "type": node.type,
                "fitness": node.fitness,
                "children": {
                    child_id: self.get_evolution_tree(child_id)
                    for child_id in node.children
                    if child_id in self._nodes
                },
            }
        }

    def search_genome(self, query: str) -> List[GenomeNode]:
        """Busca no genoma."""
        results: List[tuple[GenomeNode, float]] = []
        query_lower = query.lower()

        for node in self._nodes.values():
            score = 0.0

            if query_lower in node.name.lower():
                score += 0.5
            if query_lower in str(node.dna).lower():
                score += 0.3
            if query_lower in node.type.lower():
                score += 0.2

            if score > 0:
                results.append((node, score))

        results.sort(key=lambda item: item[1], reverse=True)
        return [node for node, _ in results[:10]]

    def get_genome_dashboard(self) -> Dict[str, Any]:
        """Retorna dashboard do genoma."""
        total_nodes = len(self._nodes)
        root = self._nodes.get(self._root_id) if self._root_id else None

        return {
            "total_nodes": total_nodes,
            "root_id": self._root_id,
            "root_name": root.name if root else None,
            "type_distribution": {
                node_type: len(ids) for node_type, ids in self._type_index.items()
            },
            "avg_fitness": (
                sum(node.fitness for node in self._nodes.values()) / total_nodes
                if total_nodes > 0
                else 0
            ),
            "avg_depth": self._calculate_avg_depth(),
            "recent_nodes": [node.to_dict() for node in list(self._nodes.values())[-5:]],
        }

    def _calculate_avg_depth(self) -> float:
        """Calcula profundidade média."""
        depths: List[int] = []
        for node in self._nodes.values():
            depth = 0
            current: Optional[str] = node.id
            while current:
                current_node = self._nodes.get(current)
                if not current_node or not current_node.parent_id:
                    break
                depth += 1
                current = current_node.parent_id
            depths.append(depth)

        return sum(depths) / len(depths) if depths else 0

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Literal

from src.maze import Coordinate, Maze


EventKind = Literal["discover", "expand", "path"]


@dataclass(slots=True)
class TraceEvent:
    kind: EventKind
    row: int
    col: int
    frontier_size: int

    def to_dict(self) -> dict[str, int | str]:
        return {
            "kind": self.kind,
            "row": self.row,
            "col": self.col,
            "frontier_size": self.frontier_size,
        }


@dataclass(slots=True)
class SolverMetrics:
    nodes_explored: int
    frontier_peak: int
    path_length: int
    path_cost: int
    runtime_ms: float

    def to_dict(self) -> dict[str, int | float]:
        return {
            "nodes_explored": self.nodes_explored,
            "frontier_peak": self.frontier_peak,
            "path_length": self.path_length,
            "path_cost": self.path_cost,
            "runtime_ms": round(self.runtime_ms, 3),
        }


@dataclass(slots=True)
class SolverStatus:
    found: bool
    guaranteed_optimal: bool
    actual_optimal: bool | None
    optimality_note: str

    def to_dict(self) -> dict[str, bool | str | None]:
        return {
            "found": self.found,
            "guaranteed_optimal": self.guaranteed_optimal,
            "actual_optimal": self.actual_optimal,
            "optimality_note": self.optimality_note,
        }


@dataclass(slots=True)
class SolverResult:
    algorithm: str
    path: list[Coordinate]
    events: list[TraceEvent]
    metrics: SolverMetrics
    status: SolverStatus

    def to_payload(self) -> dict:
        return {
            "algorithm": self.algorithm,
            "path": [list(node) for node in self.path],
            "events": [event.to_dict() for event in self.events],
            "metrics": self.metrics.to_dict(),
            "status": self.status.to_dict(),
            "actual_optimal": self.status.actual_optimal,
            "optimality_note": self.status.optimality_note,
        }


def reconstruct_path(
    parents: dict[Coordinate, Coordinate | None],
    goal: Coordinate,
) -> list[Coordinate]:
    path: list[Coordinate] = []
    node: Coordinate | None = goal
    while node is not None:
        path.append(node)
        node = parents.get(node)
    path.reverse()
    return path


def record_event(
    events: list[TraceEvent],
    kind: EventKind,
    node: Coordinate,
    frontier_size: int,
) -> None:
    row, col = node
    events.append(
        TraceEvent(
            kind=kind,
            row=row,
            col=col,
            frontier_size=frontier_size,
        )
    )


def record_path(events: list[TraceEvent], path: list[Coordinate]) -> None:
    for node in path:
        record_event(events, "path", node, frontier_size=0)


def result_from_search(
    *,
    algorithm: str,
    maze: Maze,
    events: list[TraceEvent],
    parents: dict[Coordinate, Coordinate | None],
    found: bool,
    nodes_explored: int,
    frontier_peak: int,
    runtime_start: float,
    guaranteed_optimal: bool,
    optimality_note: str,
) -> SolverResult:
    runtime_ms = (perf_counter() - runtime_start) * 1000
    path = reconstruct_path(parents, maze.goal) if found else []

    if found:
        record_path(events, path)

    metrics = SolverMetrics(
        nodes_explored=nodes_explored,
        frontier_peak=frontier_peak,
        path_length=max(len(path) - 1, 0),
        path_cost=maze.path_cost(path),
        runtime_ms=runtime_ms,
    )
    status = SolverStatus(
        found=found,
        guaranteed_optimal=guaranteed_optimal,
        actual_optimal=None,
        optimality_note=optimality_note,
    )
    return SolverResult(
        algorithm=algorithm,
        path=path,
        events=events,
        metrics=metrics,
        status=status,
    )

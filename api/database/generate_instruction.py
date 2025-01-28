from typing import List
from database.models import ConnectionDB, StepDB, ModelDB
import networkx as nx


def generate_stepdb(models: List[ModelDB], connections: List[ConnectionDB],
                    max_models_in_step: int = 3,) -> List[StepDB]:
    # Tworzenie grafu skierowanego z modeli i połączeń
    graph = nx.DiGraph()

    for model in models:
        graph.add_node(model.model_id, model=model)

    for conn in connections:
        graph.add_edge(conn.up_id, conn.down_id, connection=conn)

    steps = []
    step_number = 0
    current_models = []
    current_connections = []

    # Stopnie wejściowe wierzchołków
    in_degree = {node: graph.in_degree(node) for node in graph.nodes}
    zero_in_degree = [node for node, degree in in_degree.items()
                      if degree == 0]

    while zero_in_degree:
        current = zero_in_degree.pop(0)
        current_models.append(graph.nodes[current]['model'])

        current_connections.extend([
            conn for conn in connections
            if conn.down_id == current
        ])

        # Aktualizacja grafu
        for neighbor in list(graph.successors(current)):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                zero_in_degree.append(neighbor)

        graph.remove_node(current)

        # Zapisz krok gdy równy max lub nie ma więcej do dodania
        if len(current_models) == max_models_in_step or not zero_in_degree:
            steps.append(StepDB(
                step=step_number,
                models=current_models,
                connections=current_connections
            ))
            step_number += 1
            current_models = []
            current_connections = []

    return steps

from typing import List
from database.models import ConnectionDB, StepDB, ModelDB
import networkx as nx


def generate_stepdb(models: List[ModelDB], connections: List[ConnectionDB],
                    max_models_in_step: int = 3) -> List[StepDB]:
    # Uzupełnienie grafu skierowanego
    graph = nx.DiGraph()

    for model in models:
        graph.add_node(model.model_id, model=model)

    for conn in connections:
        graph.add_edge(conn.up_id, conn.down_id, connection=conn)

    steps = []
    step_number = 0
    current_step = {'models': [], 'connection': []}
    save_step = False  # służy do wymuszenia zapisania kroku

    while graph:
        bottom_models = [node for node in graph.nodes if graph.in_degree(node) == 0]
        if len(bottom_models) == len(graph.nodes):  
            save_step = True 
        for i in range(0, len(bottom_models), max_models_in_step):
            batch_models = bottom_models[i:i + max_models_in_step]

            current_step['connection'].extend(
                [graph.edges[edge]["connection"]
                 for edge in graph.edges 
                 if edge[0] in batch_models or edge[1] in batch_models
                 ]
            )

            current_step['models'].extend(
                [graph.nodes[model_id]["model"] for model_id in batch_models]
            )

            if save_step or len(current_step['models']) >= max_models_in_step:
                filtered_connections = [
                        connection for connection in current_step['connection']
                        if any(connection.down_id == model.model_id for model in current_step['models'])
                    ]

                steps.append(StepDB(
                    step=step_number,
                    models=current_step['models'][:max_models_in_step],
                    connections=filtered_connections
                ))
                step_number += 1
                current_step['models'] = current_step['models'][max_models_in_step:]
                current_step['connection'] = [connection for connection in current_step['connection']
                                              if connection not in filtered_connections]
                save_step = False
            else:
                save_step = True

            #  Usuwanie przetworzonych modeli z grafu
            graph.remove_nodes_from(batch_models)
    return steps

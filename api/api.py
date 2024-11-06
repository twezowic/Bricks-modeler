from pprint import pprint
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import database.mysqldb as mysqldb
import database.mongodb as mongodb
from database.connection import ModelDB, StepDB, find_connected_groups, temp_prepare_steps
import json
import networkx as nx

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


@app.get('/parts')
async def get_thumbnails(filter: str = Query(None)):
    thumbnails = mysqldb.get_filtered_parts(filter) if filter else mysqldb.get_parts_thumbnail()
    result = [{'imageUrl': t[2], 'name': t[0]} for t in thumbnails][:18]
    return result

@app.get('/model/{id}')
async def get_model(id: str):
    result = mongodb.get_model(id)
    if result:
        return json.loads(result)
    else:
        return HTTPException(status_code=404, detail="Model` not found.")


class Scene(BaseModel):
    models: list


@app.post('/connection')
async def get_connections2(models: Scene):
    result = find_connected_groups(models)

    return result


@app.post("/prepare_instruction")
async def prepare_instruction(models: Scene):
    db_models, steps = temp_prepare_steps(models)
    mongodb.temp_add_whole_instruction(steps, db_models)


class InstructionCheck(BaseModel):
    set_id: int
    step: int
    models: list


def _prepare_edges(steps: list[StepDB]):
    edges = []
    for step in steps:
        edges.append((step.up_id, step.down_id))
    return edges

@app.post("/instruction/check")
def compare_instruction_files(instruction_steps: InstructionCheck):
    current_models, current_steps = temp_prepare_steps(instruction_steps.models)
    instruction_models, instruction_steps = mongodb.get_current_steps(instruction_steps.set_id, instruction_steps.step)

    if len(current_steps) != len(instruction_steps) or len(current_models) != len(instruction_models):
        return False

    instruction_db_models = [ModelDB(model['model_id'], model['color'], model['name']) for model in instruction_models]
    instruction_db_steps = [StepDB(step['up_mask'], step['up_model_id'], step['down_mask'], step['down_model_id']) for step in instruction_steps]

    models1 = {model.model_id: model for model in instruction_db_models}
    models2 = {model.model_id: model for model in current_models}

    # print(current_models)
    # print()
    # print(current_steps)
    # print()
    # print(instruction_models)
    # print()
    # print(instruction_steps)

    G1 = nx.DiGraph()
    edges1 = _prepare_edges(instruction_db_steps)
    G1.add_edges_from(edges1)

    G2 = nx.DiGraph()
    edges2 = _prepare_edges(current_steps)
    G2.add_edges_from(edges2)

    matcher = nx.isomorphism.DiGraphMatcher(G1, G2)
    if matcher.is_isomorphic():
        mapping = matcher.mapping
        for v1, v2 in mapping.items():
            # Sprawdzanie koloru i typu elementu
            if models1[v1] != models2[v2]:
                return False
            # Przemiana w obecnych połączeniach id modeli na odpowiadające z instrukcji
            _replace_id(current_steps, v2, v1)
    else:
        return False
    
    # Sprawdzanie czy maski odpowiadają
    steps1 = {
        (step.up_id, step.down_id): step for step in instruction_db_steps
    }
    steps2 = {
        (step.up_id, step.down_id): step for step in current_steps
    }

    return steps1 == steps2


def _replace_id(steps: list[StepDB], old: str, new: str) -> list[StepDB]:
    for step in steps:
        if step.down_id == old:
            step.down_id = new
        if step.up_id == old:
            step.up_id = new


class Track(BaseModel):
    name: str
    track: list
    thumbnail: str
    user_id: str


@app.post("/tracks")
async def save_track(track: Track):
    try:
        mongodb.add_track(track.name, track.track, track.thumbnail, track.user_id)
        return {"message": "Track added successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/tracks/user/{user_id}")
async def get_tracks(user_id: str):
    result = mongodb.get_all_tracks(user_id)
    return result


@app.get("/tracks/{track_id}")
async def get_track(track_id: str):
    result = mongodb.get_track(track_id)
    if result:
        return result
    else:
        raise HTTPException(status_code=404, detail="Track not found")


# uvicorn api:app --reload

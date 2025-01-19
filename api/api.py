from typing import Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import database.mongodb as mongodb
from database.connection import find_connected_groups, connection_for_api
import json
from database.instruction import prepare_step, compare_instruction_step
from database.generate_instruction import generate_stepdb

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


@app.get('/parts')
async def get_thumbnails(filter: str = Query(None),
                         category: str = Query(None),
                         size: str = Query(None)):
    size = [int(x) for x in size.split(',')]
    thumbnails = mongodb.get_thumbnails_v3(filter, category, size)
    print(len(thumbnails))
    return thumbnails


@app.get('/model/{id}')
async def get_model(id: str):
    result = mongodb.get_model_v3(id)
    if result:
        return json.loads(result)
    else:
        return HTTPException(status_code=404, detail="Model` not found.")


class Track(BaseModel):
    name: str
    track: list
    thumbnail: str
    user_id: str
    set_id: str = None
    step: int = None


@app.post("/tracks")
async def save_track(track: Track):
    try:
        mongodb.add_track_v3(track.name, track.track,
                             track.thumbnail, track.user_id, track.set_id, track.step)
        return {"message": "Track added successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/tracks/user/{user_id}")
async def get_tracks(user_id: str):
    result = mongodb.get_all_tracks_v3(user_id)
    return result


@app.get("/tracks/{track_id}")
async def get_track(track_id: str):
    result = mongodb.get_track_v3(track_id)
    if result:
        return result
    else:
        raise HTTPException(status_code=404, detail="Track not found")


class Track(BaseModel):
    track: list
    thumbnail: str
    step: int = None


@app.put("/tracks/{track_id}")
async def update_track(track_id: str, track: Track):
    mongodb.update_track(track_id, track.track, track.thumbnail, track.step)


class Scene(BaseModel):
    models: list


@app.post('/connection')
async def get_connections2(models: Scene):
    result = find_connected_groups(models)

    return result


class SceneInstruction(Scene):
    name: str
    user_id: str


@app.post('/instruction/generate')
async def generate_instruction(scene: SceneInstruction):
    models, connections = prepare_step(scene)
    steps = generate_stepdb(models, connections)
    set_id = mongodb.add_instruction(scene.name, scene.user_id, steps)
    return {"steps": steps, "set_id": set_id}


class Instruction(BaseModel):
    set_id: str
    instruction: list[Optional[bytes]]


@app.put('/instruction/generate')
async def add_instruction_to_set(instruction: Instruction):
    mongodb.add_instruction_to_set(instruction.set_id,
                                   instruction.instruction)


class Instruction(BaseModel):
    set_id: str
    step: int
    models: list


@app.post("/instruction/check")
def compare_instruction_files(instruction_steps: Instruction):
    return compare_instruction_step(instruction_steps.models,
                                    instruction_steps.set_id,
                                    instruction_steps.step)


@app.get("/instruction/models/{set_id}/{step}")
async def get_instruction_models(set_id: str, step: int):
    return mongodb.get_step_models(set_id, step)


@app.get("/instruction/{set_id}")
async def get_instruction(set_id: str):
    return mongodb.get_instruction(set_id)


# TODO delete

class Scene(BaseModel):
    models: list


@app.post('/connection123')
async def get_connections(models: Scene):
    return connection_for_api(models)


@app.get("/sets")
async def get_sets_from_user(user_id: str):
    return mongodb.get_sets_from_user(user_id)


@app.get("/sets/{page_index}")
async def get_sets(page_index: int):
    return mongodb.get_sets(page_index)


class Review(BaseModel):
    set_id: str
    comment: str
    user_id: str


@app.post('/comment')
async def add_review(review: Review):
    mongodb.add_comment(review.set_id, review.comment, review.user_id)


@app.get('/comment/{set_id}')
async def get_comments(set_id: str):
    result = mongodb.get_comments_for_set(set_id)
    return result

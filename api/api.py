from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import database.mysqldb as mysqldb
import database.mongodb as mongodb
from database.connection import find_connected_groups
import json

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
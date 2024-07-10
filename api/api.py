from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import database.mysqldb as mysqldb
import database.mongodb as mongodb
from database.connection import connection_for_api
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
async def get_connections(models: Scene):
    result = connection_for_api(models)

    for point in result:
        point['point'] = tuple(map(int, point['point']))

    return result

class Track(BaseModel):
    name: str
    track: list
    thumbnail: str
    user_id: str


@app.post("/tracks")
async def save_track(track: Track):
    try:
        mongodb.add_track(track.name, track.track, track.thumbnail)
        return {"message": "Track added successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/tracks")
async def get_tracks():
    result = mongodb.get_all_tracks()
    if result:

        return result
    else:
        raise HTTPException(status_code=404, detail="Track not found")


@app.get("/tracks/{id}")
async def get_tracks(id: str):
    result = mongodb.get_track(id)
    if result:
        return result
    else:
        raise HTTPException(status_code=404, detail="Track not found")


# uvicorn api:app --reload
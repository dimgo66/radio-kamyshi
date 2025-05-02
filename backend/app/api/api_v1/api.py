from fastapi import APIRouter

from app.api.api_v1.endpoints import users, auth, tracks, playlists, programs, broadcast

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(tracks.router, prefix="/tracks", tags=["tracks"])
api_router.include_router(playlists.router, prefix="/playlists", tags=["playlists"])
api_router.include_router(programs.router, prefix="/programs", tags=["programs"])
api_router.include_router(broadcast.router, prefix="/broadcast", tags=["broadcast"]) 
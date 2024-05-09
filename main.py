"""
Module for defining and running a FastAPI application.

This module contains the main code for setting up and running a FastAPI application
with routes for authentication, contacts, and users.

The `startup` function is an event handler that initializes a connection to the
Redis server for rate limiting.

The `read_root` function is a route handler for the root endpoint ("/") of the
FastAPI application.

The script runs the FastAPI application using uvicorn with host "0.0.0.0" and port 8000.
"""
import redis.asyncio as redis
import uvicorn
from fastapi import FastAPI, Depends
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from fastapi.middleware.cors import CORSMiddleware
from src.conf.config import settings
from src.routes import contacts, auth, users


app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix='/api')
app.include_router(contacts.router, prefix='/api')
app.include_router(users.router, prefix='/api')


@app.on_event("startup")
async def startup():
    """
    Event handler to initialize a connection to the Redis server.

    This function is executed when the FastAPI application starts up.
    It initializes a connection to the Redis server for rate limiting
    using the settings from the configuration.
    """
    r = await redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0, encoding="utf-8",
                          decode_responses=True)
    await FastAPILimiter.init(r)


@app.get("/", dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def read_root():
    """
    Route handler for the root endpoint ("/") of the FastAPI application.

    This function returns a JSON response with a message indicating that
    the task has started. It also applies rate
    limiting to restrict the number of requests to this endpoint.
    """
    return {"message": "Module_11...14 homework started"}


# Run the FastAPI app
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

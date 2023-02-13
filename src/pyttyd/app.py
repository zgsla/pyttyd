from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from pyttyd import __static__, routes

app = FastAPI(routes=[
    routes.terminal.router
])

app.mount("/static", StaticFiles(directory=__static__), name="static")

app.include_router(router=routes.html.router)
app.include_router(router=routes.ssh.router)

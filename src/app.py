from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from src.comparison import run_algorithm_suite


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="Python Maze Solver Visualizer")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class RunRequest(BaseModel):
    size: int = Field(default=15, ge=5, le=60)
    seed: int | None = Field(default=None, ge=0)
    weighted: bool = False
    loop_factor: float = Field(default=0.18, ge=0.0, le=1.0)


@app.get("/")
def read_index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.post("/api/run")
def run_visualization(request: RunRequest) -> dict:
    return run_algorithm_suite(
        size=request.size,
        seed=request.seed,
        weighted=request.weighted,
        loop_factor=request.loop_factor,
    )

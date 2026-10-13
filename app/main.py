from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.agent import generate_plan, replan


BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"


app = FastAPI(
    title="Question → Action Agent",
    description="Turns questions into personalized action plans.",
    version="1.0.0"
)


app.mount(
    "/static",
    StaticFiles(directory=FRONTEND_DIR),
    name="static"
)


class PlanRequest(BaseModel):
    question: str


class ReplanRequest(BaseModel):
    progress: str


@app.get("/")
def home():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "Question → Action Agent"
    }


@app.post("/plan")
def create_plan(request: PlanRequest):
    try:
        if not request.question.strip():
            raise HTTPException(
                status_code=400,
                detail="Please enter a question."
            )

        result = generate_plan(request.question)

        return result

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.post("/replan")
def update_plan(request: ReplanRequest):
    try:
        if not request.progress.strip():
            raise HTTPException(
                status_code=400,
                detail="Please enter your progress."
            )

        result = replan(request.progress)

        return result

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

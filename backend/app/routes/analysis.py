"""
Analysis routes.
"""
from fastapi import APIRouter, Depends, HTTPException, Header
from ..services.analysis_orchestrator import AnalysisOrchestrator
from ..core.security import decode_access_token
from ..database.connection import db_instance

router = APIRouter()


def get_current_user(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token")
    token = authorization.split(" ")[1]
    return decode_access_token(token)


analysis_collection = db_instance.db["analysis_results"]
project_collection = db_instance.db["projects"]
orchestrator = AnalysisOrchestrator(analysis_collection, project_collection)


@router.post("/projects/{project_id}/analysis")
async def create_analysis(project_id: str, current_user: dict = Depends(get_current_user)):
    project = project_collection.find_one({"project_id": project_id})
    if not project or project.get("owner_id") != current_user["user_id"]:
        raise HTTPException(status_code=404, detail="Project not found or not owned by user")

    url = project.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="Project does not have a URL to evaluate")

    return await orchestrator.evaluate_and_store_async(
        url=url,
        project_id=project_id,
        owner_id=current_user["user_id"],
    )


@router.get("/projects/{project_id}/analysis")
def get_analyses(project_id: str):
    return orchestrator.get_all_analyses_for_project(project_id)


@router.get("/projects/{project_id}/analysis/{result_id}")
def get_analysis(result_id: str):
    result = orchestrator.get_analysis_by_id(result_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.delete("/projects/{project_id}/analysis/{result_id}")
def delete_analysis(result_id: str):
    result = orchestrator.delete_analysis(result_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

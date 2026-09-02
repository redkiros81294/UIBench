"""
Project routes.
"""
from fastapi import APIRouter, Depends, HTTPException, Header
from ..services.project_service import ProjectService
from ..models.project import ProjectCreate, ProjectUpdate
from ..core.security import decode_access_token

router = APIRouter()


def get_current_user(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token")
    token = authorization.split(" ")[1]
    return decode_access_token(token)


projects_collection = None
project_service = None


def _get_project_service() -> ProjectService:
    global projects_collection, project_service
    if projects_collection is None:
        from ..database.connection import db_instance
        projects_collection = db_instance.db["projects"]
        project_service = ProjectService(projects_collection)
    return project_service


@router.post("/projects")
def create_project(project_in: ProjectCreate, current_user: dict = Depends(get_current_user)):
    service = _get_project_service()
    return service.create_project(project_in, owner_id=current_user["user_id"])


@router.get("/projects/{project_id}")
def get_project(project_id: str, current_user: dict = Depends(get_current_user)):
    service = _get_project_service()
    project = service.get_project(project_id)
    if "error" in project:
        raise HTTPException(status_code=404, detail=project["error"])
    return project


@router.get("/projects")
def list_projects(current_user: dict = Depends(get_current_user)):
    service = _get_project_service()
    return service.list_projects(current_user["user_id"])


@router.delete("/projects/{project_id}")
def delete_project(project_id: str, current_user: dict = Depends(get_current_user)):
    service = _get_project_service()
    result = service.delete_project(project_id, current_user["user_id"])
    if "error" in result:
        raise HTTPException(
            status_code=403 if result["error"] == "Not authorized to delete this project" else 404,
            detail=result["error"],
        )
    return result


@router.put("/projects/{project_id}")
def update_project(project_id: str, update_in: ProjectUpdate, current_user: dict = Depends(get_current_user)):
    service = _get_project_service()
    result = service.update_project(project_id, current_user["user_id"], update_in.model_dump(exclude_none=True))
    if "error" in result:
        raise HTTPException(
            status_code=403 if result["error"] == "Not authorized to update this project" else 404,
            detail=result["error"],
        )
    return result

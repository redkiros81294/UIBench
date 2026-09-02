"""
Project service.
"""
from typing import Optional
from pymongo.collection import Collection
from ..models.project import ProjectModel, ProjectCreate, ProjectUpdate


class ProjectService:
    def __init__(self, collection: Collection):
        self.collection = collection

    def create_project(self, project_in: ProjectCreate, owner_id: str) -> dict:
        project = ProjectModel(**project_in.model_dump(), owner_id=owner_id)
        project_data = project.model_dump()
        self.collection.insert_one(project_data)
        return {"message": "Project created", "project_id": project.project_id}

    def get_project(self, project_id: str) -> dict:
        project = self.collection.find_one({"project_id": project_id})
        if not project:
            return {"error": "Project not found"}
        project["_id"] = str(project["_id"])
        project.pop("_id", None)
        return project

    def list_projects(self, owner_id: str) -> list[dict]:
        projects = self.collection.find({"owner_id": owner_id})
        result = []
        for project in projects:
            project["_id"] = str(project["_id"])
            result.append(project)
            result[-1].pop("_id", None)
        return result

    def delete_project(self, project_id: str, owner_id: str) -> dict:
        project = self.collection.find_one({"project_id": project_id})
        if not project:
            return {"error": "Project not found"}
        if project["owner_id"] != owner_id:
            return {"error": "Not authorized to delete this project"}

        self.collection.delete_one({"project_id": project_id})
        return {"message": "Project deleted"}

    def update_project(self, project_id: str, owner_id: str, update_data: dict) -> dict:
        project = self.collection.find_one({"project_id": project_id})
        if not project:
            return {"error": "Project not found"}
        if project["owner_id"] != owner_id:
            return {"error": "Not authorized to update this project"}

        restricted_fields = {"project_id", "owner_id", "_id", "creation_date"}
        update_data = {k: v for k, v in update_data.items() if k not in restricted_fields}
        if not update_data:
            return {"error": "No valid fields to update"}

        self.collection.update_one({"project_id": project_id}, {"$set": update_data})
        return {"message": "Project updated"}

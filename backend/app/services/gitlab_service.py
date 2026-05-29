"""GitLab API Integration Service"""
import httpx
from typing import Optional, List, Dict, Any


class GitLabService:
    def __init__(self, base_url: str, access_token: str):
        self.base_url = base_url.rstrip("/")
        self.access_token = access_token
        self.headers = {"PRIVATE-TOKEN": access_token}

    async def get_projects(self, search: str = "", per_page: int = 20) -> List[Dict[str, Any]]:
        """获取 GitLab 项目列表"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v4/projects",
                headers=self.headers,
                params={"search": search, "per_page": per_page, "simple": True},
            )
            response.raise_for_status()
            return response.json()

    async def get_project(self, project_id: int) -> Dict[str, Any]:
        """获取单个项目详情"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v4/projects/{project_id}",
                headers=self.headers,
            )
            response.raise_for_status()
            return response.json()

    async def get_branches(self, project_id: int) -> List[Dict[str, Any]]:
        """获取项目分支列表"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v4/projects/{project_id}/repository/branches",
                headers=self.headers,
            )
            response.raise_for_status()
            return response.json()

    async def get_commits(self, project_id: int, ref_name: str = "main", per_page: int = 20) -> List[Dict[str, Any]]:
        """获取提交记录"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v4/projects/{project_id}/repository/commits",
                headers=self.headers,
                params={"ref_name": ref_name, "per_page": per_page},
            )
            response.raise_for_status()
            return response.json()

    async def get_merge_requests(self, project_id: int, state: str = "opened") -> List[Dict[str, Any]]:
        """获取合并请求"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v4/projects/{project_id}/merge_requests",
                headers=self.headers,
                params={"state": state},
            )
            response.raise_for_status()
            return response.json()

    async def get_pipelines(self, project_id: int, ref: str = None) -> List[Dict[str, Any]]:
        """获取流水线列表"""
        params = {}
        if ref:
            params["ref"] = ref
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v4/projects/{project_id}/pipelines",
                headers=self.headers,
                params=params,
            )
            response.raise_for_status()
            return response.json()

    async def get_pipeline_detail(self, project_id: int, pipeline_id: int) -> Dict[str, Any]:
        """获取流水线详情"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v4/projects/{project_id}/pipelines/{pipeline_id}",
                headers=self.headers,
            )
            response.raise_for_status()
            return response.json()

    async def get_pipeline_jobs(self, project_id: int, pipeline_id: int) -> List[Dict[str, Any]]:
        """获取流水线 Job 列表"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v4/projects/{project_id}/pipelines/{pipeline_id}/jobs",
                headers=self.headers,
            )
            response.raise_for_status()
            return response.json()

    async def get_project_statistics(self, project_id: int) -> Dict[str, Any]:
        """获取项目统计信息"""
        project = await self.get_project(project_id)
        branches = await self.get_branches(project_id)
        mrs = await self.get_merge_requests(project_id, state="opened")
        pipelines = await self.get_pipelines(project_id)
        return {
            "project_name": project.get("name"),
            "default_branch": project.get("default_branch"),
            "branch_count": len(branches),
            "open_merge_requests": len(mrs),
            "total_pipelines": len(pipelines),
            "last_activity": project.get("last_activity_at"),
        }


def get_gitlab_service(base_url: str, access_token: str) -> GitLabService:
    """获取 GitLab 服务实例"""
    return GitLabService(base_url=base_url, access_token=access_token)

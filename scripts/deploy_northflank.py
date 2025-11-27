#!/usr/bin/env python3
"""
Deploy Ozon Parser API to Northflank
Uses Northflank API to create project and service
"""

import os
import sys
import json
import time
import requests
from pathlib import Path

# Northflank API
NORTHFLANK_API = "https://api.northflank.com/v1"
NORTHFLANK_TOKEN = os.environ.get("NORTHFLANK_API_TOKEN")

# Project settings
PROJECT_NAME = "ozon-parser"
SERVICE_NAME = "ozon-parser-api"
REGION = "europe-west"


def api_request(method: str, endpoint: str, data: dict = None) -> dict:
    """Make Northflank API request"""
    headers = {
        "Authorization": f"Bearer {NORTHFLANK_TOKEN}",
        "Content-Type": "application/json"
    }

    url = f"{NORTHFLANK_API}{endpoint}"

    if method == "GET":
        resp = requests.get(url, headers=headers)
    elif method == "POST":
        resp = requests.post(url, headers=headers, json=data)
    elif method == "DELETE":
        resp = requests.delete(url, headers=headers)
    else:
        raise ValueError(f"Unknown method: {method}")

    if resp.status_code >= 400:
        print(f"Error {resp.status_code}: {resp.text}")
        return None

    return resp.json() if resp.text else {}


def create_project():
    """Create Northflank project"""
    print(f"Creating project '{PROJECT_NAME}'...")

    data = {
        "name": PROJECT_NAME,
        "description": "Ozon competitor price parser API",
        "region": REGION
    }

    result = api_request("POST", "/projects", data)

    if result:
        print(f"✅ Project created: {result.get('data', {}).get('id')}")
        return result["data"]["id"]
    else:
        # Try to get existing project
        projects = api_request("GET", "/projects")
        for p in projects.get("data", {}).get("projects", []):
            if p["name"] == PROJECT_NAME:
                print(f"✅ Project already exists: {p['id']}")
                return p["id"]

    return None


def create_service(project_id: str):
    """Create combined service (build + run)"""
    print(f"Creating service '{SERVICE_NAME}'...")

    data = {
        "name": SERVICE_NAME,
        "description": "FastAPI + Playwright parser",
        "type": "combined",
        "billing": {
            "deploymentPlan": "nf-compute-20"
        },
        "buildSettings": {
            "dockerfile": {
                "buildPath": "/",
                "dockerFilePath": "/Dockerfile",
                "dockerWorkDir": "/"
            }
        },
        "deployment": {
            "instances": 1,
            "external": {
                "enabled": True
            },
            "internal": {
                "enabled": False
            }
        },
        "ports": [
            {
                "name": "http",
                "internalPort": 8000,
                "protocol": "HTTP",
                "public": True
            }
        ],
        "healthChecks": [
            {
                "type": "http",
                "path": "/api/health",
                "port": 8000,
                "initialDelaySeconds": 30,
                "periodSeconds": 30,
                "timeoutSeconds": 10,
                "failureThreshold": 3
            }
        ]
    }

    result = api_request("POST", f"/projects/{project_id}/services/combined", data)

    if result:
        service_id = result.get("data", {}).get("id")
        print(f"✅ Service created: {service_id}")
        return service_id

    return None


def set_env_variables(project_id: str, service_id: str, env_vars: dict):
    """Set environment variables for service"""
    print("Setting environment variables...")

    secrets = []
    for key, value in env_vars.items():
        secrets.append({
            "key": key,
            "value": value,
            "secret": "CREDENTIALS" in key or "KEY" in key or "TOKEN" in key
        })

    data = {"variables": secrets}

    result = api_request(
        "POST",
        f"/projects/{project_id}/services/{service_id}/runtime/env",
        data
    )

    if result:
        print(f"✅ {len(secrets)} environment variables set")
        return True

    return False


def trigger_build(project_id: str, service_id: str, repo_url: str, branch: str = "main"):
    """Trigger build from Git repository"""
    print(f"Triggering build from {repo_url}...")

    data = {
        "gitUrl": repo_url,
        "branch": branch
    }

    result = api_request(
        "POST",
        f"/projects/{project_id}/services/{service_id}/builds",
        data
    )

    if result:
        build_id = result.get("data", {}).get("id")
        print(f"✅ Build started: {build_id}")
        return build_id

    return None


def get_service_url(project_id: str, service_id: str) -> str:
    """Get public URL of deployed service"""
    result = api_request("GET", f"/projects/{project_id}/services/{service_id}")

    if result:
        ports = result.get("data", {}).get("ports", [])
        for port in ports:
            if port.get("dns"):
                return f"https://{port['dns']}"

    return None


def main():
    if not NORTHFLANK_TOKEN:
        print("❌ NORTHFLANK_API_TOKEN not set")
        print("Set it with: export NORTHFLANK_API_TOKEN='nf-...'")
        sys.exit(1)

    # Load environment variables
    env_file = Path(__file__).parent.parent / ".env"
    env_vars = {}

    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env_vars[key] = value

    # Create project
    project_id = create_project()
    if not project_id:
        print("❌ Failed to create project")
        sys.exit(1)

    # Create service
    service_id = create_service(project_id)
    if not service_id:
        print("❌ Failed to create service")
        sys.exit(1)

    # Set environment variables
    if env_vars:
        set_env_variables(project_id, service_id, env_vars)

    print("\n" + "=" * 50)
    print("✅ Northflank project created!")
    print("=" * 50)
    print(f"\nProject ID: {project_id}")
    print(f"Service ID: {service_id}")
    print("\nNext steps:")
    print("1. Go to https://app.northflank.com")
    print("2. Connect your GitHub repository")
    print("3. Add GOOGLE_CREDENTIALS_JSON env variable")
    print("4. Deploy!")


if __name__ == "__main__":
    main()

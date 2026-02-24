"""FastAPI application for DeamCompan."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from ..core.artifacts.registry import DecisionRegistry
from ..core.artifacts.store import ArtifactStore
from ..core.workspace.state import WorkspaceState
from .routes import agents, artifacts, meetings, workspace


# Global state (initialized on startup)
store: ArtifactStore | None = None
workspace: WorkspaceState | None = None
registry: DecisionRegistry | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan."""
    global store, workspace, registry

    # Startup
    store = ArtifactStore("./workspace")
    workspace = WorkspaceState(store)
    registry = DecisionRegistry(store)

    yield

    # Shutdown
    pass


app = FastAPI(
    title="DeamCompan API",
    description="Virtual Company Workspace API",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
app.include_router(meetings.router, prefix="/api/meetings", tags=["meetings"])
app.include_router(artifacts.router, prefix="/api/artifacts", tags=["artifacts"])
app.include_router(workspace.router, prefix="/api/workspace", tags=["workspace"])


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "deamcompan"}


# Serve static files for UI
try:
    app.mount("/", StaticFiles(directory="./ui/dist", html=True), name="ui")
except RuntimeError:
    # UI not built yet
    pass


@app.get("/")
async def root():
    """Root endpoint - serve UI or API info."""
    return {
        "name": "DeamCompan",
        "version": "0.1.0",
        "description": "Virtual Company Workspace",
        "docs": "/docs",
    }

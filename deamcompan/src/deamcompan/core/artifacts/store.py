"""Artifact store for persisting artifacts to JSON files."""

import json
import os
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class ArtifactStore:
    """File-based store for artifacts."""

    def __init__(self, base_path: str = "./workspace"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

        # Create subdirectories for different artifact types
        self.artifacts_path = self.base_path / "artifacts"
        self.artifacts_path.mkdir(exist_ok=True)

        self.decisions_path = self.artifacts_path / "decisions"
        self.decisions_path.mkdir(exist_ok=True)

        self.meetings_path = self.artifacts_path / "meetings"
        self.meetings_path.mkdir(exist_ok=True)

        self.initiatives_path = self.artifacts_path / "initiatives"
        self.initiatives_path.mkdir(exist_ok=True)

        self.action_items_path = self.artifacts_path / "action_items"
        self.action_items_path.mkdir(exist_ok=True)

    def _get_path(self, artifact_type: str, artifact_id: str) -> Path:
        """Get the file path for an artifact."""
        type_paths = {
            "decision": self.decisions_path,
            "meeting": self.meetings_path,
            "initiative": self.initiatives_path,
            "action_item": self.action_items_path,
        }
        path = type_paths.get(artifact_type, self.artifacts_path)
        return path / f"{artifact_id}.json"

    def save(self, artifact_type: str, artifact_id: str, data: BaseModel) -> None:
        """Save an artifact to disk."""
        file_path = self._get_path(artifact_type, artifact_id)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data.model_dump(mode="json"), f, indent=2, ensure_ascii=False)

    def load(self, artifact_type: str, artifact_id: str, model_class: type[T]) -> T | None:
        """Load an artifact from disk."""
        file_path = self._get_path(artifact_type, artifact_id)
        if not file_path.exists():
            return None
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return model_class.model_validate(data)

    def list_all(self, artifact_type: str, model_class: type[T]) -> list[T]:
        """List all artifacts of a type."""
        type_paths = {
            "decision": self.decisions_path,
            "meeting": self.meetings_path,
            "initiative": self.initiatives_path,
            "action_item": self.action_items_path,
        }
        path = type_paths.get(artifact_type, self.artifacts_path)
        artifacts = []

        if not path.exists():
            return artifacts

        for file_path in path.glob("*.json"):
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            artifacts.append(model_class.model_validate(data))

        return artifacts

    def delete(self, artifact_type: str, artifact_id: str) -> bool:
        """Delete an artifact. Returns True if deleted, False if not found."""
        file_path = self._get_path(artifact_type, artifact_id)
        if file_path.exists():
            file_path.unlink()
            return True
        return False

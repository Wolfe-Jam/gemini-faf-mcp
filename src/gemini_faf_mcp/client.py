"""
FAF Client - Connect to the Source of Truth

Remote-first client that can hit the Cloud Run endpoint
or parse .faf files locally.
"""

import os
from typing import Any

import requests

# Live endpoint - the "Source of Truth"
DEFAULT_ENDPOINT = "https://faf-source-of-truth-631316210911.us-east1.run.app"
TELEMETRY_ENDPOINT = "https://faf-source-of-truth-631316210911.us-east1.run.app/telemetry"

__version__ = "2.7.0"


def _send_handshake():
    """Silent telemetry ping - tracks active usage on Glory Wall."""
    if os.environ.get("FAF_TELEMETRY_OFF"):
        return  # Respect opt-out
    try:
        requests.post(
            TELEMETRY_ENDPOINT,
            json={
                "event": "client_init",
                "package": "gemini-faf-mcp",
                "version": __version__,
                "security": "SW-02"
            },
            timeout=2
        )
    except Exception:
        pass  # Silent fail - never block user code


class FAFClient:
    """
    Client for FAF (Foundational AI-context Format) operations.

    Can operate in two modes:
    - Remote: Calls the Cloud Run "Source of Truth" endpoint
    - Local: Parses .faf files directly

    Example:
        client = FAFClient()
        dna = client.get_project_dna()  # Uses remote endpoint

        client = FAFClient(local=True)
        dna = client.get_project_dna("project.faf")  # Local parse
    """

    def __init__(
        self,
        endpoint: str = DEFAULT_ENDPOINT,
        agent: str = "gemini",
        local: bool = False
    ):
        self.endpoint = endpoint
        self.agent = agent
        self.local = local
        _send_handshake()  # Glory Wall telemetry

    def get_project_dna(self, path: str = "project.faf") -> dict[str, Any]:
        """
        Retrieve project DNA from .faf file.

        Args:
            path: Path to .faf file (local mode) or path hint (remote mode)

        Returns:
            Parsed FAF data as dictionary
        """
        if self.local:
            from .parser import parse_faf
            return parse_faf(path)

        return self._fetch_remote(path)

    def _fetch_remote(self, path: str) -> dict[str, Any]:
        """Fetch DNA from Cloud Run endpoint."""
        headers = {
            "Content-Type": "application/json",
            "X-FAF-Agent": self.agent
        }
        payload = {"path": path}

        response = requests.post(
            self.endpoint,
            json=payload,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        data: dict[str, Any] = response.json()
        return data

    def update_dna(
        self,
        updates: dict[str, Any],
        message: str = "faf-client: DNA update"
    ) -> dict[str, Any]:
        """
        Update project DNA via Voice-to-FAF endpoint.

        Args:
            updates: Dictionary of field updates (supports dot notation)
            message: Commit message for the update

        Returns:
            Response from the endpoint including sha and security status
        """
        if self.local:
            raise NotImplementedError("Local updates not yet supported")

        headers = {"Content-Type": "application/json"}
        payload = {
            "updates": updates,
            "message": message
        }

        response = requests.put(
            self.endpoint,
            json=payload,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        data: dict[str, Any] = response.json()
        return data

    def get_score(self) -> int:
        """Get the current FAF score (0-100)."""
        dna = self.get_project_dna()
        scores = dna.get("scores") or {}
        raw = scores.get("faf_score", 0)
        return int(raw) if raw is not None else 0

    def is_elite(self) -> bool:
        """Check if project has Elite status (100% score)."""
        return self.get_score() == 100

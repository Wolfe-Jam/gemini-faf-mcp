"""
gemini-faf-mcp - Universal Context Landing Pad for FAF

The "Source of Truth" for FAF (Foundational AI-context Format)
integration with Google Gemini.

Part of the FAF ecosystem:
- claude-faf-mcp (#2759) - Anthropic
- gemini-faf-mcp - Google
- grok-faf-mcp - xAI

Usage:
    from gemini_faf_mcp import FAFClient

    client = FAFClient()
    dna = client.get_project_dna("project.faf")

Live Endpoint:
    https://faf-source-of-truth-631316210911.us-east1.run.app

Glory Wall:
    https://faf-landing.vercel.app/glory.html
"""

__version__ = "1.0.2"
__author__ = "wolfejam"

from .client import FAFClient
from .parser import parse_faf, validate_faf

__all__ = ["FAFClient", "parse_faf", "validate_faf", "__version__"]

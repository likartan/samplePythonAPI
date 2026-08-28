"""Sphinx configuration for the Ticketing System documentation."""

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

project = "Ticketing System"
author = "Ticketing System contributors"
release = "0.1.0"

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "alabaster"

autodoc_typehints = "description"
autodoc_default_options = {
    "members": True,
    "show-inheritance": True,
}
autodoc_mock_imports = ["fastapi", "nicegui"]

nitpicky = True
nitpick_ignore_regex = [
    ("py:class", r"ConfigDict"),
    ("py:class", r"datetime\.datetime"),
    ("py:class", r"enum\.StrEnum"),
    ("py:class", r"fastapi\.APIRouter"),
    ("py:class", r"fastapi\.FastAPI"),
    ("py:class", r"pathlib\.Path"),
    ("py:class", r"pydantic\.main\.BaseModel"),
]
myst_heading_anchors = 3
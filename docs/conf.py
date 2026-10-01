"""Sphinx configuration for the local package."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
project = "EcoAdapt Exporter"
extensions = ["sphinx.ext.autodoc", "sphinx.ext.viewcode", "sphinx_rtd_theme"]
autodoc_member_order = "bysource"
html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
exclude_patterns = ["_build"]

html_title = "EcoAdapt Exporter"
html_theme_options = {
    "collapse_navigation": False,
    "sticky_navigation": True,
    "navigation_depth": 4,
    "style_nav_header_background": "#115e59",
}
html_css_files = ["custom.css"]

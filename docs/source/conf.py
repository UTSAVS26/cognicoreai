# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

# -- Path setup --------------------------------------------------------------
# Tell Sphinx where your code is located
import os
import sys

sys.path.insert(0, os.path.abspath("../../src"))


# -- Project information -----------------------------------------------------

project = "CogniCoreAI"
copyright = "2025, Utsav Singhal"
author = "Utsav Singhal"
release = "2.0.0a1"


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",  # Enables automatic documentation from docstrings
    "sphinx_autodoc_typehints",
]

templates_path = ["_templates"]
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"

# A path to a logo file
html_logo = "_static/cognicoreai_logo.png"

# Theme-specific options for light and dark mode
html_theme_options = {
    "light_css_variables": {
        "color-brand-primary": "#336790",
        "color-brand-content": "#336790",
    },
    "dark_css_variables": {
        "color-brand-primary": "#5b9bd5",
        "color-brand-content": "#5b9bd5",
    },
}

# A folder for custom static files (such as logos)
html_static_path = ["_static"]

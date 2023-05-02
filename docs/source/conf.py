# Configuration file for the Sphinx documentation builder.
import os
import sys
sys.path.insert(0, os.path.abspath('../../src'))
# -- Project information

project = 'Gym Trading Env'
copyright = '2023, Clement Perroud'
author = 'Clement Perroud'

release = '0.1'
version = '0.1.0'

# -- General configuration

extensions = [
    'sphinx.ext.githubpages',
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx_copybutton',
    "sphinxext.opengraph"
]


templates_path = ['_templates']

# -- Options for HTML output

html_theme = 'furo'
html_title = "Gym Trading Environment"
html_static_path = ['_static']
html_favicon = 'images/favicon.png'
html_theme_options = {
    "light_logo": "logo_light-bg.png",
    "dark_logo": "logo_dark-bg.png",
    "sidebar_hide_name": True,
}

html_css_files = ["style.css"]

# -- Open Graph Config

ogp_site_url = "https://gym-trading-env.readthedocs.io/"
ogp_image = "https://gym-trading-env.readthedocs.io/en/latest/_images/render.gif"

ogp_custom_meta_tags = [
    '<meta name="google-site-verification" content="qlHrEXzlsE1udbL26FLjeuxawDdMPJ2EvmFbsrJsrBw" />',
]

ogp_enable_meta_description = True

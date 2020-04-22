#!/usr/bin/env python3
# built-in
import os
import sys
from datetime import date
from pathlib import Path

# external
import alabaster
from recommonmark.transform import AutoStructify

sys.path.append(os.path.abspath('../'))
extensions = [
    'alabaster',
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages',
    'recommonmark',
]

templates_path = ['_templates']
source_suffix = ['.rst', '.md']
master_doc = 'index'

project = 'DepHell'
copyright = '{}, Gram (@orsinium)'.format(date.today().year)
author = 'Gram (@orsinium)'

version = '0.8.2'
release = version

language = None
exclude_patterns = []
todo_include_todos = True

pygments_style = 'sphinx'
html_theme = 'alabaster'
html_theme_path = [alabaster.get_path()]
html_static_path = [str(Path(__file__).parent.parent / 'assets')]
html_theme_options = {
    'logo': 'logo.png',
    'logo_name': 'false',
    'description': 'Python project management',

    'sidebar_width': '240px',
    'show_powered_by': 'false',
    'caption_font_size': '20px',

    # 'color': '#2c3e50',
    'github_banner': 'true',
    'github_user': 'dephell',
    'github_repo': 'dephell',
    'github_type': 'star',

    'extra_nav_links': {
        'Home': 'https://dephell.org/',
        'GitHub repository': 'https://github.com/dephell/dephell',
        'Create an issue': 'https://github.com/dephell/dephell/issues/new',
    },
}

# -- Options for HTMLHelp output ------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'dephelldoc'


# -- Options for LaTeX output ---------------------------------------------

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, 'dephell.tex', 'DepHell Documentation',
     '@orsinium', 'manual'),
]


# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [(master_doc, 'dephell', 'DepHell Documentation', [author], 1)]


# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, 'dephell', 'DepHell Documentation',
     author, 'DepHell', 'One line description of project.', 'Miscellaneous'),
]


# https://github.com/rtfd/recommonmark/blob/master/docs/conf.py
def setup(app):
    config = {
        # 'url_resolver': lambda url: github_doc_root + url,
        'auto_toc_tree_section': 'Contents',
        'enable_eval_rst': True,
    }
    app.add_config_value('recommonmark_config', config, True)
    app.add_transform(AutoStructify)

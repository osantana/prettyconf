from importlib.metadata import version as get_version

project = 'prettyconf'
author = 'Osvaldo Santana Neto'
copyright = f'2015-2026, {author}'  # noqa: A001

release = get_version('prettyconf')
version = '.'.join(release.split('.')[:2])

extensions = [
    'sphinx.ext.autodoc',
    'sphinx_rtd_theme',
]

autoclass_content = 'both'

master_doc = 'index'
source_suffix = '.rst'
language = 'en'
exclude_patterns = []
pygments_style = 'sphinx'

html_theme = 'sphinx_rtd_theme'
htmlhelp_basename = 'prettyconfdoc'

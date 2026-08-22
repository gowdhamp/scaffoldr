"""Static application metadata shared across modules.

Kept separate from main.py so other modules (e.g. core.upgrade) can import
the current version without creating a circular import with the CLI entrypoint.
"""

APP_NAME = "Scaffoldr"
VERSION = "1.3.3"
GITHUB_REPO = "gowdhamp/scaffoldr"

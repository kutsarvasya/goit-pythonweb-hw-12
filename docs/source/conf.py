import os
import sys

sys.path.insert(0, os.path.abspath("../.."))

os.environ.setdefault(
    "DB_URL",
    "postgresql+asyncpg://postgres:567234@localhost:5432/contacts_app",
)
os.environ.setdefault("JWT_SECRET", "test_secret")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("JWT_EXPIRATION_SECONDS", "3600")

os.environ.setdefault("BREVO_API_KEY", "test_brevo_api_key")

os.environ.setdefault("MAIL_FROM", "test@example.com")
os.environ.setdefault("MAIL_FROM_NAME", "Contacts API")

os.environ.setdefault("REDIS_URL", "redis://localhost:6379")

os.environ.setdefault("CLD_NAME", "test")
os.environ.setdefault("CLD_API_KEY", "123456")
os.environ.setdefault("CLD_API_SECRET", "test")

project = "Contacts API"
copyright = "2026, V_Kutsar"
author = "V_Kutsar"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
]

templates_path = ["_templates"]
exclude_patterns = []

html_theme = "alabaster"
html_static_path = ["_static"]

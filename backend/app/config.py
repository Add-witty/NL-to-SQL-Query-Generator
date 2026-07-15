from pydantic import BaseModel


class Settings(BaseModel):
    """
    Central application settings.

    Kept minimal by design: this project has no auth, no database
    connection, and no cloud deployment (see project_scope.md), so
    there are no secrets or environment-dependent values yet.
    """

    app_name: str = "Natural Language to SQL Generator"
    version: str = "0.1.0"


settings = Settings()

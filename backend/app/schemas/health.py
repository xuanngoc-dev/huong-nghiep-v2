from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    app_name: str


class DatabaseHealthResponse(BaseModel):
    status: str
    database: str
    host: str
    port: int
    user: str
    detail: str | None = None

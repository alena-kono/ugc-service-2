import pydantic
from src.settings.base import BaseAppSettings


class JaegerSettings(BaseAppSettings):
    agent_host: str = pydantic.Field(env="JAEGER_AGENT_HOST", default="localhost")
    agent_port: int = pydantic.Field(env="JAEGER_AGENT_PORT", default=6831)
    service_name: str = pydantic.Field(env="JAEGER_SERVICE_NAME", default="UNKNOWN")
    enabled: bool = pydantic.Field(env="JAEGER_ENABLED", default=False)

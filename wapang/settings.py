import os

from pydantic_settings import BaseSettings, SettingsConfigDict

# 환경 변수로 설정된 환경을 가져옵니다.
ENV = os.getenv("ENV", "local")
assert ENV in ("local", "test", "prod")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=f".env.{ENV}",         # 환경에 따라 자동 선택
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DB_DIALECT: str
    DB_ASYNC_DRIVER: str
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_DATABASE: str


    # property 데코레이터는 메서드를 필드처럼 사용할 수 있게 해줍니다.
    # 예컨데, SETTINGS.is_local() 대신 SETTINGS.is_local 으로 사용할 수 있습니다.
    @property
    def is_local(self) -> bool:
        return ENV == "local"
    
    @property
    def is_test(self) -> bool:
        return ENV == "test"

    @property
    def is_prod(self) -> bool:
        return ENV == "prod"

    # @property
    # def env_file(self) -> str:
    #     return f".env.{ENV}"


SETTINGS = Settings()
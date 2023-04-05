from pydantic import BaseModel, StrictStr, HttpUrl, PositiveInt


class DBConfig(BaseModel):
    user: StrictStr
    password: StrictStr
    host: StrictStr
    dbname: StrictStr
    port: PositiveInt

    @property
    def url(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.dbname}"


class AppConfig(BaseModel):
    db: DBConfig

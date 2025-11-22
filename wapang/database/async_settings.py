from wapang.settings import SETTINGS



class AsyncDatabaseSettings():

    @property
    def url(self) -> str:
        return f"{SETTINGS.DB_DIALECT}+{SETTINGS.DB_ASYNC_DRIVER}://{SETTINGS.DB_USER}:{SETTINGS.DB_PASSWORD}@{SETTINGS.DB_HOST}:{SETTINGS.DB_PORT}/{SETTINGS.DB_DATABASE}"



ASYNC_DB_SETTINGS = AsyncDatabaseSettings()
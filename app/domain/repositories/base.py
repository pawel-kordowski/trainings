from app.database import async_session


class PostgresRepository:
    async def __aenter__(self):
        self.session = async_session()
        await self.session.begin()
        return self

    async def __aexit__(self, *args, **kwargs):
        await self.session.close()

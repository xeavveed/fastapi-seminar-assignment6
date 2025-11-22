from typing import TYPE_CHECKING, AsyncGenerator
import pytest
import pytest_asyncio

if TYPE_CHECKING:
    from httpx import AsyncClient

# 하위 테스트 모듈에서 공통으로 사용할 플러그인/픽스처 로드
pytest_plugins = ["tests.stores.conftest"]


@pytest.fixture
def user_signup_data():
    return {"email": "test1234@snu.ac.kr", "password": "password123"}


@pytest.fixture
def another_user_signup_data():
    return {"email": "another_user@snu.ac.kr", "password": "password1234"}


@pytest_asyncio.fixture(autouse=True, scope="session")
async def set_test_env():
    import os

    os.environ["ENV"] = "test"


@pytest_asyncio.fixture(scope="function")
async def async_client(set_test_env) -> AsyncGenerator["AsyncClient", None]:
    from httpx import AsyncClient, ASGITransport

    from wapang.main import app
    from wapang.database.common import Base
    from wapang.database.async_connection import async_db_manager

    # 데이터베이스 초기화 및 스키마 반영
    async with async_db_manager.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test/"
    ) as client:
        yield client

    # 데이터베이스 스키마 삭제 및 초기화
    async with async_db_manager.engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await async_db_manager.engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def user(async_client: "AsyncClient", user_signup_data: dict) -> dict:
    req = user_signup_data

    res = await async_client.post("/api/users/", json=req)

    return res.json()


@pytest_asyncio.fixture(scope="function")
async def token(
    async_client: "AsyncClient", user: dict, user_signup_data: dict
) -> dict:
    req = {"email": user_signup_data["email"], "password": user_signup_data["password"]}

    res = await async_client.post("/api/auth/tokens", json=req)
    res_json = res.json()

    return {
        "access_token": res_json["access_token"],
        "refresh_token": res_json["refresh_token"],
    }


@pytest_asyncio.fixture(scope="function")
async def access_token(token: dict) -> str:
    return token["access_token"]


@pytest_asyncio.fixture(scope="function")
async def another_user_access_token(
    async_client: "AsyncClient", another_user_signup_data: dict
) -> str:
    signup_res = await async_client.post("/api/users/", json=another_user_signup_data)
    signup_res.raise_for_status()

    login_req = another_user_signup_data
    login_res = await async_client.post("/api/auth/tokens", json=login_req)
    login_res.raise_for_status()

    login_json = login_res.json()

    return login_json["access_token"]

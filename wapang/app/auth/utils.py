from datetime import datetime, timedelta
from typing import Annotated, Optional

from fastapi import Depends, Header
import argon2
from authlib.jose import jwt, JWTClaims
from authlib.jose.errors import JoseError

from wapang.app.users.services import UserService
from wapang.app.auth.settings import AUTH_SETTINGS
from wapang.app.auth.exceptions import (
    BadAuthorizationHeaderException,
	UnauthenticatedException,
    InvalidAccountException,
    InvalidTokenException
)
from wapang.app.users.models import User

def verify_password(plain_password: str, hashed_password: str) -> None:
	try:
		argon2.PasswordHasher().verify(hashed_password, plain_password)
	except argon2.exceptions.VerifyMismatchError:
		raise InvalidAccountException()
	
def issue_token(user_id: str, lifespan_minutes: int, secret: str) -> str:
	header = {'alg': 'HS256'}
	payload = {
		'sub': user_id,
		'exp': int((datetime.now() + timedelta(minutes=lifespan_minutes)).timestamp())
	}
	return str(jwt.encode(header, payload, key=secret), 'utf-8')

def verify_and_decode_token(token: str, secret: str) -> JWTClaims:
	try:
		claims = jwt.decode(token, key=secret)
		claims.validate()
		return claims
	except JoseError:
		raise InvalidTokenException()
	
def get_token_from_authorization_header(authorization: str) -> str:
	authorization_parts = authorization.split()
	if len(authorization_parts) != 2 \
			or authorization_parts[0].lower() != "bearer":
		raise BadAuthorizationHeaderException()
	token = authorization_parts[1]
	return token

async def login_with_header(
        user_service: Annotated[UserService, Depends()],
        authorization: Annotated[str | None, Header()] = None
):
	if authorization is None:
		raise UnauthenticatedException()
	
	token = get_token_from_authorization_header(authorization)
	claims = verify_and_decode_token(token, AUTH_SETTINGS.ACCESS_TOKEN_SECRET)

	user_id = claims.get('sub', None)
	if user_id is None:
		raise InvalidTokenException()
	
	user = await user_service.get_user_by_id(user_id)
	if user is None:
		raise InvalidAccountException()
	return user

async def optional_login_with_header(
    user_service: Annotated[UserService, Depends()],
    authorization: Annotated[str | None, Header()] = None
) -> Optional[User]:
    if authorization is None:
        return None #비로그인 상황 시 None 반환
    try:
        token = get_token_from_authorization_header(authorization)
        claims = verify_and_decode_token(token, AUTH_SETTINGS.ACCESS_TOKEN_SECRET)

        user_id = claims.get('sub')
        if user_id is None:
            return None
        return await user_service.get_user_by_id(user_id)
    except Exception:
        return None #비로그인 상황 시 None 반환
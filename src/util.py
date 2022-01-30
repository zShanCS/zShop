from fastapi import HTTPException, status, Depends
from sqlalchemy.orm.session import Session


from src.hashing import verify_password
from src.database import get_db
from src.oauth2 import oauth2_scheme
from src.token import verify_token_and_get_data
from src import crud

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail='Could not validate credentials',
    headers={"WWW-Authenticate": "Bearer"}
)
login_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Incorrect username or password",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    email: str = verify_token_and_get_data(token, credentials_exception)
    user = crud.get_user_by_email(db=db, user_email=email)
    if not user:
        raise credentials_exception
    return user


def authenticate_user(email: str, password: str, db: Session):
    user = crud.get_user_by_email(db=db, user_email=email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

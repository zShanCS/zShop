from fastapi import APIRouter, Depends
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm.session import Session


from src.database import get_db
from src.util import authenticate_user, login_exception
from src.token import create_access_token

from src import schemas

router = APIRouter(
    prefix='/token',
    tags=['Authentication']
)


@router.post('/', response_model=schemas.Token)
async def login_for_token_access(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(email=form_data.username,
                             password=form_data.password, db=db)
    if not user:
        raise login_exception
    access_token = create_access_token(data={"sub": user.email})
    return {'access_token': access_token, 'token_type': 'bearer'}

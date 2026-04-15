from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from . import crud, schemas, models
from .database import get_db

router = APIRouter(prefix="/api/users", tags=["users"])


def success_response(data=None):
    return {"code": 200, "message": "ok", "data": data}


def error_response(code: int, message: str):
    return {"code": code, "message": message, "data": None}


@router.get("")
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return success_response([schemas.UserResponse.from_orm(u) for u in users])


@router.get("/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return success_response(schemas.UserResponse.from_orm(user))


@router.post("")
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    created_user = crud.create_user(db=db, user=user)
    return success_response(schemas.UserResponse.from_orm(created_user))


@router.put("/{user_id}")
def update_user(user_id: int, user: schemas.UserUpdate, db: Session = Depends(get_db)):
    updated_user = crud.update_user(db, user_id=user_id, user=user)
    if updated_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return success_response(schemas.UserResponse.from_orm(updated_user))


@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    deleted_user = crud.delete_user(db, user_id=user_id)
    if deleted_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return success_response(schemas.UserResponse.from_orm(deleted_user))

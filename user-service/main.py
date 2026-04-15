from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import api, models, database

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="User Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api.router)


@app.on_event("startup")
def startup_event():
    db = database.SessionLocal()
    try:
        if db.query(models.User).count() == 0:
            sample_users = [
                models.User(username="test1", password="123456", nickname="测试用户1", phone="13800138001"),
                models.User(username="test2", password="123456", nickname="测试用户2", phone="13800138002"),
            ]
            for user in sample_users:
                db.add(user)
            db.commit()
    finally:
        db.close()


@app.get("/")
def root():
    return {"message": "User Service is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)

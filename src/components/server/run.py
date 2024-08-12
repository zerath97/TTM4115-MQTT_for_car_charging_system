from fastapi import FastAPI
import uvicorn
import endpoints
import models
from database import SessionLocal, engine

def run():
    ''' Starts the server '''

    models.Base.metadata.create_all(bind=engine) # Creates database file, if not present

    app = FastAPI()
    app.include_router(endpoints.router)
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")

if __name__ == "__main__":
    run()
from fastapi import FastAPI
from dotenv import load_dotenv
import os, uvicorn

load_dotenv()
app = FastAPI()

from routes.start import router as start_app
from routes.prompt import router as prompt_router
from routes.files import router as file_router
from routes.authenticate import auth_router
from routes.logout import logout_router
app.include_router(start_app)
app.include_router(prompt_router)
app.include_router(file_router)
app.include_router(auth_router)
app.include_router(logout_router)


if __name__ == "__main__":
    host = os.getenv("HOST")
    port = int(os.getenv("PORT"))
    uvicorn.run("main:app", host=host, port=port, reload=False)




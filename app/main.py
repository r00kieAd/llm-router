from fastapi import FastAPI
from dotenv import load_dotenv
import os, uvicorn
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
app = FastAPI()

cors_env = os.getenv("CORS_ALLOWED_ORIGINS", "")
if cors_env:
    allow_origins = [o.strip() for o in cors_env.split(",") if o.strip()]
else:
    allow_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from routes.start import router as start_app
from routes.prompt import router as prompt_router
from routes.files import router as file_router
from routes.authenticate import auth_router
from routes.logout import logout_router
from routes.settings import settings_router
app.include_router(start_app)
app.include_router(prompt_router)
app.include_router(file_router)
app.include_router(auth_router)
app.include_router(logout_router)
app.include_router(settings_router)


if __name__ == "__main__":
    host = os.getenv("HOST")
    port = int(os.getenv("PORT"))
    uvicorn.run("main:app", host=host, port=port, reload=False)




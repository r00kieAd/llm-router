from fastapi import FastAPI

app = FastAPI()

from app.routes.start import router as start_app
from app.routes.prompt import router as prompt_router
from app.routes.files import router as file_router
app.include_router(start_app)
app.include_router(prompt_router)
app.include_router(file_router)

for route in app.routes:
    print(f"{route.path} [{','.join(route.methods)}]")






import os
from fastapi import UploadFile

ALLOWED_EXTENSIONS = ('.txt', '.pdf')
UPLOAD_DIR = 'app/data'
MAX_SIZE = 5

def save_file(file: UploadFile, save_dir: str = UPLOAD_DIR) -> str:
    filename = file.filename
    if not filename or not filename.lower().endswith(ALLOWED_EXTENSIONS):
        raise ValueError("Unsupported file format")
    content = file.file.read()
    if len(content) > MAX_SIZE * 1024 * 1024:
        raise ValueError(f"File too large, max limit is {MAX_SIZE}")
    
    os.makedirs(save_dir, exist_ok=True)
    path = os.path.join(save_dir, filename)

    with open(path, "wb") as f:
        f.write(content)
    return path

def clear_files(save_dir: str = UPLOAD_DIR) -> list[str]:
    deleted = []
    if not os.path.exists(save_dir):
        return deleted
    
    for name in os.listdir(save_dir):
        if name.startswith("."):
            continue
        file_path = os.path.join(save_dir, name)
        if os.path.isfile(file_path):
            os.remove(file_path)
            deleted.append(name)
    return deleted
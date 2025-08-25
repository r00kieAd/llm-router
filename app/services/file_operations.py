import os
from fastapi import UploadFile

ALLOWED_EXTENSIONS = ('.txt', '.pdf')
UPLOAD_DIR = os.path.join(os.getcwd(), "data")
MAX_SIZE = 1

def save_file(file: UploadFile, username) -> str:
    username = os.path.basename(username)
    save_dir = os.path.join(UPLOAD_DIR, username)
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

def clear_files(username) -> list[str]:
    username = os.path.basename(username)
    save_dir = os.path.join(UPLOAD_DIR, username)
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
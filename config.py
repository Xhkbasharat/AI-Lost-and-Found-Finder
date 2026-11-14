from pathlib import Path

# Project directory
BASE_DIR = Path(__file__).resolve().parent

# Storage directories
UPLOAD_FOLDER = BASE_DIR / "uploads"
DATABASE_PATH = BASE_DIR / "lost_found.db"

# Create upload folder automatically
UPLOAD_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)

# AI model configuration
MODEL_NAME = "openai/clip-vit-base-patch32"

# Image processing configuration
IMAGE_SIZE = (224, 224)

# Similarity threshold
SIMILARITY_THRESHOLD = 0.70

# Maximum upload size: 10 MB
MAX_CONTENT_LENGTH = 10 * 1024 * 1024

# Supported image formats
ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "webp"
}

# Flask configuration
SECRET_KEY = "change-this-to-a-random-secret-key"
DEBUG = True

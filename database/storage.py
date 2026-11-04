import os
import uuid
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client


# Load environment variables from project root
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
BUCKET_NAME = os.getenv("SUPABASE_STORAGE_BUCKET", "product-images")

MAX_FILE_SIZE = 5 * 1024 * 1024

# Accepted image formats and their file signatures
IMAGE_SIGNATURES = {
    "jpeg": (".jpg", lambda data: data.startswith(b"\xff\xd8\xff")),
    "png": (".png", lambda data: data.startswith(b"\x89PNG\r\n\x1a\n")),
    "webp": (
        ".webp",
        lambda data: (
            len(data) >= 12
            and data.startswith(b"RIFF")
            and data[8:12] == b"WEBP"
        ),
    ),
}


def get_storage_client():
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        raise RuntimeError(
            "Supabase Storage credentials are missing from .env"
        )

    return create_client(
        SUPABASE_URL,
        SUPABASE_SERVICE_ROLE_KEY
    )


def upload_product_image(image_file):
    if image_file is None:
        raise ValueError("No image file provided")

    # Always read from the beginning of the uploaded file
    image_file.stream.seek(0)

    image_data = image_file.stream.read(MAX_FILE_SIZE + 1)

    # Reset the stream so it remains reusable
    image_file.stream.seek(0)

    if not image_data:
        raise ValueError("The uploaded image is empty")

    if len(image_data) > MAX_FILE_SIZE:
        raise ValueError("Image size cannot exceed 5 MB")

    image_format = None

    for fmt, (extension, validator) in IMAGE_SIGNATURES.items():
        if validator(image_data):
            image_format = fmt
            break

    if image_format is None:
        raise ValueError("Only valid JPEG, PNG and WebP images are allowed")

    extension = IMAGE_SIGNATURES[image_format][0]

    # Generate a unique filename to avoid collisions
    file_path = f"products/{uuid.uuid4().hex}{extension}"

    content_types = {
        "jpeg": "image/jpeg",
        "png": "image/png",
        "webp": "image/webp",
    }

    try:
        client = get_storage_client()

        client.storage.from_(BUCKET_NAME).upload(
            path=file_path,
            file=image_data,
            file_options={
                "content-type": content_types[image_format],
                "upsert": "false",
            }
        )

        return file_path

    except Exception as error:
        raise RuntimeError(
            f"Product image upload failed: {error}"
        ) from error


def get_product_image_url(file_path):
    if not file_path:
        return None

    try:
        client = get_storage_client()

        return client.storage.from_(BUCKET_NAME).get_public_url(
            file_path
        )

    except Exception as error:
        raise RuntimeError(
            f"Could not retrieve product image URL: {error}"
        ) from error


def delete_product_image(file_path):
    if not file_path:
        return

    # Only allow paths inside the products folder
    if not file_path.startswith("products/") or ".." in file_path:
        raise ValueError("Invalid product image path")

    try:
        client = get_storage_client()

        client.storage.from_(BUCKET_NAME).remove(
            [file_path]
        )

    except Exception as error:
        raise RuntimeError(
            f"Product image deletion failed: {error}"
        ) from error
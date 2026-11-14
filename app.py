import os
import uuid

from pathlib import Path
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash
)
from werkzeug.utils import secure_filename

from config import (
    UPLOAD_FOLDER,
    MAX_CONTENT_LENGTH,
    ALLOWED_EXTENSIONS,
    SECRET_KEY
)

from database import ItemDatabase
from image_engine import ImageEngine
from similarity import SimilarityEngine


app = Flask(__name__)

app.secret_key = SECRET_KEY

app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)

app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH


# Initialize database and AI engine
database = ItemDatabase()

image_engine = ImageEngine()

similarity_engine = SimilarityEngine(
    database,
    image_engine
)


def allowed_file(filename):

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


def save_image(file):

    if not file or not file.filename:
        raise ValueError("Please select an image.")

    if not allowed_file(file.filename):
        raise ValueError("Unsupported image format.")

    # Generate unique filename
    extension = file.filename.rsplit(".", 1)[1].lower()

    filename = secure_filename(
        f"{uuid.uuid4().hex}.{extension}"
    )

    file_path = Path(
        app.config["UPLOAD_FOLDER"]
    ) / filename

    # Validate image before saving
    from PIL import Image

    file.stream.seek(0)

    with Image.open(file.stream) as image:
        image.verify()

    file.stream.seek(0)
    file.save(file_path)

    return str(file_path)


@app.route("/")
def home():

    items = database.get_items()

    return render_template(
        "index.html",
        items=items
    )


@app.route("/report", methods=["POST"])
def report_item():

    try:

        item_name = request.form.get(
            "item_name", ""
        ).strip()

        description = request.form.get(
            "description", ""
        ).strip()

        category = request.form.get(
            "category", ""
        ).strip()

        location = request.form.get(
            "location", ""
        ).strip()

        item_type = request.form.get(
            "item_type", ""
        ).strip().lower()

        image = request.files.get("image")

        if not item_name:
            raise ValueError("Item name is required.")

        if item_type not in {"lost", "found"}:
            raise ValueError("Invalid item type.")

        image_path = save_image(image)

        database.add_item(
            item_name,
            description,
            category,
            location,
            image_path,
            item_type
        )

        flash("Item registered successfully!", "success")

    except Exception as error:

        flash(str(error), "error")

    return redirect(url_for("home"))


@app.route("/search", methods=["POST"])
def search_item():

    try:

        image = request.files.get("image")

        query_path = save_image(image)

        results = similarity_engine.search_similar_items(
            query_path,
            top_k=10
        )

        # Remove temporary search image
        Path(query_path).unlink(missing_ok=True)

        return render_template(
            "index.html",
            items=database.get_items(),
            results=results
        )

    except Exception as error:

        flash(str(error), "error")

        return redirect(url_for("home"))


@app.route("/resolve/<int:item_id>", methods=["POST"])
def resolve_item(item_id):

    if database.update_status(item_id, "resolved"):

        flash("Item marked as resolved.", "success")

    else:

        flash("Item not found.", "error")

    return redirect(url_for("home"))


@app.errorhandler(413)
def file_too_large(error):

    flash("Image exceeds the 10 MB limit.", "error")

    return redirect(url_for("home"))


if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )

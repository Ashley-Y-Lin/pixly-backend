"""Flask app for Pix.ly"""

import os

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from sqlalchemy import create_engine, text, insert
from werkzeug.datastructures import FileStorage

from PIL import Image, ImageOps, ImageChops, ImageFilter
import requests
from io import BytesIO

from models import db, connect_db, Photo
from aws import upload_photo_s3, remove_photo_s3
from exif import get_exif_data

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "postgresql:///photos"
)
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "ashley-secret"

connect_db(app)

engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])

with engine.connect() as connection:
    try:
        result = connection.execute(text("SELECT * FROM photos"))
        print("Connection successful!")
    except Exception as e:
        print(f"Connection error: {str(e)}")


@app.before_request
def basic_authentication():
    if request.method.lower() == "options":
        return Response()


######### PHOTOS ROUTES #########


@app.get("/api/photos")
def list_photos():
    """Return all photos in system.

    Returns JSON like:
        {photos: [{id, caption, file_name, aws_s3, exif_data}, ...]}
    """

    photos = [photo.to_dict() for photo in Photo.query.all()]
    return jsonify(photos=photos)


@app.post("/api/photos")
def create_photo():
    """Add photo, and return data about new photo.

    Takes as input formData representing a photo like:
        { caption, fileObject }

    Returns JSON like:
        {photo: [{id, caption, file_name, aws_s3, exif_data}]}
    """

    caption = request.form.get("caption")
    file_object = request.files["fileObject"]

    file_name = file_object.filename
    s3_file_path = upload_photo_s3(file_object)
    exif_data = get_exif_data(file_object)

    photo = Photo(
        caption=caption,
        file_name=file_name,
        aws_s3=s3_file_path,
        exif_data=exif_data or {},
    )

    db.session.add(photo)
    db.session.commit()

    return (jsonify(photo=photo.to_dict()), 201)


@app.post("/api/photos-bulk")
def create_photos_bulk():
    """Adds a bunch of photos to the database, returns number of photos added.

    Takes as input an array of photos objects like:
        [ { caption, URL }... ]

    Returns JSON of photos added, like:
        {photo: [{id, caption, file_name, aws_s3, exif_data}...]}
    """
    photos_data = request.json

    photos = []
    for photo in photos_data:
        caption = photo.get("caption")
        URL = photo.get("URL")

        response = requests.get(URL)

        file_object = BytesIO(response.content)

        file_storage = FileStorage(
            stream=file_object,
            filename=caption,
            content_type="image/jpeg",
        )

        s3_file_path = upload_photo_s3(file_storage)
        exif_data = get_exif_data(file_storage)

        photo = Photo(
            caption=caption,
            file_name=caption,
            aws_s3=s3_file_path,
            exif_data=exif_data or {},
        )

        photos.append(photo)

        file_object.close()

    db.session.execute(insert(Photo), [photo.to_dict() for photo in photos])
    db.session.commit()

    return (jsonify(photos=[photo.to_dict() for photo in photos]), 201)


@app.get("/api/photos/<int:photo_id>")
def get_photo(photo_id):
    """Return data on specific photo.

    Returns JSON like:
        {photo: [{id, caption, file_name, aws_s3, exif_data}]}
    """

    photo = Photo.query.get_or_404(photo_id)
    return jsonify(photo=photo.to_dict())


@app.patch("/api/photos/<int:photo_id>")
def update_photo(photo_id):
    """Update photo caption from data in request. Return updated data. The only
    field that can be updated is caption, takes as input JSON like
    { caption, file_name, aws_s3, exif_data }

    Returns JSON like:
        {photo: [{id, caption, file_name, aws_s3, exif_data}]}
    """

    data = request.json

    photo = Photo.query.get_or_404(photo_id)

    if data.get("aws_s3"):
        remove_photo_s3(photo)

    photo.caption = data.get("caption", photo.caption)
    photo.file_name = data.get("file_name", photo.file_name)
    photo.aws_s3 = data.get("aws_s3", photo.aws_s3)
    photo.exif_data = data.get("exif_data", photo.exif_data)

    db.session.add(photo)
    db.session.commit()

    return jsonify(photo=photo.to_dict())


@app.delete("/api/photos/<int:photo_id>")
def remove_photo(photo_id):
    """Delete photo and return confirmation message.

    Returns JSON of {deleted: "photo_id"}
    """

    photo = Photo.query.get_or_404(photo_id)

    deleted_photo_filename = remove_photo_s3(photo)

    db.session.delete(photo)
    db.session.commit()

    return jsonify(deleted=photo_id)


######### SEARCH ROUTES #########


@app.get("/api/photos/search-caption/<search_term>")
def search_photos_caption(search_term):
    """Searches photos for search term in caption, using PostgreSQL full-text
    search. Used in caption search on front-end.

    Returns JSON like:
        {photos: [{id, caption, file_name, aws_s3, exif_data}, ...]}
    """

    with engine.connect() as connection:
        query = """
        SELECT row_to_json(t)
        FROM (
            SELECT *
            FROM photos
            WHERE to_tsvector('english', caption) @@ to_tsquery(:search_term)
        ) t
        """

        result = connection.execute(text(query), {"search_term": search_term})

        rows = [row[0] for row in result]

        return jsonify(photos=rows)


@app.get("/api/photos/search-metadata/<search_term>")
def search_photos_metadata(search_term):
    """Searches photos for given metadata field values, using PostgreSQL
    full-text search. Used in metadata search on front-end.

    Returns JSON like:
        {photos: [{id, caption, file_name, aws_s3, exif_data}, ...]}
    """
    print("search_photos_metadata is running")

    with engine.connect() as connection:
        query = """
        SELECT row_to_json(t)
        FROM (
            SELECT *
            FROM photos
            WHERE json_to_tsvector('English', exif_data, '"all"') @@ to_tsquery(:search_term)
        ) t
        """

        result = connection.execute(text(query), {"search_term": search_term})
        # print("all rows", result.fetchall())

        rows = [row[0] for row in result]

        return jsonify(photos=rows)


######### EDIT ROUTES #########


@app.post("/api/photos/edit/<int:photo_id>/<edit_type>")
def create_edit_preview(photo_id, edit_type):
    """Edits photo, and returns local file link to edited photo preview.

    Returns JSON like: {editedPhotoURL}
        where editedPhotoURL is an object like
        {file_name: string, aws_s3: string, exif_data: object}
    """

    photo_data = Photo.query.get_or_404(photo_id)

    # Download the image from AWS S3
    response = requests.get(photo_data.aws_s3)

    local_path = f"/Users/AshleyLin1/rithm/exercises/pix.ly/pix.ly frontend/pixly/src/edit-previews/original-{photo_id}.jpg"
    with open(local_path, "wb") as file:
        file.write(response.content)

    image = Image.open(local_path)

    if edit_type == "blackAndWhite":
        edited_image = image.convert("L")
    elif edit_type == "addBorder":
        edited_image = ImageOps.expand(image, border=30, fill="black")
    elif edit_type == "invertColors":
        edited_image = ImageChops.invert(image)
    elif edit_type == "sketch":
        edited_image = image.convert("L").filter(ImageFilter.FIND_EDGES)

    edited_photo_filename = f"edited-{photo_data.file_name}.jpg"
    edited_photo_url = f"/Users/AshleyLin1/rithm/exercises/pix.ly/pix.ly frontend/pixly/src/edit-previews/edited-{photo_data.file_name}.jpg"
    edited_image.save(edited_photo_url)

    file_object = open(edited_photo_url, "rb")

    file_storage = FileStorage(
        stream=file_object,
        filename=edited_photo_filename,
        content_type="image/jpeg",
    )

    s3_file_path = upload_photo_s3(file_storage)
    exif_data = get_exif_data(file_storage)

    file_object.close()
    os.remove(local_path)
    os.remove(edited_photo_url)

    return {
        "editedPhotoURL": {
            "file_name": edited_photo_filename,
            "aws_s3": s3_file_path,
            "exif_data": exif_data,
        }
    }

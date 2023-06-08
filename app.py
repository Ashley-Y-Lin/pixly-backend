"""Flask app for Pix.ly"""

import os

from flask import Flask, request, jsonify, Response
from flask_cors import CORS

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


@app.before_request
def basic_authentication():
    if request.method.lower() == "options":
        return Response()


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
    """Update photo caption from data in request. Return updated data.

    Returns JSON like:
        {photo: [{id, caption, file_name, aws_s3, exif_data}]}
    """

    data = request.json

    photo = Photo.query.get_or_404(photo_id)

    photo.caption = data.get("caption", photo.caption)

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

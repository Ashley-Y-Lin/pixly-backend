from app import app
from models import db, Photo

db.drop_all()
db.create_all()

c1 = Photo(
    caption="dandelions",
    aws_s3="https://pixly-ashleylin.s3.amazonaws.com/dandelions.jpeg",
    file_name="dandelions.jpeg",
    exif_data={
        "Camera Make": "Canon",
        "Camera Model": "EOS 80D",
        "Exposure Time": "1/200 sec",
        "Aperture": "f/5.6",
        "ISO Speed": 200,
        "Focal Length": "50 mm",
    },
)

c2 = Photo(
    caption="strawberries",
    aws_s3="https://pixly-ashleylin.s3.amazonaws.com/strawberries.jpeg",
    file_name="strawberries.jpeg",
    exif_data={
        "Camera Make": "Nikon",
        "Camera Model": "D750",
        "Exposure Time": "1/1000 sec",
        "Aperture": "f/2.8",
        "ISO Speed": 400,
        "Focal Length": "35 mm",
    },
)

c3 = Photo(
    caption="tomatoes",
    aws_s3="https://pixly-ashleylin.s3.amazonaws.com/tomatoes.jpeg",
    file_name="tomatoes.jpeg",
    exif_data={
        "Camera Make": "Sony",
        "Camera Model": "Alpha A7 III",
        "Exposure Time": "1/500 sec",
        "Aperture": "f/4.0",
        "ISO Speed": 800,
        "Focal Length": "24 mm",
    },
)

db.session.add_all([c1, c2, c3])
db.session.commit()

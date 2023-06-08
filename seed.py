from app import app
from models import db, Photo

db.drop_all()
db.create_all()

# FIXME: fake aws_s3 and file_name right now!

c1 = Photo(
    caption="sunset",
    aws_s3="https://t4.ftcdn.net/jpg/01/04/78/75/360_F_104787586_63vz1PkylLEfSfZ08dqTnqJqlqdq0eXx.jpg",
    file_name="fake1",
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
    caption="bird",
    aws_s3="https://www.dpreview.com/files/p/articles/1852634480/_9959.jpeg",
    file_name="fake2",
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
    caption="elephants",
    aws_s3="https://i.natgeofe.com/n/2745c809-e54d-41e5-8391-06ab2ffcafc3/NationalGeographic_1422702.jpg",
    file_name="fake3",
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

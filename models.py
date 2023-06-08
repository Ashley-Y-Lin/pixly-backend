"""Models for Pix.ly app."""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Photo(db.Model):
    """Photo."""

    __tablename__ = "photos"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    caption = db.Column(db.String(200), nullable=False, default="")

    file_name = db.Column(db.String(200), nullable=False, default="")

    aws_s3 = db.Column(db.String(500), nullable=False)

    exif_data = db.Column(db.JSON, nullable=False, default={})

    def to_dict(self):
        """Serialize a photo to a dict of photo info."""

        return {
            "id": self.id,
            "caption": self.caption,
            "file_name": self.file_name,
            "aws_s3": self.aws_s3,
            "exif_data": self.exif_data,
        }


def connect_db(app):
    """Connect to database."""

    app.app_context().push()
    db.app = app
    db.init_app(app)

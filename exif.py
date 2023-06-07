from PIL import Image
from PIL.ExifTags import TAGS


def get_exif_data(file_object):
    """get_exif_data returns the EXIF metadata for an image.

    Takes as input a file_object (instance of FileStorage). Returns an object
    containing EXIF metadata fields that can be accessed.
    """

    image = Image.open(file_object)

    if hasattr(image, "exif"):
        exif_data = image._getexif()
        out_exif = {}

        if exif_data is not None:
            for tagid in exif_data:
                # getting the tag name instead of tag id
                tagname = TAGS.get(tagid, tagid)

                # passing the tagid to get its respective value
                value = exif_data.get(tagid)

                # add tagname and value to out_exif
                out_exif.tagname = value

        return out_exif

    else:
        print("No EXIF metadata found.")

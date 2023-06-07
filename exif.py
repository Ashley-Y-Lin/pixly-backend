from PIL import Image
from PIL.ExifTags import TAGS
from fractions import Fraction


def get_exif_data(file_object):
    """get_exif_data returns the EXIF metadata for an image.

    Takes as input a file_object (instance of FileStorage). Returns an object
    containing EXIF metadata fields that can be accessed.
    """
    image = Image.open(file_object)

    exif_data = image.getexif()

    out_exif = {}

    for tagid in exif_data:
        tagname = TAGS.get(tagid, tagid)
        value = exif_data.get(tagid)

        if isinstance(value, int) or isinstance(value, str):
            print(f"normal, value = {value}, type = {type(value)}")

        else:
            print(f"not normal, type = {type(value)}")

            if value.denominator == 0:
                value = int(value.numerator)
            else:
                value = int(value.numerator / value.denominator)
            print(f"not normal but changed, type = {type(value)}")

        out_exif[tagname] = value

    return out_exif

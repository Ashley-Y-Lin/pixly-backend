import boto3
import os
import dotenv

dotenv.load_dotenv()

S3_BUCKET = "pixly-ashleylin"
REGION = "us-east-1"

session = boto3.Session(
    aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.environ.get("AWS_SECRET_KEY"),
    region_name=REGION,
)

s3 = session.client("s3")


def upload_photo_s3(fileObject):
    try:
        response = s3.put_object(
            Bucket=S3_BUCKET,
            Key=fileObject.filename,
            Body=fileObject,
            ContentType=fileObject.content_type,
        )
        return f"https://{S3_BUCKET}.s3.{REGION}.amazonaws.com/{fileObject.filename}"
    except Exception as e:
        print(f"Error uploading file: {e}")
        return None


def remove_photo_s3(photo):
    print("remove photo is running")

    try:
        response = s3.delete_object(
            Bucket=S3_BUCKET,
            Key=photo.file_name,
        )
        return photo.file_name
    except Exception as e:
        print(f"Error removing file from S3: {e}")
        return None

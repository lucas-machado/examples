import os
import uuid
import boto3

BUCKET = os.getenv("AWS_S3_BUCKET")
REGION = os.getenv("AWS_S3_REGION", "us-east-1")

def get_client():
    return boto3.client(
        "s3",
        region_name=REGION,
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
    )


def upload_image(bytes_content: bytes, content_type: str, filename: str | None = None) -> str:
    ext = "jpg"
    if filename and "." in filename:
        ext = filename.rsplit(".", 1)[-1].lower()
    if content_type and "/" in content_type:
        ext = content_type.split("/")[-1].lower()
    key = f"moments/{uuid.uuid4()}.{ext}"
    client = get_client()
    client.put_object(
        Bucket=BUCKET,
        Key=key,
        Body=bytes_content,
        ContentType=content_type or "application/octet-stream",
    )
    return f"https://{BUCKET}.s3.{REGION}.amazonaws.com/{key}"

import os
import boto3
import uuid
from datetime import datetime
from dotenv import load_dotenv
 
# Load variables from .env file
load_dotenv()
 
# Set AWS credentials directly from environment variables
os.environ["AWS_ACCESS_KEY_ID"] = os.getenv("aws_access_key_id")
os.environ["AWS_SECRET_ACCESS_KEY"] = os.getenv("aws_secret_access_key")
os.environ["AWS_DEFAULT_REGION"] = os.getenv("region_name")
 
# Constants
BUCKET_NAME = os.getenv("s3_bucket_name")
S3_BASE_FOLDER = "uploads"
 
def upload_images(image_path):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    s3_folder = f"{S3_BASE_FOLDER}/"
    s3 = boto3.client('s3')
    image_name = os.path.basename(image_path)

    s3_key = s3_folder + f"uncompressed_{timestamp}_{str(uuid.uuid1())}_{image_name}"
    try:
        s3.upload_file(image_path, BUCKET_NAME, s3_key)
        region = os.getenv("region_name")
        s3_url = f"https://{BUCKET_NAME}.s3.{region}.amazonaws.com/{s3_key}"
        # print(f"Uploaded: {image_path} → {s3_url}")
        return s3_key, s3_url
    except Exception as e:
        print(f"Failed to upload {image_name}: {e}")

if __name__ == "__main__":
    s3_key, s3_url = upload_images("./testing images/debug/DJI_0485.JPG")
    print(s3_url)
            
 
 

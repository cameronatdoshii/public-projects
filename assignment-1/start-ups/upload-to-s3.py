import boto3
import json
import logging
import requests
import os
from contextlib import closing

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

def create_bucket(bucket_name, region=None):
    try:
        s3_client = boto3.client('s3', region_name=region) if region else boto3.client('s3')
        if region and region != 'us-east-1':
            s3_client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': region})
        else:
            s3_client.create_bucket(Bucket=bucket_name)
        logger.info(f"Created bucket {bucket_name} in region {region}")
    except Exception as e:
        logging.error(e)
        return False
    return True


def check_bucket_exists(bucket_name):
    s3 = boto3.resource('s3')
    try:
        s3.meta.client.head_bucket(Bucket=bucket_name)
        logger.info(f"Bucket {bucket_name} exists")
        return True
    except Exception as e:
        logger.error(f"Bucket {bucket_name} does not exist: {e}")
        return False

    
def check_file_exists(bucket_name, file_name):
    s3_client = boto3.client('s3')
    try:
        s3_client.head_object(Bucket=bucket_name, Key=file_name)
        return True  # The file exists
    except Exception as e:
        if e.response and e.response['Error']['Code'] == '404':
            return False  # The file does not exist
        else:
            raise  # Raise other exceptions



def download_images(bucket_name):
    s3 = boto3.client('s3')

    with open('a1.json') as file:
        music = json.load(file)["songs"]

    for song in music:
        img_url = song['img_url']
        response = requests.get(img_url, stream=True)

        if response.status_code == 200:
            file_location = f"images/{song['artist']}/{song['year']}/{song['title'].replace(' ', '_')}.jpg"
            
            # Create the directory if it doesn't exist
            os.makedirs(os.path.dirname(file_location), exist_ok=True)

            if not check_file_exists(bucket_name, file_location):
                with closing(response), open(file_location, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)

                with open(file_location, 'rb') as data:
                    s3.upload_fileobj(data, bucket_name, file_location)
                    logger.info(f"Uploaded {song['title']} image to S3")
            else:
                logger.info(f"File {file_location} already exists in S3")
        else:
            logger.error(f"Failed to download {song['title']} image from the web")

def main():
    bucket_name = 's3864826-a1-music-image-bucket'
    region = 'us-east-1'  # Specify your region
    if not check_bucket_exists(bucket_name):
        if create_bucket(bucket_name, region):
            logger.info(f"Bucket {bucket_name} created successfully.")
        else:
            logger.error(f"Failed to create bucket {bucket_name}.")
            return
    else:
        logger.info(f"Bucket {bucket_name} already exists.")

    download_images(bucket_name)


if __name__ == '__main__':
    main()

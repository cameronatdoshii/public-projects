import boto3
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

class s3_helper:
    def __init__(self, profile_name='default'):
        session = boto3.Session(profile_name=profile_name)
        self.s3_client = session.client('s3')
    
    def generate_presigned_url(self, bucket_name, object_name, expiration=604800):
        try:
            response = self.s3_client.generate_presigned_url('get_object',
                                                             Params={'Bucket': bucket_name,
                                                                     'Key': object_name},
                                                             ExpiresIn=expiration)
        except Exception as e:
            logger.error(e)
            return None
        return response

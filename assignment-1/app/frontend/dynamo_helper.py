import boto3
from boto3.dynamodb.conditions import Key, Attr
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

class dynamo_helper:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')

    def query_login(self, email, password, table_name):
        table = self.dynamodb.Table(table_name)
        response = table.get_item(Key={'email': email})

        if 'Item' in response and response['Item'].get('password') == password:
            return True, "Login Successful"
        return False, "Email or Password is Invalid"
    
    def add_user(self, email, user_name, password, table_name):
        table = self.dynamodb.Table(table_name)
        # Check if the user already exists
        existing_user = table.get_item(Key={'email': email})
        if 'Item' in existing_user:
            return False, {'error': 'the email already exists'}

        try:
            response = table.put_item(Item={'email': email, 'user_name': user_name, 'password': password})
            return True, {'success': 'user added successfully'}
        except Exception as e:
            return False, {'error': str(e)}


    def query_music(self, title=None, artist=None, year=None):
        logger.info(f"Querying music with title: {title}, artist: {artist}, year: {year}")
        
        filter_expression = None
        
        if title:
            filter_expression = Attr('title').eq(title) if not filter_expression else filter_expression & Attr('title').eq(title)
            logger.info(f"Filter expression: {filter_expression}")
        
        if artist:
            filter_expression = Attr('artist').eq(artist) if not filter_expression else filter_expression & Attr('artist').eq(artist)
            logger.info(f"Filter expression: {filter_expression}")
            
        if year:
            filter_expression = Attr('year').eq(year) if not filter_expression else filter_expression & Attr('year').eq(year)
            logger.info(f"Filter expression: {filter_expression}")
            
        if not filter_expression:
            logger.info("No filter expression is provided")
            return 'No result is retrieved. Please query again'
        
        try:
            table = self.dynamodb.Table('music')
            response = table.scan(FilterExpression=filter_expression)
            logger.info(f"Response: {response}")
            
            return response['Items']
        except Exception as e:
            logger.error(f"Error: {e}")
            
            return str(e)
        



# def main():
#     helper = dynamo_helper()
#     helper.query_music(title='40oz to Freedom')
#     helper.query_music(artist='Sublime')
#     helper.query_music(year='1997')
#     helper.query_music(title='40oz to Freedom', artist='Sublime')
#     helper.query_music(title='40oz to Freedom', year='1996')
#     helper.query_music(artist='Sublime', year='1996')
#     helper.query_music(title='40oz to Freedom', artist='Sublime', year='1996')
#     helper.query_music(title='40oz to Freedom', artist='Sublime', year='1995')
    
# if __name__ == '__main__':
#     main()
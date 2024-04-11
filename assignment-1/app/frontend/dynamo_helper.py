import boto3
from boto3.dynamodb.conditions import Key, Attr
import logging
import ast
import json

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

class dynamo_helper:
    def __init__(self, profile_name='default'):
        session = boto3.Session(profile_name=profile_name)
        self.dynamodb = session.resource('dynamodb')

    def query_login(self, email, password, table_name):
        table = self.dynamodb.Table(table_name)
        response = table.get_item(Key={'email': email})

        if 'Item' in response and response['Item'].get('password') == password:
            return True, "Login Successful", response['Item']['user_name']
        return False, "Email or Password is Invalid", None
    
    def add_user(self, email, user_name, password, table_name):
        table = self.dynamodb.Table(table_name)
        # Check if the user already exists
        existing_user = table.get_item(Key={'email': email})
        if 'Item' in existing_user:
            return False, {'error': 'the email already exists'}

        try:
            response = table.put_item(Item={'email': email, 'user_name': user_name, 'password': password, 'subbed_music': '[]'})
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
        
    def remove_subbed_music(self, title, artist, year, email):
        table = self.dynamodb.Table('login')
        response = table.get_item(Key={'email': email})
        logger.info(f"Response: {response}")
        
        # Parse the string into a list of dictionaries (assuming subbed_music is stored as a string).
        current_music = ast.literal_eval(response['Item']['subbed_music'])

        # Update the condition to correctly identify the item to remove
        current_music = [
            m for m in current_music 
            if not (m['Title'] == title and m['Artist'] == artist and m['Year'] == year)
        ]

        # Convert the list back to a string to store in DynamoDB
        music_str = json.dumps(current_music)

        response = table.update_item(
            Key={'email': email},
            UpdateExpression='SET subbed_music = :val1',
            ExpressionAttributeValues={':val1': music_str}
        )
        return current_music

        
    def get_subbed_music(self, email):
        table = self.dynamodb.Table('login')
        response = table.get_item(Key={'email': email})
        logger.info(f"Response: {response}")
        return ast.literal_eval(response['Item']['subbed_music'])
        
    def add_subbed_music(self, new_subbed, email):
        
        logger.info(f"Adding subbed music: {new_subbed} for email: {email}")
        
        try:
            table = self.dynamodb.Table('login')
            current_results = table.get_item(Key={'email': email})
            current_music = current_results['Item']['subbed_music']
            current_music = ast.literal_eval(current_music)
            new_music = new_subbed['subbed_music']
            
            # Convert list of dictionaries to a list of tuples for comparison
            existing_music_set = {tuple(music.items()) for music in current_music}

            # Add new music if it's not already in the set
            for music in new_music:
                if tuple(music.items()) not in existing_music_set:
                    current_music.append(music)

            response = table.update_item(
                Key={'email': email},
                UpdateExpression='SET subbed_music = :val1',
                ExpressionAttributeValues={':val1': str(current_music)}
            )
            return current_music
        except Exception as e:
            logger.error(f"Error: {e}")
            return False, {'error': str(e)}




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
#     helper.add_subbed_music({'subbed_music': [{'Title': 'Darkness Between the Fireflies', 'Artist': 'Mason Jennings', 'Year': '1997', 'ImagePath': 'https://raw.githubusercontent.com/davidpots/songnotes_cms/master/public/images/artists/MasonJennings.jpg'}, {'Title': 'Nothing', 'Artist': 'Mason Jennings', 'Year': '1997', 'ImagePath': 'https://raw.githubusercontent.com/davidpots/songnotes_cms/master/public/images/artists/MasonJennings.jpg'}, {'Title': 'Karma Police', 'Artist': 'Radiohead', 'Year': '1997', 'ImagePath': 'https://raw.githubusercontent.com/davidpots/songnotes_cms/master/public/images/artists/Radiohead.jpg'}, {'Title': 'No Surprises', 'Artist': 'Radiohead', 'Year': '1997', 'ImagePath': 'https://raw.githubusercontent.com/davidpots/songnotes_cms/master/public/images/artists/Radiohead.jpg'}]}, "cameron@thegilmours.co.za")
#   helper.get_subbed_music("cameron@thegilmours.co.za")


# if __name__ == '__main__':
#     main()

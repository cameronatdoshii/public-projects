import boto3
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)


def check_exists(table_name):

    dynamodb = boto3.resource('dynamodb')

    try:
        table = dynamodb.Table(table_name)
        table.load()
        logger.info(f"Table {table_name} exists")
        return True
    except Exception as e:
        logger.error(f"Table {table_name} does not exist: {e}")
        return False


def create_table(table_name):

    dynamodb = boto3.resource('dynamodb')

    table_attributes = [
        {
            'AttributeName': 'email',
            'AttributeType': 'S'
        }
    ]

    key_shema = [
        {
            'AttributeName': 'email',
            'KeyType': 'HASH'
        }
    ]

    provisioned_throughput = {
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5
    }

    table = dynamodb.create_table(
        TableName=table_name,
        KeySchema=key_shema,
        AttributeDefinitions=table_attributes,
        ProvisionedThroughput=provisioned_throughput
    )

    try:
        table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
        logger.info("Table created successfully")
        return True
    except Exception as e:
        logger.error(f"Table creation failed: {e}")
        return False


def load_data(table_name):

    dynamodb = boto3.resource('dynamodb')

    table = dynamodb.Table(table_name)

    base_email_prefix = 's3864826'
    base_email_suffix = '@student.rmit.edu.au'

    user_name = 'Cameron Gilmour'

    password = 'CoolPassWord'

    data = {
        'email': None,
        'user_name': None,
        'password': None
    }

    for i in range(0, 9):
        email = f"{base_email_prefix}{i}{base_email_suffix}"
        data['email'] = email
        data['user_name'] = user_name + str(i)
        data['password'] = password + str(i)
        try:
            table.put_item(Item=data)
            logger.info(f"Data loaded successfully for {email}")
        except Exception as e:
            logger.error(f"Data load failed for {email}: {e}")


def main():
    table_name = 'login'
    if not check_exists(table_name):
        create_table(table_name)
        load_data(table_name)
    else:
        logger.info(f"Table {table_name} already exists")


if __name__ == '__main__':
    main()


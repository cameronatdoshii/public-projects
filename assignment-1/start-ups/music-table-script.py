import boto3
import json
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
            'AttributeName': 'title',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'artist',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'year',
            'AttributeType': 'S'
        }
    ]

    key_schema = [
        {
            'AttributeName': 'artist',
            'KeyType': 'HASH'
        },
        {
            'AttributeName': 'title',
            'KeyType': 'RANGE'
        }
    ]

    gsi = [
        {
            'IndexName': 'YearIndex',
            'KeySchema': [
                {
                    'AttributeName': 'year',
                    'KeyType': 'HASH'
                }
            ],
            'Projection': {
                'ProjectionType': 'ALL'
            },
            'ProvisionedThroughput': {
                'ReadCapacityUnits': 10,
                'WriteCapacityUnits': 10
            }
        }
    ]

    provisioned_throughput = {
        'ReadCapacityUnits': 10,
        'WriteCapacityUnits': 10
    }

    try:
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=key_schema,
            AttributeDefinitions=table_attributes,
            ProvisionedThroughput=provisioned_throughput,
            GlobalSecondaryIndexes=gsi
        )

        table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
        logger.info("Table created successfully")
        return True
    except Exception as e:
        logger.error(f"Table creation failed: {e}")
        return False


def load_data(table_name):

    dynamodb = boto3.resource('dynamodb')

    table = dynamodb.Table(table_name)

    with open('a1.json', 'r') as file:
        try:
            music = json.load(file)
            for song in music['songs']:
                table.put_item(Item=song)
            logger.info("Data loaded successfully")
        except Exception as e:
            logger.error(f"Data loading failed: {e}")


def main():
    table_name = 'music'
    if not check_exists(table_name):
        create_table(table_name)
        load_data(table_name)
    else:
        logger.info(f"Table {table_name} already exists")


if __name__ == '__main__':
    main()


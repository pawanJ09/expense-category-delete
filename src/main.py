from boto3 import resource
from botocore.exceptions import ClientError
import json
import os

resource = resource('dynamodb', region_name='us-east-2')
table = resource.Table('expense-categories')


def lambda_handler(event, context):
    try:
        print(f'Incoming event: {event}')
        event_http_method = event['requestContext']['http']['method']
        print(f'Incoming API Gateway HTTP Method: {event_http_method}')
        event_path = event['requestContext']['http']['path']
        print(f'Incoming API Gateway Path: {event_path}')
        try:
            query_string = event['rawQueryString']
            print(f'Incoming API Gateway Query String: {query_string}')
            req_category = query_string.split('=')[1]
            if req_category:
                table.delete_item(Key={
                    'category': req_category
                })
                print('Returning successful response')
                msg = {"message": f"{req_category} category successfully added."}
                return {
                    "statusCode": 204,
                    "headers": {"content-type": "application/json"},
                    "body": json.dumps(msg)
                }
            else:
                msg = {"message": "category query param not provided."}
                return {
                    "statusCode": 400,
                    "headers": {"content-type": "application/json"},
                    "body": json.dumps(msg)
                }
        except KeyError as ke:
            msg = {"message": "category query param not provided."}
            return {
                "statusCode": 400,
                "headers": {"content-type": "application/json"},
                "body": json.dumps(msg)
            }
    except (Exception, ClientError) as e:
        msg = e.response['Error']['Message']
        print(f'Exception caught: {msg}')
        return {
            "statusCode": 500,
            "headers": {"content-type": "application/json"},
            "body": json.dumps(msg)
        }


if __name__ == '__main__':
    script_dir = os.path.dirname(__file__)
    rel_path = '../events/test-agw-event.json'
    abs_file_path = os.path.join(script_dir, rel_path)
    with open(abs_file_path) as f:
        test_event = json.load(f)
        lambda_handler(test_event, None)
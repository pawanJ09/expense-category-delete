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
        body = event['body']
        print(f'Incoming API Gateway Body: {body}')
        req = json.loads(body)
        if req['category']:
            try:
                table_item = table.get_item(Key={'category': req['category']})
                if table_item['Item']:
                    msg = {"message": f"{req['category']} category already exists."}
                    print(f'Exception caught: {msg}')
                    return {
                        "statusCode": 400,
                        "headers": {"content-type": "application/json"},
                        "body": json.dumps(msg)
                    }
            except KeyError as ke:
                print(f'{req["category"]} not found in table. Now adding.')
            vals = list()
            try:
                vals.extend(req['val'])
            except KeyError as ke:
                # If existing request has no vals then handle gracefully and still add the
                # category
                print(f'Request has no val')
            # Converting to set and back to list to remove duplicates
            vals_list = list(set(vals))
            response = table.put_item(Item={
                'category': req['category'],
                'val': vals_list
            })
            print('Returning successful response')
            msg = {"message": f"{req['category']} category successfully added."}
            return {
                "statusCode": 201,
                "headers": {"content-type": "application/json"},
                "body": json.dumps(msg)
            }

    except (AttributeError, KeyError) as er:
        msg = {"message": "Category not defined in the request."}
        print(f'Exception caught: {msg}')
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
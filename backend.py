import base64
import json
import os.path
import time
from datetime import datetime
from typing import Optional

import boto3
from pydantic import BaseModel, Field
from werkzeug.utils import secure_filename

S3_BUCKET = "location-finder-data-bucket"
very_secret_password = "VerySecretP@ssword69"

os.environ['TZ'] = 'Europe/Amsterdam'
time.tzset()

class LocationData(BaseModel):
    lat: float
    lon: float
    name: str
    team: str
    browser_info: str
    date: datetime = Field(default_factory=datetime.now)
    qr_id: Optional[str] = None


def iterate_bucket_items():
    """
    Generator that iterates over all objects in a given s3 bucket

    See http://boto3.readthedocs.io/en/latest/reference/services/s3.html#S3.Client.list_objects_v2
    for return data format
    :param bucket: name of s3 bucket
    :return: dict of metadata for an object
    """

    client = boto3.client('s3')
    paginator = client.get_paginator('list_objects_v2')
    page_iterator = paginator.paginate(Bucket=S3_BUCKET)

    for page in page_iterator:
        if page['KeyCount'] > 0:
            for item in page['Contents']:
                yield item['Key']


def get_html(file):
    with open(file, 'r') as f:
        return {
            "statusCode": 200,
            "body": f.read(),
            "headers": {
                'Content-Type': 'text/html',
            }
        }

def get_css(file):
    with open(file, 'r') as f:
        return {
            "statusCode": 200,
            "body": f.read(),
            "headers": {
                'Content-Type': 'text/css',
            }
        }


def get_image(file, image_type='png'):
    with open(file, 'rb') as f:
        return {
            "statusCode": 200,
            "body": base64.b64encode(f.read()),
            "isBase64Encoded": True,
            "headers": {
                'Content-Type': f'image/{image_type}',
            }
        }


def response_404():
    return {
        "statusCode": 404,
        "body": "Not found"
    }


def response_401():
    return {
        "statusCode": 401,
        "body": "Wrong password"
    }


def handler(event, context):
    try:
        method = event['requestContext']['http']['method']
        path = event['requestContext']['http']['path']
        headers = event['headers']
        print(f"method: {method}, path: {path}")
        if method == 'GET' and path == '/ping':
            return ping()
        elif method == 'POST' and path == '/location':
            return store_location(LocationData.parse_raw(event.get('body')))
        elif method == 'GET' and path == '/location':
            if headers.get('password') != very_secret_password:
                return response_401()
            return get_location()
        if method == 'GET' and path == '/':
            return get_html('index.html')
        if method == 'GET' and path == '/admin':
            return get_html('admin.html')
        elif method == 'GET' and path.startswith('/resources/'):
            if not os.path.isfile(path[1:]):
                return response_404()
            if path.endswith('.png'):
                return get_image(path[1:], 'png')
            elif path.endswith('.jpg') or path.endswith('.jpeg'):
                return get_image(path[1:], 'jpg')
            elif path.endswith('.svg'):
                return get_image(path[1:], 'svg+xml')
            elif path.endswith('.css'):
                return get_css(path[1:])
            else:
                return response_404()
        else:
            return response_404()
    except Exception as e:
        print(e)
        raise e


def ping():
    return "online"


def store_location(location_data: LocationData):
    s3_client = boto3.client('s3')

    s3_client.put_object(Bucket=S3_BUCKET,
                         Key=f'{secure_filename(location_data.team)}/{secure_filename(location_data.name)}/location.json',
                         Body=location_data.json())
    return "ok"


def get_location():
    client = boto3.client('s3')
    data = []
    for item in iterate_bucket_items():
        for version in client.list_object_versions(Bucket=S3_BUCKET, Prefix=item)['Versions']:
            obj = client.get_object(Bucket=S3_BUCKET, Key=item, VersionId=version['VersionId'])
            data.append(json.loads(obj['Body'].read()))

    data.sort(key=lambda x: x['date'], reverse=True)

    return data

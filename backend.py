import json
from datetime import datetime

import boto3
from pydantic import BaseModel
from werkzeug.utils import secure_filename

S3_BUCKET = "location-finder-data-bucket"

class DefaultInput(BaseModel):
    command: str


class LocationData(DefaultInput):
    lat: float
    lon: float
    name: str
    team: str
    browser_info: str
    date: datetime = datetime.now()


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


def handler(event, context):
    print(event)


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
        obj = client.get_object(Bucket=S3_BUCKET, Key=item)
        data.append(json.loads(obj['Body'].read()))

    return data

import pytest
import boto3
from services.config import AWS_ENDPOINT_URL, AWS_REGION, SHIPPING_QUEUE, SHIPPING_TABLE_NAME

@pytest.fixture(scope="module")
def dynamo_resource():
    return boto3.resource(
        "dynamodb",
        endpoint_url=AWS_ENDPOINT_URL,
        region_name=AWS_REGION,
        aws_access_key_id="test",
        aws_secret_access_key="test",
    )

@pytest.fixture(scope="module")
def sqs_client():
    return boto3.client(
        "sqs",
        endpoint_url=AWS_ENDPOINT_URL,
        region_name=AWS_REGION,
        aws_access_key_id="test",
        aws_secret_access_key="test",
    )

#Створення запису
def test_create_item(dynamo_resource):
    table = dynamo_resource.Table(SHIPPING_TABLE_NAME)
    table.put_item(Item={"shipping_id": "22", "type": "standard"})
    result = table.get_item(Key={"shipping_id": "22"})
    assert "Item" in result

#Перегляд існуючого запису
def test_read_item(dynamo_resource):
    table = dynamo_resource.Table(SHIPPING_TABLE_NAME)
    table.put_item(Item={"shipping_id": "22", "type": "express"})
    result = table.get_item(Key={"shipping_id": "22"})
    assert result["Item"]["type"] == "express"

#Перегляд неіснуючого запису
def test_read_nonexistent_item(dynamo_resource):
    table = dynamo_resource.Table(SHIPPING_TABLE_NAME)
    result = table.get_item(Key={"shipping_id": "999"})
    assert "Item" not in result

def test_send_sqs_message(sqs_client):
    queue_url = sqs_client.get_queue_url(QueueName=SHIPPING_QUEUE)["QueueUrl"]
    resp = sqs_client.send_message(QueueUrl=queue_url, MessageBody="Hello")
    assert "MessageId" in resp

def test_receive_sqs_message(sqs_client):
    queue_url = sqs_client.get_queue_url(QueueName=SHIPPING_QUEUE)["QueueUrl"]
    sqs_client.send_message(QueueUrl=queue_url, MessageBody="Test")
    messages = sqs_client.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=1)
    assert "Messages" in messages

def test_update_item(dynamo_resource):
    table = dynamo_resource.Table(SHIPPING_TABLE_NAME)
    table.put_item(Item={"shipping_id": "3", "type": "standard"})
    table.update_item(Key={"shipping_id": "3"}, UpdateExpression="SET #t=:val", ExpressionAttributeNames={"#t": "type"}, ExpressionAttributeValues={":val": "express"})
    result = table.get_item(Key={"shipping_id": "3"})
    assert result["Item"]["type"] == "express"

def test_delete_item(dynamo_resource):
    table = dynamo_resource.Table(SHIPPING_TABLE_NAME)
    table.put_item(Item={"shipping_id": "22", "type": "standard"})
    table.delete_item(Key={"shipping_id": "22"})
    result = table.get_item(Key={"shipping_id": "22"})
    assert "Item" not in result

def test_send_multiple_messages(sqs_client):
    queue_url = sqs_client.get_queue_url(QueueName=SHIPPING_QUEUE)["QueueUrl"]
    for i in range(10):
        sqs_client.send_message(QueueUrl=queue_url, MessageBody=f"msg{i}")
    messages = sqs_client.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=3)
    assert len(messages.get("Messages", [])) >= 1

def test_dynamo_sqs_integration(dynamo_resource, sqs_client):
    table = dynamo_resource.Table(SHIPPING_TABLE_NAME)
    table.put_item(Item={"shipping_id": "5", "type": "express"})
    queue_url = sqs_client.get_queue_url(QueueName=SHIPPING_QUEUE)["QueueUrl"]
    sqs_client.send_message(QueueUrl=queue_url, MessageBody="order5")
    result = table.get_item(Key={"shipping_id": "5"})
    messages = sqs_client.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=1)
    assert "Item" in result and "Messages" in messages
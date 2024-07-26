from flask import Flask, jsonify
import boto3
import time

app = Flask(__name__)

dynamodb = boto3.resource(
    'dynamodb',
    region_name='us-east-1',
    endpoint_url='http://host.docker.internal:8000'
)

table = dynamodb.Table('api-pos-pago')


def calculate_ttl(days=30):
    return int(time.time()) + days * 86400


@app.route('/add-item')
def add_item():
    item = {
        'id': '123',
        'data': 'ejemplo',
        'ttl': calculate_ttl(30)
    }
    table.put_item(Item=item)
    return jsonify({'message': 'Item added', 'item': item})


@app.route('/items')
def list_items():
    response = table.scan()
    return jsonify(response['Items'])


if __name__ == '__main__':
    app.run(host='0.0.0.0')

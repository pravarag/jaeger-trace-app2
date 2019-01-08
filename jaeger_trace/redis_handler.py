from flask import Flask
from flask import request
import redis
from tracer import init_tracer
from tracer import init_tracer
from opentracing.ext import tags
from opentracing.propagation import Format
import requests
import os
from flask import jsonify
from random import randint


listen = ['default']

app=Flask(__name__)
tracer = init_tracer('redis-handler')
redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_port = os.getenv('REDIS_PORT', '6379')

conn_redis = redis.StrictRedis(host=redis_host, port=int(redis_port), db=0)
#conn_redis = redis.StrictRedis(host='localhost', port=6379, db=0)

@app.route('/db')
def redis_handler():
	span_ctx = tracer.extract(Format.HTTP_HEADERS, request.headers)
	span_tags = {tags.SPAN_KIND: tags.SPAN_KIND_RPC_SERVER}
	with tracer.start_active_span('redis-handler-span', child_of=span_ctx, tags=span_tags):
		span = tracer.active_span
		print(request.headers)
		print(request.headers.get('Delivery-Guy'))
		food_item = request.headers.get('Order-Item')
		conn_redis.set('Order-Item', str(food_item))
		order_id = randint(0, 50)

		conn_redis.set('Order-Id', str(order_id))
		span.set_tag('Order-Id', order_id)

		return "Your order-id is "+str(order_id)

# @app.route('/createhash')
# def call_redis_display():
# 	span_ctx = tracer.extract(Format.HTTP_HEADERS, request.headers)
# 	span_tags = {tags.SPAN_KIND: tags.SPAN_KIND_RPC_SERVER}
# 	with tracer.start_active_span('redis-handler-createhash', child_of=span_ctx, tags=span_tags):
# 		order_id = request.headers.get('Order-Id')
# 		print(order_id)

# 		# create hset
# 		delv_guy = conn_redis.get('Delivery_Guy')
# 		order_item = conn_redis.get('Order-Item')
# 		conn_redis.hset('Order1', 'Order-Id', order_id)
# 		conn_redis.hset('Order1', 'Delivery_Guy', delv_guy)
# 		conn_redis.hset('Order1', 'Order-Item', order_item)


# 		url = 'http://localhost:8083/'
# 		span = tracer.active_span
# 		span.set_tag(tags.HTTP_METHOD, 'GET')
# 		span.set_tag(tags.HTTP_URL, url)
# 		span.set_tag(tags.SPAN_KIND, tags.SPAN_KIND_RPC_SERVER)
# 		headers = {'Order-Id':order_id}
# 		tracer.inject(span, Format.HTTP_HEADERS, headers)
# 		r = requests.get(url, headers)


if __name__ == "__main__":
	app.run(port=8082)
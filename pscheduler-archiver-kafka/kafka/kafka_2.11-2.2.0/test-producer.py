#!/usr/bin/python

from kafka import KafkaProducer

producer = KafkaProducer(bootstrap_servers='10.0.0.10:9092')
producer.send('test', b'a python test message').get(timeout=30)

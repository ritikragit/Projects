from kafka import KafkaProducer
import json
import time
import random
import uuid
from config import KAFKA_BOOTSTRAP, TOPIC, BUFFER_FILE

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    acks="all",
    retries=5
)


def generate_transaction():
    return {
        "transaction_id": str(uuid.uuid4()),
        "card_id": random.randint(1000, 1010),
        "amount": round(random.uniform(10, 1000), 2),
        "timestamp": int(time.time() * 1000)
    }


def buffer_event(event):
    with open(BUFFER_FILE, "a") as f:
        f.write(json.dumps(event) + "\n")


while True:
    tx = generate_transaction()
    try:
        producer.send(TOPIC, key=str(tx["card_id"]).encode(), value=tx)
        producer.flush()
        print("Sent:", tx)
    except Exception as e:
        print("Kafka down, buffering:", e)
        buffer_event(tx)

    time.sleep(1)

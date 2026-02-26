import os

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "localhost:9092")
TOPIC = "transactions_raw"
BUFFER_FILE = "buffer.jsonl"

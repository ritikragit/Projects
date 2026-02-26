# open-streaming-lakehouse-platform

This project is a **Stage-0 streaming scaffold**: a local Kafka broker + a Python producer that generates events and falls back to a local buffer when Kafka is unavailable.

## Final structure

```text
open-streaming-lakehouse-platform/
├── docker/
│   └── docker-compose.yml
├── services/
│   ├── producer/
│   │   ├── producer.py
│   │   ├── config.py
│   │   └── requirements.txt
│   └── consumer/
│       └── requirements.txt
├── configs/
├── scripts/
├── .env
├── .gitignore
├── README.md
└── Makefile
```

## Quick start

1. Start Kafka:
   ```bash
   docker compose -f docker/docker-compose.yml up -d
   ```
2. Install producer dependencies:
   ```bash
   pip install -r services/producer/requirements.txt
   ```
3. Run producer:
   ```bash
   python services/producer/producer.py
   ```

## Failure test

While the producer is running, stop Kafka:

```bash
docker stop kafka
```

Expected behavior:
- terminal prints `Kafka down, buffering: ...`
- `buffer.jsonl` appears at project root

---

## Line-by-line explainer (why each line exists)

Below is a practical explanation for every line in each Stage-0 file.

### 1) `.gitignore`

```gitignore
__pycache__/
*.pyc
.env
venv/
.idea/
.DS_Store
buffer.jsonl
```

- `__pycache__/`: excludes Python bytecode cache folders generated at runtime.
- `*.pyc`: excludes compiled Python artifacts.
- `.env`: keeps machine-local secrets/config out of git history.
- `venv/`: excludes local virtual environment packages.
- `.idea/`: excludes IDE-specific project settings.
- `.DS_Store`: excludes macOS finder metadata.
- `buffer.jsonl`: excludes runtime failure-buffer data from version control.

### 2) `.env`

```env
KAFKA_BOOTSTRAP=localhost:9092

KAFKA_CFG_NODE_ID=1
KAFKA_CFG_PROCESS_ROLES=broker,controller
KAFKA_CFG_CONTROLLER_QUORUM_VOTERS=1@kafka:9093
KAFKA_CFG_LISTENERS=PLAINTEXT://:9092,CONTROLLER://:9093
KAFKA_CFG_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092
KAFKA_CFG_CONTROLLER_LISTENER_NAMES=CONTROLLER
ALLOW_PLAINTEXT_LISTENER=yes
```

- `KAFKA_BOOTSTRAP=localhost:9092`: gives clients the broker endpoint from host machine.
- blank line: separates app-level variable from broker internals for readability.
- `KAFKA_CFG_NODE_ID=1`: sets broker node ID.
- `KAFKA_CFG_PROCESS_ROLES=broker,controller`: runs single-node KRaft broker+controller.
- `KAFKA_CFG_CONTROLLER_QUORUM_VOTERS=1@kafka:9093`: defines controller quorum for node 1.
- `KAFKA_CFG_LISTENERS=...`: opens broker and controller listener ports inside container.
- `KAFKA_CFG_ADVERTISED_LISTENERS=...`: tells clients how to reach broker from host.
- `KAFKA_CFG_CONTROLLER_LISTENER_NAMES=CONTROLLER`: marks the controller listener name.
- `ALLOW_PLAINTEXT_LISTENER=yes`: allows plaintext mode for local/dev simplicity.

### 3) `docker/docker-compose.yml`

```yaml
version: '3.8'

services:
  kafka:
    image: bitnami/kafka:latest
    container_name: kafka
    ports:
      - "9092:9092"
    env_file:
      - ../.env
```

- `version: '3.8'`: selects compose schema version.
- blank line: visual separation of top-level keys.
- `services:`: starts service declarations.
- `kafka:`: names the service.
- `image: bitnami/kafka:latest`: uses maintained Kafka image.
- `container_name: kafka`: stable local container name for commands (`docker stop kafka`).
- `ports:`: declares host/container port mappings.
- `- "9092:9092"`: exposes broker port to host.
- `env_file:`: imports environment variables.
- `- ../.env`: loads root `.env` from `docker/` directory context.

### 4) `services/producer/config.py`

```python
import os

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "localhost:9092")
TOPIC = "transactions_raw"
BUFFER_FILE = "buffer.jsonl"
```

- `import os`: needed to read environment variables.
- blank line: separates imports from constants.
- `KAFKA_BOOTSTRAP = ...`: allows configurable broker endpoint with safe default.
- `TOPIC = ...`: central topic name constant for consistency.
- `BUFFER_FILE = ...`: central file path for offline buffering.

### 5) `services/producer/producer.py`

```python
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
```

- `from kafka import KafkaProducer`: imports Kafka client producer class.
- `import json`: serializes events and buffered lines.
- `import time`: adds timestamps and pacing.
- `import random`: produces synthetic test data.
- `import uuid`: creates unique transaction IDs.
- `from config ...`: reuses centralized settings.
- blank line: separates imports from object construction.
- `producer = KafkaProducer(`: initializes reusable producer instance.
- `bootstrap_servers=...`: points producer to Kafka endpoint.
- `value_serializer=...`: forces JSON bytes payloads.
- `acks="all"`: waits for strongest broker acknowledgment.
- `retries=5`: retries transient failures.
- `)`: closes producer config.
- blank lines: standard function spacing.
- `def generate_transaction():`: encapsulates event generation logic.
- `return {`: returns one event payload.
- `"transaction_id": ...`: sets globally unique transaction ID.
- `"card_id": ...`: simulates card/account identifier.
- `"amount": ...`: simulates realistic decimal amount.
- `"timestamp": ...`: includes event time in epoch milliseconds.
- `}`: closes payload dict.
- blank lines: separate functions.
- `def buffer_event(event):`: helper to persist unsent event.
- `with open(..., "a") as f:`: appends safely without overwriting history.
- `f.write(...)`: writes one JSON line per event.
- blank lines: separate helper from main loop.
- `while True:`: runs continuous stream generation.
- `tx = generate_transaction()`: creates one synthetic event.
- `try:`: attempts primary send path.
- `producer.send(...)`: sends event to Kafka topic with key.
- `producer.flush()`: forces immediate send (useful in simple demos).
- `print("Sent:", tx)`: visible success log.
- `except Exception as e:`: catches broker/network/runtime send errors.
- `print("Kafka down, buffering:", e)`: visible failure-mode log.
- `buffer_event(tx)`: preserves data when broker is unavailable.
- blank line: loop readability.
- `time.sleep(1)`: emits one event per second to control rate.

### 6) `services/producer/requirements.txt`

```txt
kafka-python
```

- `kafka-python`: installs Python Kafka client used by producer.

### 7) `services/consumer/requirements.txt`

```txt
# consumer dependencies
```

- `# consumer dependencies`: placeholder file to reserve consumer service location.

### 8) `Makefile`

```make
.PHONY: kafka-up kafka-down producer deps

kafka-up:
	docker compose -f docker/docker-compose.yml up -d

kafka-down:
	docker compose -f docker/docker-compose.yml down

deps:
	pip install -r services/producer/requirements.txt

producer:
	python services/producer/producer.py
```

- `.PHONY ...`: marks targets as command aliases, not file outputs.
- blank line: readability.
- `kafka-up:`: declares start target.
- `docker compose ... up -d`: starts Kafka in background.
- blank line: readability.
- `kafka-down:`: declares stop target.
- `docker compose ... down`: stops/removes compose resources.
- blank line: readability.
- `deps:`: declares dependency install target.
- `pip install ...`: installs producer dependencies.
- blank line: readability.
- `producer:`: declares producer run target.
- `python ... producer.py`: starts producer script.

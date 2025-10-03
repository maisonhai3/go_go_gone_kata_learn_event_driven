# Redis Streams Event Broker

This is an upgraded version of the event-driven architecture using **Redis Streams** for persistent, reliable event handling.

## 🚀 Features

- ✅ **Persistent Events**: All events are stored in Redis and survive application restarts
- ✅ **Event Replay**: Replay historical events from any point in time
- ✅ **Consumer Groups**: Reliable message processing with acknowledgment
- ✅ **Event History**: Query past events for debugging or auditing
- ✅ **Automatic Reconnection**: Resilient to Redis connection issues
- ✅ **Thread-Safe**: Concurrent event processing

## 📋 Prerequisites

- Python 3.8+
- Docker and Docker Compose (for Redis)

## 🔧 Setup

### 1. Start Redis

```bash
# Start Redis in Docker
docker-compose up -d

# Check Redis is running
docker-compose ps

# View Redis logs
docker-compose logs -f redis
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

## 🎯 Usage

### Running the Main Application

```bash
# Run with Redis Streams
python main_redis.py
```

### Event Replay Example

```bash
# Replay historical events
python example_replay.py
```

## 📊 Key Differences from In-Memory Broker

| Feature | In-Memory Broker | Redis Streams Broker |
|---------|-----------------|---------------------|
| Persistence | ❌ No | ✅ Yes |
| Event Replay | ❌ No | ✅ Yes |
| Event History | ❌ No | ✅ Yes |
| Survives Restart | ❌ No | ✅ Yes |
| Distributed | ❌ No | ✅ Yes |
| Consumer Groups | ❌ No | ✅ Yes |

## 🔍 Event Stream Operations

### View Event History

```python
from redis_event_broker import broker

# Get last 10 events
history = broker.get_event_history("AuctionEnded", count=10)
for event in history:
    print(f"ID: {event['id']}, Data: {event['data']}")
```

### Replay Events

```python
# Replay all events from the beginning
broker.replay_events("AuctionEnded", from_id='0')

# Replay from specific event ID
broker.replay_events("AuctionEnded", from_id='1696320000000-0', count=5)
```

### Stream Information

```python
info = broker.get_stream_info("AuctionEnded")
print(f"Total events: {info['length']}")
```

## 🐳 Docker Commands

```bash
# Start Redis
docker-compose up -d

# Stop Redis
docker-compose down

# Stop and remove data
docker-compose down -v

# View logs
docker-compose logs -f redis

# Access Redis CLI
docker exec -it event_broker_redis redis-cli
```

## 🔧 Redis CLI Useful Commands

```bash
# Connect to Redis
docker exec -it event_broker_redis redis-cli

# List all streams
KEYS events:*

# View stream info
XINFO STREAM events:AuctionEnded

# View stream content
XRANGE events:AuctionEnded - +

# View consumer groups
XINFO GROUPS events:AuctionEnded

# View pending messages
XPENDING events:AuctionEnded default
```

## 📈 Architecture Benefits

1. **Durability**: Events are persisted to disk (AOF enabled)
2. **Scalability**: Can add more consumers to process events in parallel
3. **Debugging**: Can replay events to reproduce bugs
4. **Auditing**: Complete history of all events
5. **Reliability**: Consumer groups ensure messages are processed at least once

## 🎓 Learning Points

- Redis Streams provide a powerful pub/sub + persistence model
- Consumer groups enable reliable, distributed event processing
- Event sourcing becomes possible with complete event history
- You can rebuild application state by replaying events

## 🔄 Migration from In-Memory Broker

The Redis broker maintains the same API as the in-memory broker:

```python
# Old way (in-memory)
from event_broker import broker

# New way (Redis Streams)
from redis_event_broker import broker

# Same API!
broker.subscribe("EventType", handler)
broker.publish("EventType", data)
```

## 🚨 Troubleshooting

**Redis connection failed?**
```bash
# Check if Redis is running
docker-compose ps

# Restart Redis
docker-compose restart redis
```

**Events not being consumed?**
- Check that consumer threads are started (happens automatically on subscribe)
- Verify Redis stream exists: `docker exec -it event_broker_redis redis-cli KEYS events:*`

**Need to reset everything?**
```bash
# Stop and remove all data
docker-compose down -v

# Start fresh
docker-compose up -d
```

## 📚 Next Steps

- Explore dead letter queues for failed messages
- Add event versioning for schema evolution
- Implement event snapshots for faster state rebuilding
- Add monitoring and metrics (Redis slow log, stream length)
- Scale horizontally with multiple consumer instances

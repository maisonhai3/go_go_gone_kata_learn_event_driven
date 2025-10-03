# 🚀 Quick Start Guide - Redis Streams Event Broker

## ✅ What You've Got Now

You've successfully upgraded your event-driven architecture with **Redis Streams**! Here's what changed:

### Before (In-Memory)
```python
from event_broker import broker  # Events lost on restart ❌
```

### After (Redis Streams)
```python
from redis_event_broker import broker  # Events persisted ✅
```

## 📁 New Files Created

1. **`docker-compose.yml`** - Redis container configuration
2. **`redis_event_broker.py`** - New persistent event broker
3. **`services_redis.py`** - Services using Redis broker
4. **`main_redis.py`** - Main application with Redis
5. **`example_replay.py`** - Event replay demonstration
6. **`demo_persistence.py`** - Persistence demonstration
7. **`requirements.txt`** - Python dependencies
8. **`README_REDIS.md`** - Full documentation
9. **`COMPARISON.md`** - Detailed comparison
10. **`QUICK_START.md`** - This file!

## 🎯 Running the Application

### Option 1: Using uv (Recommended) 🚀

```bash
# 1. Start Redis (First Time)
docker-compose up -d

# 2. Sync Dependencies (First Time)
uv sync

# 3. Run the Application
uv run python run_redis.py

# 4. View Persisted Events
uv run python run_demo_persistence.py

# 5. Replay Events
uv run python run_demo_replay.py
```

### Option 2: Using pip (Traditional)

```bash
# 1. Start Redis (First Time)
docker-compose up -d

# 2. Install Dependencies (First Time)
pip install -r requirements.txt

# 3. Run the Application
python run_redis.py

# 4. View Persisted Events
python run_demo_persistence.py

# 5. Replay Events
python run_demo_replay.py
```

## 🔥 Key Features You Now Have

### ✅ Persistence
Events survive application restarts:
```bash
# Run the app
uv run python run_redis.py  # or: python run_redis.py

# Stop it (Ctrl+C)

# Run again - events still there!
uv run python run_demo_persistence.py  # or: python run_demo_persistence.py
```

### ✅ Event History
Query past events:
```python
history = broker.get_event_history("AuctionEnded", count=10)
```

### ✅ Event Replay
Replay for debugging:
```python
broker.replay_events("AuctionEnded", from_id='0')
```

### ✅ Stream Statistics
Monitor your event streams:
```python
info = broker.get_stream_info("AuctionEnded")
print(f"Total events: {info['length']}")
```

## 🎮 Commands Cheat Sheet

### Docker/Redis Management
```bash
# Start Redis
docker-compose up -d

# Stop Redis
docker-compose down

# View Redis logs
docker-compose logs -f redis

# Check if Redis is running
docker-compose ps

# Access Redis CLI
docker exec -it event_broker_redis redis-cli

# Remove all data (start fresh)
docker-compose down -v
```

### Redis CLI Commands
```bash
# Inside Redis CLI (docker exec -it event_broker_redis redis-cli)

# List all streams
KEYS events:*

# View stream content
XRANGE events:AuctionEnded - +

# View stream info
XINFO STREAM events:AuctionEnded

# View consumer groups
XINFO GROUPS events:AuctionEnded

# Count events in stream
XLEN events:AuctionEnded
```

### Application Commands
```bash
# Run main application (Redis)
python run_redis.py

# Run main application (in-memory)
python run_inmemory.py

# Demo persistence
python run_demo_persistence.py

# Replay events
python run_demo_replay.py
```

## 🆚 Quick Comparison

| Task | In-Memory | Redis Streams |
|------|-----------|---------------|
| Run app | `python main.py` | `python main_redis.py` |
| Persistence | ❌ None | ✅ Full |
| View history | ❌ Can't | ✅ `demo_persistence.py` |
| Replay events | ❌ Can't | ✅ `example_replay.py` |
| Debugging | ❌ Hard | ✅ Easy |

## 💡 Common Use Cases

### View All Events After Crash
```bash
python demo_persistence.py
```

### Replay Events for Debugging
```bash
python example_replay.py
```

### Monitor Event Streams
```bash
docker exec -it event_broker_redis redis-cli
> XINFO STREAM events:AuctionEnded
```

### Clear All Data (Start Fresh)
```bash
docker-compose down -v
docker-compose up -d
```

## 🐛 Troubleshooting

### "Connection refused" Error
```bash
# Check if Redis is running
docker-compose ps

# If not running, start it
docker-compose up -d
```

### "No module named 'redis'" Error
```bash
# Install dependencies
pip install -r requirements.txt
```

### Want to Start Fresh?
```bash
# Remove all persisted data
docker-compose down -v

# Start Redis again
docker-compose up -d
```

### Old Events in the Way?
```bash
# Access Redis and flush
docker exec -it event_broker_redis redis-cli FLUSHALL
```

## 🎓 Learning Path

1. **Start with in-memory** (`main.py`) - Understand concepts
2. **Upgrade to Redis** (`main_redis.py`) - See persistence
3. **Explore persistence** (`demo_persistence.py`) - View stored events
4. **Try replay** (`example_replay.py`) - Event sourcing pattern
5. **Read comparison** (`COMPARISON.md`) - Understand tradeoffs

## 📊 What's Happening Under the Hood

When you run `main_redis.py`:

1. ✅ Connects to Redis on port 6379
2. ✅ Creates consumer groups for each event type
3. ✅ Starts background threads to consume events
4. ✅ Publishes events to Redis Streams
5. ✅ Consumers read and acknowledge events
6. ✅ All events persisted to disk (AOF)

## 🚀 Next Steps

### For Learning:
- Read `COMPARISON.md` for detailed analysis
- Read `README_REDIS.md` for full documentation
- Experiment with replay at different points
- Try adding new event types

### For Production:
- Add error handling and retries
- Implement dead letter queues
- Add monitoring (stream length, lag)
- Set up Redis cluster for HA
- Configure backup strategy

## 📚 Key Files to Understand

1. **`redis_event_broker.py`** - Core implementation
   - `publish()` - Sends events to Redis
   - `subscribe()` - Creates consumers
   - `replay_events()` - Replays history
   - `get_event_history()` - Query past events

2. **`docker-compose.yml`** - Redis configuration
   - AOF persistence enabled
   - Health checks configured
   - Data volume mounted

3. **`main_redis.py`** - Application entry point
   - Same flow as `main.py`
   - Shows event history
   - Demonstrates statistics

## 🎯 Quick Test

Run this to see everything working:

```bash
# 1. Start Redis
docker-compose up -d

# 2. Run the app (creates events)
python main_redis.py
# Press Enter when done

# 3. View persisted events
python demo_persistence.py

# 4. Replay events
python example_replay.py
```

If all three work, you're all set! ✅

## 💬 Questions?

- **"How do I view events?"** → Run `demo_persistence.py`
- **"How do I replay events?"** → Run `example_replay.py`
- **"Events not persisting?"** → Check `docker-compose ps`
- **"Want to start over?"** → Run `docker-compose down -v`
- **"See the code?"** → Check `redis_event_broker.py`

---

**You now have a production-ready, persistent event broker!** 🎉

All your events are safely stored in Redis and can survive:
- ✅ Application crashes
- ✅ Server restarts
- ✅ Deployments
- ✅ Development cycles

Happy event-driven programming! 🚀

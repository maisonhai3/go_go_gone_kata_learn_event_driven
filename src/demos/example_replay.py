# example_replay.py
"""
Example showing how to replay events from Redis Streams.
This demonstrates the persistence and replay capabilities.
"""

import time
from src.brokers.redis_event_broker import broker
from src.models.events import AuctionEnded, PaymentProcessed

def replay_handler(event):
    """Handler that will be called for replayed events"""
    print(f"  🎬 Replay handler received: {event}")

if __name__ == "__main__":
    print("--- Event Replay Example ---\n")
    
    # Subscribe to events (these handlers will receive replayed events)
    broker.subscribe("AuctionEnded", replay_handler)
    broker.subscribe("PaymentProcessed", replay_handler)
    
    time.sleep(1)  # Give consumers time to start
    
    print("\n1️⃣ Replaying all AuctionEnded events:")
    broker.replay_events("AuctionEnded", from_id='0')
    
    time.sleep(1)
    
    print("\n2️⃣ Replaying all PaymentProcessed events:")
    broker.replay_events("PaymentProcessed", from_id='0')
    
    time.sleep(1)
    
    print("\n3️⃣ Getting event history:")
    history = broker.get_event_history("AuctionEnded", count=10)
    print(f"\nFound {len(history)} AuctionEnded events in history:")
    for event in history:
        print(f"  - {event['id']}: {event['data']}")
    
    print("\n✅ Replay complete!")
    
    input("\nPress Enter to exit...")
    broker.close()

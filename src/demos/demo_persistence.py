# demo_persistence.py
"""
Demonstration of Redis Streams persistence capabilities.
This script shows how events survive application restarts.
"""

import time
import sys
from uuid import uuid4
from src.brokers.redis_event_broker import broker

def demo_persistence():
    print("=== REDIS STREAMS PERSISTENCE DEMO ===\n")
    
    # Check if there are existing events
    print("1️⃣ Checking for existing events in Redis...")
    for event_type in ["BidderRegistered", "AuctionEnded", "PaymentProcessed"]:
        info = broker.get_stream_info(event_type)
        count = info.get('length', 0)
        print(f"   - {event_type}: {count} events")
    
    print("\n2️⃣ Let's view the event history...")
    
    auction_history = broker.get_event_history("AuctionEnded", count=10)
    if auction_history:
        print(f"\n📜 Found {len(auction_history)} AuctionEnded events:")
        for event in auction_history:
            print(f"   - ID: {event['id']}")
            print(f"     Auction: {event['data'].get('auction_id')}")
            print(f"     Winner: {event['data'].get('winning_bidder_id')}")
            print(f"     Price: ${event['data'].get('winning_price')}")
            print()
    else:
        print("   No AuctionEnded events found. Run main_redis.py first!")
    
    payment_history = broker.get_event_history("PaymentProcessed", count=10)
    if payment_history:
        print(f"📜 Found {len(payment_history)} PaymentProcessed events:")
        for event in payment_history:
            print(f"   - ID: {event['id']}")
            print(f"     Status: {event['data'].get('status')}")
            print(f"     Amount: ${event['data'].get('amount')}")
            print()
    else:
        print("   No PaymentProcessed events found.")
    
    print("\n3️⃣ Key Insight:")
    print("   ✅ All these events were persisted BEFORE this script ran!")
    print("   ✅ They survived the application restart!")
    print("   ✅ This is the power of persistent event streams!\n")
    
    # Demonstrate that we can still access old data even after restart
    print("4️⃣ Redis Stream Statistics:")
    for event_type in ["BidderRegistered", "AuctionEnded", "PaymentProcessed"]:
        info = broker.get_stream_info(event_type)
        if info.get('length', 0) > 0:
            print(f"\n   Stream: events:{event_type}")
            print(f"   - Total events: {info.get('length', 0)}")
            print(f"   - First entry ID: {info.get('first_entry', ['N/A'])[0] if info.get('first_entry') else 'N/A'}")
            print(f"   - Last entry ID: {info.get('last_entry', ['N/A'])[0] if info.get('last_entry') else 'N/A'}")
            print(f"   - Consumer groups: {info.get('groups', 0)}")
    
    broker.close()

if __name__ == "__main__":
    try:
        demo_persistence()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted.")
        broker.close()
        sys.exit(0)

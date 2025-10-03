# redis_event_broker.py
import json
import threading
import time
from typing import Callable, Any, Dict, List, Optional
from dataclasses import asdict, is_dataclass
import redis
from redis.exceptions import ResponseError

class RedisEventBroker:
    """
    Event Broker using Redis Streams for persistence and reliability.
    
    Features:
    - Persistent event storage
    - Event replay capability
    - Consumer groups for reliable processing
    - Automatic reconnection
    """
    
    def __init__(self, redis_host: str = 'localhost', redis_port: int = 6379, redis_db: int = 0):
        print(f"🔌 Connecting to Redis at {redis_host}:{redis_port}...")
        self.redis_client = redis.Redis(
            host=redis_host,
            port=redis_port,
            db=redis_db,
            decode_responses=True,
            health_check_interval=30
        )
        
        # Test connection
        try:
            self.redis_client.ping()
            print("✅ Redis Event Broker initialized successfully.")
        except redis.ConnectionError as e:
            print(f"❌ Failed to connect to Redis: {e}")
            print("💡 Make sure Redis is running. Use: docker-compose up -d")
            raise
        
        self._subscribers: Dict[str, List[Callable]] = {}
        self._consumer_threads: Dict[str, threading.Thread] = {}
        self._running = True
        
    def subscribe(self, event_type: str, callback: Callable, consumer_group: str = "default"):
        """
        Subscribe to an event type with a callback function.
        
        Args:
            event_type: The type of event to listen for
            callback: Function to call when event is received
            consumer_group: Consumer group name (for load balancing)
        """
        print(f"📝 New subscription: {callback.__qualname__} is listening for '{event_type}' in group '{consumer_group}'")
        
        # Store subscriber
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
        
        # Create consumer group if it doesn't exist
        stream_key = f"events:{event_type}"
        try:
            self.redis_client.xgroup_create(stream_key, consumer_group, id='0', mkstream=True)
            print(f"  ✅ Created consumer group '{consumer_group}' for stream '{stream_key}'")
        except ResponseError as e:
            if 'BUSYGROUP' not in str(e):
                print(f"  ⚠️  Error creating consumer group: {e}")
        
        # Start consumer thread if not already running for this event type
        thread_key = f"{event_type}:{consumer_group}"
        if thread_key not in self._consumer_threads:
            thread = threading.Thread(
                target=self._consume_events,
                args=(event_type, consumer_group),
                daemon=True,
                name=f"Consumer-{thread_key}"
            )
            thread.start()
            self._consumer_threads[thread_key] = thread
    
    def publish(self, event_type: str, data: Any, event_id: Optional[str] = None):
        """
        Publish an event to Redis Stream.
        
        Args:
            event_type: The type of event
            data: Event data (will be serialized to JSON)
            event_id: Optional custom event ID (default: auto-generated)
        """
        stream_key = f"events:{event_type}"
        
        # Serialize data to JSON
        if is_dataclass(data):
            event_data = asdict(data)
        elif isinstance(data, dict):
            event_data = data
        else:
            event_data = {"data": str(data)}
        
        # Convert all values to strings for Redis
        redis_data = {
            "event_type": event_type,
            "payload": json.dumps(event_data, default=str)
        }
        
        # Publish to Redis Stream
        if event_id:
            stream_id = self.redis_client.xadd(stream_key, redis_data, id=event_id)
        else:
            stream_id = self.redis_client.xadd(stream_key, redis_data)
        
        print(f"\n📢 Published event '{event_type}' to Redis Stream (ID: {stream_id})")
        print(f"   Data: {event_data}")
        
        return stream_id
    
    def _consume_events(self, event_type: str, consumer_group: str):
        """
        Background thread that consumes events from Redis Stream.
        """
        stream_key = f"events:{event_type}"
        consumer_name = f"consumer_{threading.get_ident()}"
        
        print(f"🎧 Started consumer '{consumer_name}' for '{event_type}' in group '{consumer_group}'")
        
        while self._running:
            try:
                # Read messages from the stream
                messages = self.redis_client.xreadgroup(
                    groupname=consumer_group,
                    consumername=consumer_name,
                    streams={stream_key: '>'},
                    count=10,
                    block=1000  # Block for 1 second
                )
                
                if messages:
                    for stream, events in messages:
                        for event_id, event_data in events:
                            self._process_event(event_type, event_id, event_data, stream_key, consumer_group)
                            
            except Exception as e:
                print(f"❌ Error in consumer thread for '{event_type}': {e}")
                time.sleep(1)  # Back off on error
    
    def _process_event(self, event_type: str, event_id: str, event_data: Dict, stream_key: str, consumer_group: str):
        """Process a single event and acknowledge it."""
        try:
            # Deserialize payload
            payload_json = event_data.get('payload', '{}')
            payload = json.loads(payload_json)
            
            # Call all subscribers for this event type
            if event_type in self._subscribers:
                for callback in self._subscribers[event_type]:
                    try:
                        # Try to reconstruct the original object if possible
                        callback(self._reconstruct_event(payload))
                    except Exception as e:
                        print(f"❌ Error calling callback {callback.__qualname__}: {e}")
            
            # Acknowledge the message
            self.redis_client.xack(stream_key, consumer_group, event_id)
            
        except Exception as e:
            print(f"❌ Error processing event {event_id}: {e}")
    
    def _reconstruct_event(self, payload: Dict):
        """
        Attempt to reconstruct the event object.
        For now, returns a simple dict. Can be enhanced to reconstruct dataclass objects.
        """
        # Import events to reconstruct objects
        try:
            from src.models.events import BidderRegistered, AuctionEnded, PaymentProcessed
            from uuid import UUID
            
            # Try to match and reconstruct
            if 'bidder_id' in payload and 'credit_card_token' in payload:
                return BidderRegistered(
                    bidder_id=UUID(payload['bidder_id']),
                    name=payload['name'],
                    credit_card_token=payload['credit_card_token']
                )
            elif 'auction_id' in payload and 'winning_bidder_id' in payload:
                return AuctionEnded(
                    auction_id=UUID(payload['auction_id']),
                    winning_bidder_id=UUID(payload['winning_bidder_id']),
                    winning_price=float(payload['winning_price'])
                )
            elif 'auction_id' in payload and 'status' in payload:
                return PaymentProcessed(
                    auction_id=UUID(payload['auction_id']),
                    bidder_id=UUID(payload['bidder_id']),
                    amount=float(payload['amount']),
                    status=payload['status']
                )
        except Exception:
            pass
        
        # Fallback to dict
        return payload
    
    def get_event_history(self, event_type: str, count: int = 10) -> List[Dict]:
        """
        Retrieve historical events from a stream.
        
        Args:
            event_type: The type of event
            count: Number of events to retrieve
            
        Returns:
            List of events with their IDs and data
        """
        stream_key = f"events:{event_type}"
        
        try:
            # Read last N messages from the stream
            messages = self.redis_client.xrevrange(stream_key, count=count)
            
            history = []
            for event_id, event_data in messages:
                payload = json.loads(event_data.get('payload', '{}'))
                history.append({
                    'id': event_id,
                    'type': event_type,
                    'data': payload
                })
            
            return history
        except Exception as e:
            print(f"❌ Error retrieving event history: {e}")
            return []
    
    def replay_events(self, event_type: str, from_id: str = '0', count: Optional[int] = None):
        """
        Replay events from a specific point in the stream.
        
        Args:
            event_type: The type of event to replay
            from_id: Starting event ID (default: from beginning)
            count: Maximum number of events to replay (None = all)
        """
        stream_key = f"events:{event_type}"
        
        print(f"\n🔄 Replaying events from '{event_type}' starting from ID '{from_id}'...")
        
        try:
            messages = self.redis_client.xrange(stream_key, min=from_id, count=count)
            
            replayed = 0
            for event_id, event_data in messages:
                payload = json.loads(event_data.get('payload', '{}'))
                
                print(f"  📼 Replaying event {event_id}: {payload}")
                
                # Call subscribers
                if event_type in self._subscribers:
                    for callback in self._subscribers[event_type]:
                        try:
                            callback(self._reconstruct_event(payload))
                        except Exception as e:
                            print(f"❌ Error in replay callback {callback.__qualname__}: {e}")
                
                replayed += 1
            
            print(f"✅ Replayed {replayed} events")
            
        except Exception as e:
            print(f"❌ Error replaying events: {e}")
    
    def get_stream_info(self, event_type: str) -> Dict:
        """Get information about a stream."""
        stream_key = f"events:{event_type}"
        
        try:
            info = self.redis_client.xinfo_stream(stream_key)
            return {
                'length': info.get('length', 0),
                'first_entry': info.get('first-entry'),
                'last_entry': info.get('last-entry'),
                'groups': info.get('groups', 0)
            }
        except ResponseError:
            return {'length': 0, 'error': 'Stream does not exist'}
    
    def close(self):
        """Close the broker and cleanup resources."""
        print("\n🔌 Closing Redis Event Broker...")
        self._running = False
        
        # Wait for consumer threads to finish
        for thread in self._consumer_threads.values():
            thread.join(timeout=2)
        
        self.redis_client.close()
        print("✅ Redis Event Broker closed.")


# Create a singleton instance
broker = RedisEventBroker()

# main_redis.py
import time
from uuid import uuid4
from src.services.services_redis import RegistrationService, AuctionService, PaymentService, NotificationService
from src.brokers.redis_event_broker import broker

if __name__ == "__main__":
    print("--- System Initialization with Redis Streams ---")
    # Khởi tạo các dịch vụ. Khi khởi tạo, chúng sẽ tự đăng ký với broker.
    registration_service = RegistrationService()
    auction_service = AuctionService()
    payment_service = PaymentService()
    notification_service = NotificationService()
    
    # Give consumers time to start
    time.sleep(1)
    print("--- System Ready ---\n")

    # --- Kịch bản mô phỏng ---
    print("--- Step 1: A new bidder registers ---")
    bidder_id = registration_service.register_bidder(
        name="Gia Sư Học Tập", 
        credit_card_number="1234-5678-9012-3456"
    )

    print("\n--- Step 2: Some time passes, and an auction ends ---")
    auction_id = uuid4()
    
    # Dịch vụ đấu giá phát sự kiện kết thúc.
    # Nó không cần biết ai sẽ xử lý việc thanh toán.
    auction_service.end_auction(
        auction_id=auction_id,
        winner_id=bidder_id,
        price=99.99
    )

    # Give time for async processing
    time.sleep(2)

    print("\n--- Step 3: Check Event History ---")
    print("\n📊 AuctionEnded Event History:")
    history = broker.get_event_history("AuctionEnded", count=5)
    for event in history:
        print(f"  - ID: {event['id']}, Data: {event['data']}")
    
    print("\n📊 PaymentProcessed Event History:")
    history = broker.get_event_history("PaymentProcessed", count=5)
    for event in history:
        print(f"  - ID: {event['id']}, Data: {event['data']}")

    print("\n--- Step 4: Stream Information ---")
    for event_type in ["BidderRegistered", "AuctionEnded", "PaymentProcessed"]:
        info = broker.get_stream_info(event_type)
        print(f"\n📈 Stream '{event_type}':")
        print(f"   Total events: {info.get('length', 0)}")

    print("\n--- Simulation Finished ---")
    print("✅ All events are now persisted in Redis!")
    print("✅ You can restart the application and events will still be there.")
    print("✅ Run replay examples to see historical events in action.")
    
    # Cleanup
    input("\nPress Enter to exit...")
    broker.close()

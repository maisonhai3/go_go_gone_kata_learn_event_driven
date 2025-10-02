# main.py
from uuid import uuid4
from services import RegistrationService, AuctionService, PaymentService, NotificationService

if __name__ == "__main__":
    print("--- System Initialization ---")
    # Khởi tạo các dịch vụ. Khi khởi tạo, chúng sẽ tự đăng ký với broker.
    registration_service = RegistrationService()
    auction_service = AuctionService()
    payment_service = PaymentService()
    notification_service = NotificationService()
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

    print("\n--- Simulation Finished ---")
    print("Observe the chain of events triggered by 'AuctionEnded'.")
    print("PaymentService and NotificationService reacted without being called directly.")

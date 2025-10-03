# services_redis.py
import random
from uuid import UUID, uuid4
from src.brokers.redis_event_broker import broker
from src.models.events import BidderRegistered, AuctionEnded, PaymentProcessed

class RegistrationService:
    def register_bidder(self, name: str, credit_card_number: str):
        print(f"[Registration Service] Registering bidder '{name}'...")
        # Giả lập việc gọi cổng thanh toán để lấy token an toàn
        token = f"tok_{random.randint(1000, 9999)}"
        
        event = BidderRegistered(
            bidder_id=uuid4(),
            name=name,
            credit_card_token=token
        )
        broker.publish("BidderRegistered", event)
        return event.bidder_id

class AuctionService:
    def end_auction(self, auction_id: UUID, winner_id: UUID, price: float):
        print(f"[Auction Service] Auction '{auction_id}' has ended.")
        event = AuctionEnded(
            auction_id=auction_id,
            winning_bidder_id=winner_id,
            winning_price=price
        )
        broker.publish("AuctionEnded", event)

class PaymentService:
    def __init__(self):
        # Khi PaymentService khởi tạo, nó sẽ tự động đăng ký lắng nghe sự kiện
        broker.subscribe("AuctionEnded", self.handle_auction_ended)

    def handle_auction_ended(self, event: AuctionEnded):
        """Đây là trái tim của yêu cầu: lắng nghe và hành động."""
        print(f"[Payment Service] Received AuctionEnded event. Processing payment for winner '{event.winning_bidder_id}'.")
        
        # Giả lập việc gọi cổng thanh toán để trừ tiền
        # Logic thực tế sẽ phức tạp hơn
        payment_successful = random.choice([True, False]) 
        status = "SUCCESS" if payment_successful else "FAILED"
        
        print(f"[Payment Service] Payment status: {status}")

        payment_event = PaymentProcessed(
            auction_id=event.auction_id,
            bidder_id=event.winning_bidder_id,
            amount=event.winning_price,
            status=status
        )
        broker.publish("PaymentProcessed", payment_event)

class NotificationService:
    def __init__(self):
        broker.subscribe("PaymentProcessed", self.handle_payment_processed)

    def handle_payment_processed(self, event: PaymentProcessed):
        print(f"[Notification Service] Received PaymentProcessed event.")
        if event.status == "SUCCESS":
            print(f"  -> Sending SUCCESS email to bidder '{event.bidder_id}' for winning auction '{event.auction_id}'.")
        else:
            print(f"  -> Sending FAILED email to bidder '{event.bidder_id}' for auction '{event.auction_id}'.")

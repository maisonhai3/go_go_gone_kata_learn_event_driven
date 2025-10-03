Tuyệt vời\! Đây là một bài thực hành xuất sắc để trải nghiệm sức mạnh và tư duy đằng sau Kiến trúc Hướng sự kiện (Event-Driven Architecture). Chúng ta sẽ thiết kế và triển khai một hệ thống nhỏ bằng Python để giải quyết chính xác yêu cầu bạn đã nêu.

Thay vì gọi các hàm trực tiếp, chúng ta sẽ để các thành phần giao tiếp với nhau bằng cách "phát" và "lắng nghe" các sự kiện.

-----

### **Phân tích và Thiết kế**

Trước khi viết code, hãy cùng phân tích luồng sự kiện cho yêu cầu: *"Người đấu giá đăng ký bằng thẻ tín dụng; hệ thống tự động trừ tiền vào thẻ nếu người đó thắng."*

1.  **Sự kiện 1: `BidderRegistered` (Người đấu giá đã đăng ký)**

      * **Ai phát:** `RegistrationService` (Dịch vụ Đăng ký)
      * **Khi nào:** Khi một người dùng đăng ký thành công.
      * **Thông tin mang theo:** `bidder_id`, `name`, `credit_card_token` (chúng ta sẽ không lưu thông tin thẻ thật, chỉ một mã đại diện an toàn).

2.  **Sự kiện 2: `AuctionEnded` (Phiên đấu giá đã kết thúc)**

      * **Ai phát:** `AuctionService` (Dịch vụ Đấu giá)
      * **Khi nào:** Khi thời gian của một phiên đấu giá kết thúc.
      * **Thông tin mang theo:** `auction_id`, `winning_bidder_id`, `winning_price`.

3.  **Sự kiện 3: `PaymentProcessed` (Thanh toán đã được xử lý)**

      * **Ai phát:** `PaymentService` (Dịch vụ Thanh toán)
      * **Khi nào:** Sau khi cố gắng trừ tiền từ thẻ của người thắng cuộc.
      * **Thông tin mang theo:** `auction_id`, `bidder_id`, `amount`, `status` ('SUCCESS' hoặc 'FAILED').

**Luồng hoạt động sẽ như sau:**
`AuctionService` phát ra sự kiện `AuctionEnded`. `PaymentService` lắng nghe sự kiện này. Khi nhận được, nó sẽ xử lý thanh toán và sau đó phát ra sự kiện `PaymentProcessed`. Một dịch vụ khác, ví dụ như `NotificationService`, có thể lắng nghe sự kiện `PaymentProcessed` để gửi email cho người thắng cuộc.

Các dịch vụ này hoàn toàn **không biết** đến sự tồn tại của nhau. Chúng chỉ biết về "trung tâm tin tức" (Event Broker).

-----

### **Coding Example (Python)**

Dưới đây là một ví dụ hoàn chỉnh, mô phỏng toàn bộ luồng này. Chúng ta sẽ tạo một `EventBroker` đơn giản để giữ cho ví dụ dễ hiểu.

#### **1. `event_broker.py`: Trung tâm tin tức**

Đây là trái tim của hệ thống. Nó quản lý việc đăng ký lắng nghe và phát các sự kiện.

```python
# event_broker.py
from collections import defaultdict
from typing import Callable, Any

class EventBroker:
    def __init__(self):
        print("Event Broker initialized.")
        self._subscribers = defaultdict(list)

    def subscribe(self, event_type: str, callback: Callable):
        """Đăng ký một hàm callback để lắng nghe một loại sự kiện."""
        print(f"New subscription: {callback.__qualname__} is listening for '{event_type}'")
        self._subscribers[event_type].append(callback)

    def publish(self, event_type: str, data: Any):
        """Phát một sự kiện đến tất cả những người đã đăng ký."""
        print(f"\n📢 Publishing event '{event_type}' with data: {data}")
        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                try:
                    callback(data)
                except Exception as e:
                    print(f"Error calling callback {callback.__qualname__}: {e}")

# Tạo một instance duy nhất để toàn bộ hệ thống sử dụng
broker = EventBroker()
```

#### **2. `events.py`: Định nghĩa các loại tin tức**

Chúng ta dùng `dataclasses` để định nghĩa cấu trúc của các sự kiện một cách rõ ràng.

```python
# events.py
from dataclasses import dataclass
from uuid import UUID

@dataclass
class BidderRegistered:
    bidder_id: UUID
    name: str
    credit_card_token: str

@dataclass
class AuctionEnded:
    auction_id: UUID
    winning_bidder_id: UUID
    winning_price: float

@dataclass
class PaymentProcessed:
    auction_id: UUID
    bidder_id: UUID
    amount: float
    status: str
```

#### **3. `services.py`: Các bộ phận chức năng**

Đây là nơi chứa logic nghiệp vụ. Chú ý cách chúng hoàn toàn độc lập với nhau.

```python
# services.py
import random
from uuid import UUID, uuid4
from event_broker import broker
from events import BidderRegistered, AuctionEnded, PaymentProcessed

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

```

#### **4. `main.py`: Kịch bản mô phỏng**

File này sẽ khởi tạo các dịch vụ và mô phỏng một luồng sự kiện hoàn chỉnh.

```python
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

```

### **Cách chạy và Kết quả**

1.  Lưu 4 file trên (`event_broker.py`, `events.py`, `services.py`, `main.py`) vào cùng một thư mục.
2.  Mở terminal trong thư mục đó và chạy: `python main.py`

**Bạn sẽ thấy một output tương tự như sau:**

```
--- System Initialization ---
Event Broker initialized.
New subscription: PaymentService.handle_auction_ended is listening for 'AuctionEnded'
New subscription: NotificationService.handle_payment_processed is listening for 'PaymentProcessed'
--- System Ready ---

--- Step 1: A new bidder registers ---
[Registration Service] Registering bidder 'Gia Sư Học Tập'...

📢 Publishing event 'BidderRegistered' with data: BidderRegistered(bidder_id=..., name='Gia Sư Học Tập', credit_card_token='tok_...')

--- Step 2: Some time passes, and an auction ends ---
[Auction Service] Auction '...' has ended.

📢 Publishing event 'AuctionEnded' with data: AuctionEnded(auction_id=..., winning_bidder_id=..., winning_price=99.99)
[Payment Service] Received AuctionEnded event. Processing payment for winner '...'.
[Payment Service] Payment status: SUCCESS

📢 Publishing event 'PaymentProcessed' with data: PaymentProcessed(auction_id=..., bidder_id=..., amount=99.99, status='SUCCESS')
[Notification Service] Received PaymentProcessed event.
  -> Sending SUCCESS email to bidder '...' for winning auction '...'.

--- Simulation Finished ---
Observe the chain of events triggered by 'AuctionEnded'.
PaymentService and NotificationService reacted without being called directly.
```

Như bạn thấy, hàm `auction_service.end_auction()` chỉ phát ra một sự kiện. Hành động đó đã kích hoạt một chuỗi phản ứng dây chuyền: `PaymentService` bắt được sự kiện và xử lý, sau đó lại phát ra một sự kiện mới, và `NotificationService` lại bắt được sự kiện đó để hành động. Đây chính là bản chất của Kiến trúc Hướng sự kiện: **hành động và phản ứng một cách linh hoạt và độc lập.**
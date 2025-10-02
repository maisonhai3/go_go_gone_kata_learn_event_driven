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

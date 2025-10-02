# Event-Driven Architecture Learning Project

This project demonstrates a simple Event-Driven Architecture (EDA) implementation in Python, simulating an auction system with automatic payment processing.

## Overview

The system consists of four main components that communicate through events:

1. **Event Broker** (`event_broker.py`) - Manages event subscriptions and publishing
2. **Event Definitions** (`events.py`) - Defines event data structures
3. **Services** (`services.py`) - Business logic services that communicate through events
4. **Main Simulation** (`main.py`) - Demonstrates the event flow

## Architecture

### Services

- **RegistrationService**: Handles bidder registration and publishes `BidderRegistered` events
- **AuctionService**: Manages auctions and publishes `AuctionEnded` events
- **PaymentService**: Listens to `AuctionEnded` events, processes payments, and publishes `PaymentProcessed` events
- **NotificationService**: Listens to `PaymentProcessed` events and sends notifications

### Event Flow

```
AuctionEnded → PaymentService → PaymentProcessed → NotificationService
```

Services are completely decoupled - they don't know about each other, only about the events they emit and listen to.

## Running the Project

```bash
python main.py
```

## Expected Output

The simulation will:
1. Initialize all services (which automatically subscribe to relevant events)
2. Register a new bidder
3. End an auction with a winner
4. Automatically process payment (randomly succeeds or fails)
5. Automatically send notification based on payment status

You'll see output showing the event chain reaction:
- Auction ends → Event published
- Payment service receives event → Processes payment → Publishes payment event
- Notification service receives event → Sends notification

## Key Concepts

- **Loose Coupling**: Services don't directly call each other
- **Event-Driven**: Actions trigger events that cascade through the system
- **Scalability**: New services can be added by simply subscribing to events
- **Maintainability**: Changes to one service don't affect others

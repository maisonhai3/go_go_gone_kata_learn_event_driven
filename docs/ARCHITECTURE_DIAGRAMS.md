# Architecture Diagrams

## In-Memory Event Broker (Original)

```
┌─────────────────────────────────────────────────────────┐
│                    Application Process                   │
│                                                           │
│  ┌─────────────┐                                         │
│  │  Services   │                                         │
│  ├─────────────┤                                         │
│  │ Registration│───┐                                     │
│  │  Auction    │───┼───┐                                 │
│  │  Payment    │───┼───┼───┐                             │
│  │ Notification│◄──┼───┼───┼───┐                         │
│  └─────────────┘   │   │   │   │                         │
│                    │   │   │   │                         │
│         ┌──────────▼───▼───▼───▼──────────┐              │
│         │    In-Memory Event Broker        │              │
│         │  ┌──────────────────────────┐   │              │
│         │  │ Subscribers: {           │   │              │
│         │  │   'AuctionEnded': [...], │   │              │
│         │  │   'PaymentProcessed':[...│   │              │
│         │  │ }                        │   │              │
│         │  └──────────────────────────┘   │              │
│         └──────────────────────────────────┘              │
│                                                           │
│         ❌ Events lost on restart                         │
│         ❌ No history                                     │
│         ❌ No replay                                      │
└─────────────────────────────────────────────────────────┘
```

## Redis Streams Event Broker (New)

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Application Process                          │
│                                                                       │
│  ┌─────────────┐                                                     │
│  │  Services   │                                                     │
│  ├─────────────┤                                                     │
│  │ Registration│───┐                                                 │
│  │  Auction    │───┼───┐                                             │
│  │  Payment    │───┼───┼───┐                                         │
│  │ Notification│◄──┼───┼───┼───┐                                     │
│  └─────────────┘   │   │   │   │                                     │
│                    │   │   │   │                                     │
│         ┌──────────▼───▼───▼───▼──────────────────┐                  │
│         │    Redis Event Broker (Client)          │                  │
│         │  ┌─────────────────────────────────┐   │                  │
│         │  │ publish() ──► Redis Streams     │   │                  │
│         │  │ subscribe() ──► Consumer Threads│   │                  │
│         │  └─────────────────────────────────┘   │                  │
│         └────────────┬─────────────────▲──────────┘                  │
│                      │                 │                             │
└──────────────────────┼─────────────────┼─────────────────────────────┘
                       │                 │
                       │ TCP/IP          │
                       │ (localhost:6379)│
                       ▼                 │
┌──────────────────────────────────────────────────────────────────────┐
│                         Redis Server (Docker)                         │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                        Redis Streams                          │   │
│  │                                                               │   │
│  │  events:BidderRegistered     [1759458928760-0] {data...}     │   │
│  │                              [1759458928761-0] {data...}     │   │
│  │                                                               │   │
│  │  events:AuctionEnded         [1759458928760-0] {data...}     │   │
│  │                              [1759458928761-0] {data...}     │   │
│  │                                                               │   │
│  │  events:PaymentProcessed     [1759458928761-0] {data...}     │   │
│  │                              [1759458928762-0] {data...}     │   │
│  │                                                               │   │
│  │  ┌─────────────────────────────────────────────────────┐    │   │
│  │  │ Consumer Groups (for reliability)                    │    │   │
│  │  │  - default (for AuctionEnded)                       │    │   │
│  │  │  - default (for PaymentProcessed)                   │    │   │
│  │  └─────────────────────────────────────────────────────┘    │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                 Persistence Layer (AOF)                       │   │
│  │                                                               │   │
│  │   /data/appendonly.aof   ← Disk persistence                  │   │
│  │                                                               │   │
│  │   ✅ Survives restarts                                        │   │
│  │   ✅ Event history                                            │   │
│  │   ✅ Event replay                                             │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘
```

## Event Flow Diagram

### Publishing an Event

```
┌──────────────┐
│ AuctionService│
│   .end_auction()
└───────┬───────┘
        │
        │ 1. Create event object
        │    AuctionEnded(auction_id, winner_id, price)
        ▼
┌────────────────────┐
│ broker.publish()   │
│  "AuctionEnded"    │
└─────────┬──────────┘
          │
          │ 2. Serialize to JSON
          │    Convert dataclass → dict → JSON
          ▼
┌─────────────────────────────┐
│ Redis XADD command          │
│  XADD events:AuctionEnded * │
│    payload={...}            │
└──────────┬──────────────────┘
           │
           │ 3. Persist to Redis Stream
           ▼
    ┌──────────────────┐
    │ Redis Stream      │
    │ events:AuctionEnded│
    │ [1759-0] {data}  │
    │                   │
    │ ✅ Persisted!     │
    └──────────────────┘
```

### Consuming an Event

```
    ┌──────────────────┐
    │ Redis Stream      │
    │ events:AuctionEnded│
    │ [1759-0] {data}  │
    │                   │
    └─────────┬─────────┘
              │
              │ 1. Consumer thread polling
              │    XREADGROUP default consumer1
              ▼
    ┌─────────────────────┐
    │ Consumer Thread     │
    │  (background)       │
    └─────────┬───────────┘
              │
              │ 2. Deserialize JSON → dict
              │    Reconstruct event object
              ▼
    ┌─────────────────────┐
    │ Registered Callbacks│
    │  - PaymentService   │
    │    .handle_auction_ │
    │     ended()         │
    └─────────┬───────────┘
              │
              │ 3. Call handler with event
              ▼
    ┌─────────────────────┐
    │ PaymentService      │
    │  processes payment  │
    └─────────┬───────────┘
              │
              │ 4. Acknowledge message
              │    XACK events:AuctionEnded default [1759-0]
              ▼
         ✅ Complete!
```

## Consumer Group Pattern

```
                        ┌─────────────────────────┐
                        │   Redis Stream          │
                        │  events:AuctionEnded    │
                        │                         │
                        │  [1001-0] {event1}      │
                        │  [1002-0] {event2}      │
                        │  [1003-0] {event3}      │
                        │  [1004-0] {event4}      │
                        └───────────┬─────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
          ┌─────────▼─────────┐         ┌──────────▼──────────┐
          │ Consumer Group:   │         │ Consumer Group:     │
          │    "default"      │         │   "analytics"       │
          │                   │         │                     │
          │ ┌─────────────┐   │         │ ┌─────────────┐    │
          │ │ Consumer 1  │   │         │ │ Consumer A  │    │
          │ │ (Thread)    │   │         │ │ (Thread)    │    │
          │ └─────────────┘   │         │ └─────────────┘    │
          │                   │         │                     │
          │ ┌─────────────┐   │         └─────────────────────┘
          │ │ Consumer 2  │   │
          │ │ (Thread)    │   │         Each group gets ALL messages
          │ └─────────────┘   │         Within group: load balanced
          └───────────────────┘
          
          Messages distributed        Each consumer in group
          among consumers             gets different messages
```

## Persistence & Recovery Flow

```
┌─────────────────────────────────────────────────────────┐
│                  Event Lifecycle                         │
└─────────────────────────────────────────────────────────┘

1. Event Published
   ┌─────────────┐
   │ Application │ ──► Redis Stream ──► AOF File (Disk)
   └─────────────┘         │
                           │ ✅ Synced every 1 second
                           ▼
                      ┌──────────┐
                      │   Disk   │
                      └──────────┘

2. Application Crashes
   ┌─────────────┐
   │ Application │ ──✗ Crashed
   └─────────────┘
                   
   ┌──────────────────┐
   │ Redis Stream     │ ✅ Still has events
   │ AOF File         │ ✅ Still on disk
   └──────────────────┘

3. Application Restarts
   ┌─────────────┐
   │ Application │ ──► Connects to Redis
   └─────────────┘         │
                           │ Events still there!
                           ▼
                   ┌──────────────────┐
                   │ Redis Stream     │
                   │ - Read history   │
                   │ - Replay events  │
                   │ - Resume work    │
                   └──────────────────┘

4. Redis Restarts
   ┌─────────────┐
   │ Redis       │ ──✗ Stopped
   └─────────────┘
   
   ┌─────────────┐
   │ AOF File    │ ✅ On disk
   └─────────────┘
   
   ┌─────────────┐
   │ Redis       │ ──► Loads from AOF
   └──────┬──────┘         │
          │                │ All events restored!
          ▼                ▼
   ┌──────────────────────────┐
   │ Redis Streams Rebuilt    │
   │ - All events present     │
   │ - Consumer groups intact │
   │ - Ready to work          │
   └──────────────────────────┘
```

## Comparison: Message Flow

### In-Memory Broker
```
Publish    Subscribe    Message Flow
────────   ─────────    ────────────

Service ──► Broker ──► Handler
    │         │           │
    │     (in RAM)        │
    │                     │
    └─────────────────────┘
    
❌ Lost on crash
❌ No retry
❌ No history
```

### Redis Streams Broker
```
Publish    Subscribe    Message Flow
────────   ─────────    ────────────

Service ──► Redis ──► Consumer ──► Handler
    │         │          │           │
    │     (persisted)    │           │
    │         │          │           │
    │     ┌───▼────┐     │           │
    │     │ Disk   │     │           │
    │     └────────┘     │           │
    │                    │           │
    │                ┌───▼────┐      │
    │                │ ACK    │      │
    │                └────────┘      │
    │                                │
    └────────────────────────────────┘
    
✅ Survives crash
✅ Retry on failure
✅ Full history
✅ Replay capability
```

## Component Interaction

```
┌────────────────────────────────────────────────────────────┐
│                      Your Application                       │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │Registration │  │   Auction   │  │   Payment   │        │
│  │  Service    │  │   Service   │  │   Service   │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
│         │                │                │               │
│         │ publish()      │ publish()      │ subscribe()   │
│         ▼                ▼                ▼               │
│  ┌───────────────────────────────────────────────────┐    │
│  │         RedisEventBroker (Client Library)         │    │
│  │                                                    │    │
│  │  - Serialize events to JSON                       │    │
│  │  - Send to Redis via XADD                         │    │
│  │  - Consume via XREADGROUP                         │    │
│  │  - Deserialize and dispatch to handlers          │    │
│  │  - Acknowledge messages (XACK)                    │    │
│  └────────────────────┬──────────────────────────────┘    │
│                       │                                   │
└───────────────────────┼───────────────────────────────────┘
                        │
                        │ Redis Protocol (TCP)
                        │
┌───────────────────────▼───────────────────────────────────┐
│                    Redis Server                            │
│                                                            │
│  ┌──────────────────────────────────────────────────┐     │
│  │              Stream Storage Engine                │     │
│  │                                                   │     │
│  │  - Append-only log structure                     │     │
│  │  - Consumer group management                     │     │
│  │  - Message acknowledgment tracking               │     │
│  │  - Stream compaction (optional)                  │     │
│  └──────────────────────────────────────────────────┘     │
│                                                            │
│  ┌──────────────────────────────────────────────────┐     │
│  │           Persistence Layer (AOF)                 │     │
│  │                                                   │     │
│  │  - fsync every second                            │     │
│  │  - Automatic recovery on restart                 │     │
│  │  - Point-in-time snapshots (RDB)                │     │
│  └──────────────────────────────────────────────────┘     │
└────────────────────────────────────────────────────────────┘
```

## Key Benefits Visualization

```
┌─────────────────────────────────────────────────────────┐
│              Event-Driven Architecture Benefits         │
└─────────────────────────────────────────────────────────┘

Before (Tight Coupling):
─────────────────────────
AuctionService ──► PaymentService ──► NotificationService
                      │
                      ▼
              (Direct dependency)

❌ Hard to change
❌ Hard to test
❌ Cascade failures

After (Event-Driven with Redis):
──────────────────────────────────
AuctionService ──► Redis ──► PaymentService
                     │
                     └──► NotificationService
                     │
                     └──► AnalyticsService (new!)
                     │
                     └──► AuditService (new!)

✅ Easy to add new services
✅ Services independent
✅ Fault isolation
✅ Events persisted
✅ Can replay for debugging
✅ Full audit trail
```

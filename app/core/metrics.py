from prometheus_client import Counter, Gauge, Histogram

# Counts every supply event ingested, labelled by event type.
# Labels let you filter in Grafana: "show me only DELAYED events"
events_ingested_total = Counter(
    "orisync_events_ingested_total",
    "Total number of supply events ingested",
    ["event_type"],
)

# Counts webhook delivery attempts and their outcomes.
webhook_deliveries_total = Counter(
    "orisync_webhook_deliveries_total",
    "Total webhook delivery attempts",
    ["status"],  # success or failed
)

# Tracks how many active webhook subscriptions exist right now.
active_subscriptions = Gauge(
    "orisync_active_subscriptions",
    "Number of active webhook subscriptions",
)

# Measures how long webhook HTTP calls take.
# Histogram buckets let you calculate percentiles in Grafana.
webhook_delivery_duration_seconds = Histogram(
    "orisync_webhook_delivery_duration_seconds",
    "Time taken to deliver a webhook",
    buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0],
)

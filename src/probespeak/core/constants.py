"""Fixed product facts. Threshold numbers stay in the agent so they cannot drift."""

APP_NAME = "ProbeSpeak"
PROBLEM = "PS-015"
VERSION_LABEL = "0.3.0"
DEFAULT_TCP_TARGETS = (
    ("1.1.1.1", 443),
    ("8.8.8.8", 443),
    ("9.9.9.9", 443),
)
MONITOR_CHOICES = {
    "30 minutes": 30 * 60,
    "1 hour": 60 * 60,
    "2 hours": 2 * 60 * 60,
    "Daily": 24 * 60 * 60,
}
PLAIN = {
    "NO_FAULT": "All four checks passed. Nothing was fixed. This is not called Resolved.",
    "DNS_RESOLVER_FAILURE": (
        "Name lookup failed, and the router plus the rest of the path look quiet. "
        "That points at DNS, not a dead internet connection."
    ),
    "GATEWAY_UNREACHABLE": (
        "The router did not answer, name lookup failed, most packets were lost, "
        "and delay probes timed out together."
    ),
    "SIGNIFICANT_PACKET_LOSS": "Packets are being lost on a path that otherwise looks quiet.",
    "LOADED_LATENCY_INFLATION": "The line is fine when idle and much slower while a download runs.",
    "NONE": "The numbers are missing, too small, or they disagree. No cause is named.",
}

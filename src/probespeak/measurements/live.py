"""Live adapters. They measure; they do not decide the cause."""
from __future__ import annotations

from ..bootstrap import install_agent

install_agent()

from probespeak_agent.engine.diagnose import diagnose  # noqa: E402
from probespeak_agent.measure import full  # noqa: E402
from probespeak_agent.models import to_wire  # noqa: E402
from probespeak_agent.runner import Runner  # noqa: E402

from .external import probe_targets  # noqa: E402
from .gateway_discover import discover_gateway  # noqa: E402

def run_live(include_tcp: bool = True, include_load: bool = True) -> dict:
    """Run the four instruments. Loaded latency runs only when include_load is true.

    include_load False skips the bulk transfer and records congestion as not measured,
    which the rule engine will call insufficient. Callers that want a verdict must
    leave include_load True and must have the user's consent for that transfer.
    """
    gateway = discover_gateway()
    runner = Runner()
    if include_load:
        measurement = full(runner, label="LIVE")
    else:
        from probespeak_agent.measure import verify_dns, verify_gateway, verify_packet_loss
        from probespeak_agent.models import MeasurementSet

        dns = verify_dns(runner)
        gw = verify_gateway(runner)
        loss = verify_packet_loss(runner)
        measurement = MeasurementSet(
            dns.id, "LIVE-LIGHT", "local_agent", dns.captured_at,
            gw.gateway, dns.dns, loss.packet_loss, dns.congestion,
        )
    tcp = probe_targets() if include_tcp else None
    diagnosis = diagnose(measurement)
    return {
        "mode": "live",
        "deviceChanged": False,
        "gatewayDiscovery": gateway,
        "tcp": tcp,
        "measurement": to_wire(measurement),
        "diagnosis": diagnosis,
        "verdict": diagnosis["preliminary"],
        "loadConsent": include_load,
    }

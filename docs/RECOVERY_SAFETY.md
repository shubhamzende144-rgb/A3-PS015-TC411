# Recovery safety

Default is read-only.

A change is attempted only when all of these are true:

- The run is live, not a lab scenario.
- The rule engine offered `FIX_DNS` or `RENEW_DHCP`.
- Settings has "Enable recovery changes" on.
- The Recovery page checkbox is on.
- The confirmation dialog is accepted.
- The action is on the agent allowlist. There is no action for an arbitrary command.

Lab mode raises before any of that and does not construct a live handler.

DNS save, apply, retest, and rollback stay in the existing agent controller. The desktop does not reimplement them. Resolved is still only the agent's decision after a clean retest.

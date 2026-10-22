# Lab Client Path, Policy NSG, and Application Gateway Rewrite Checks

Gotchas observed while verifying HTTP-layer behavior against a lab Application Gateway (WAF_v2). Observations are conditional on the stated environment; treat them as checks to repeat, not guarantees.

## Client path

- If the operator PC reaches the lab endpoint only intermittently (TLS reset after about 5 s, curl exit 35; ports 80/8080 never arrive; no access-log entry on the gateway), suspect a local network agent in the path (VPN, secure web gateway, Global Secure Access) before suspecting the gateway. Confirm with one request from inside Azure.
- Use a short-lived Azure-side client (a container group running curl) for HTTP, redirect, SNI and header checks. Loop it on a fixed period and log a timestamp, protocol, status, redirect target and Set-Cookie names only (never values).
- The client's real egress IP differs from the container group's public IP. Read it from inside the container (for example an IP-echo service) and allow only that /32 on the NSG. Delete the container group and the temporary rule together when finished.
- After every configuration switch, save the client log lines of the next full loop to the evidence folder before changing again. The container log keeps a limited tail, so earlier loops are lost; if a loop must be reconstructed from console output, name that evidence as a transcript.
- A browser result from the operator PC and a curl result from Azure answer different questions. Report an untested browser path as unverified, not as unaffected.

## Policy-attached NSG

- Governance policy can attach an NSG to the gateway subnet some time after creation (observed about 1 hour later, only AllowGatewayManager). Internet 443 is then denied, and stopping or starting the gateway does not help.
- Check the subnet NSG and the 443 rule at the start and again before each test session. Add a temporary rule scoped to the test source only, and remove it afterwards. Do not edit or delete the policy-created NSG itself.

## Preflight for public IP creation

- If Public IP creation fails with a subscription feature-not-registered error, check the feature state first. Register it only in an isolated lab subscription that you are authorized to change, and note how to unregister. Do not register it in other subscriptions.

## Application Gateway rewrite checks

- Multi-site (SNI) HTTPS listeners on a port that already has a basic rule need a routing-rule priority number lower than that basic rule; otherwise the basic rule matches every host.
- Redirect rules: binding a rewrite set to a rule or a path rule whose target is a redirect is accepted by ARM, but the rewrite is not applied (a marker header is absent; status and Location are unchanged). Use a marker-header rewrite set as a control. For path-based rules, a rule-level binding did not affect the default path; whether the path map's own default setting is the cause was not checked.
- Regex typed from a rendered page: compare the characters actually stored (length, double backslash, trailing space) with the intended string. ARM accepted a double-backslash form and a trailing-space form without a validation error. The double-backslash form matched nothing, so the mitigation silently did nothing; the trailing-space form matched like the original when the cookie continued with a space after the semicolon.
- A rewrite rule with a delete action on a Set-Cookie condition removed every Set-Cookie of a response when one of them matched, including unrelated cookies. Verify the documented "only matching headers" claim with a multi-cookie response instead of assuming it.
- A URL-rewrite action with no condition changed every request path; with a Set-Cookie response condition it was accepted but not applied. WAF rules can return 403 for long Set-Cookie values independent of rewriting; check a no-rewrite baseline first.
- For each case record: whether ARM accepted it, status code, redirect target, marker header present or absent, Set-Cookie names kept or removed, protocol version. Finish with a rollback check that repeats the baseline requests.

# Flow Migration and Cleanup Runbook

Use this runbook to rebuild a cloud flow in another environment, switch over, and remove the old version. Prefer an API or CLI for any step it can complete; use the browser UI for the rest.

## Workflow

1. **Save the original.** Before any change, save the old flow's definition (trigger, form ID, question IDs, message body, destination) as JSON and do not modify it afterwards.
2. **Choose the target environment.** Confirm that it fits the purpose and permissions. Do not reuse another person's environment of unknown purpose. Creating an environment or changing permissions, sharing or DLP needs the target and impact shown and individual approval.
3. **Rebuild.** Keep question values and destinations identical to the old flow and make each notification appear once. After saving, read the definition back and compare it with the original (a check script makes this reusable).
4. **Verify behavior.** With an approved real submission explicitly labeled as a test, confirm that only the new flow posts exactly one notification. An empty run history or a run stuck at Started is not evidence of success.
5. **Switch over.** Confirm independently that the new flow is On and the old flow is Off, and that no duplicate notification occurs.
6. **Delete the old flow.** Deletion cannot be undone and removes its run history. Delete only approved targets, after confirming the name and the Off state; confirm the dialog title is the target flow name; read the list back to confirm it is gone. Keep the saved original.

## Stop Conditions

- If DLP or ACP rejects the same save or connection operation, do not retry it. Switch to rebuilding in another environment and never work around the rejection by another route.
- Passwords and MFA are the user's to enter. Do not run, stop or delete unapproved targets (helper flows, unrelated environments, other people's flows).

## Operating Notes

- **Slow or stale screens:** wait 60-240 seconds and recheck the heading and state before acting. "Unable to adopt element handle" after a click usually means the page already navigated; confirm with persistent state (the list, the saved definition) and never resend the same write.
- **Draft.js inputs:** plain typing can append. Select the field and replace its content, then read it back from the saved definition.
- **Co-owners:** on the flow's owners screen, type a name or email, confirm that exactly one candidate matches the email, then add it. Read the connection-sharing dialog before confirming. After adding, reload the page and check the owner count. The person's own consent and connection continuity (for example when the original owner leaves) are separate matters to record.
- **Dataverse for Teams:** new environment creation ends on 2026-11-15, environments that are not upgraded are stopped on 2027-09-15, and the product is retired on 2027-10-30 (upgrading remains possible after the stop). A tenant admin upgrades in the admin center; it needs free Dataverse capacity at least the environment size and the right licenses for the flows afterwards. Source: learn.microsoft.com/power-platform/important-changes-coming (recheck before relying on the dates).

## Done Criteria

- The rebuilt flow's saved definition was read back and matches the original.
- A real test submission produced a notification from the new flow only.
- The old flow is Off, and after deletion it is gone from the list.
- The location of the original and evidence, and any target not yet deleted (awaiting approval), are reported.

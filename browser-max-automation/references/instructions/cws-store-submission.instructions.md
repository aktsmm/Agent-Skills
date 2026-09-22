# CWS Submission Without CDP

Use this fallback only when a normal Chromium window is already authenticated to the Chrome Web Store Dashboard and no suitable API, MCP, or CDP route exists.

1. Pin one browser process, top-level window, selected address-bar value, publisher route, and item ID. Exclude unrelated browser sessions by PID, `user-data-dir`, and URL. Do not restart the browser, copy a profile, or handle credentials.
2. Attach Windows UI Automation read-only first. If browser chrome appears without `RootWebArea`, verify that the exact CWS page has no unsaved work, invoke Reload once, and require `RootWebArea` before any write.
3. Use `ValuePattern`, `InvokePattern`, `ExpandCollapsePattern`, and `TogglePattern`; do not use coordinates, OS keystrokes, or the clipboard. Re-resolve controls after each SPA update because automation IDs can change.
4. Accept a native file chooser only when it is the visible `Open` dialog owned by a child of the pinned browser and the matched browser window is disabled by that modal. Hash the artifact before selecting it.
5. CWS image deletion has a separate confirmation. Delete and confirm one image at a time. A multi-file choice may add only its first image, so upload remaining screenshots individually and verify the count after each upload.
6. Save the draft, navigate away and back, then re-read both locale descriptions and compare normalized-newline hashes to the source. Recheck package version and screenshot count.
7. The first **Submit for review** opens a confirmation. Verify product name and auto-publish state before confirming. Do not retry until readback proves non-application.
8. Completion requires the Dashboard item to show the expected version and **Pending review**. Keep upload, draft save, submission, review approval, and public availability as separate states.

This workflow does not make UIA a security boundary. Stop on an ambiguous window, item, modal, control, or post-write state.
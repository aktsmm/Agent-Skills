# Angular Material Automation Notes

Use this for Angular Material forms using `mat-select`, `mat-dialog`, `cdk-overlay`, or reactive form validation.

## mat-select

- Do not use native input value setters for `mat-select`; they do not update Angular form state.
- Click `.mat-select-trigger`, choose a visible `[role="option"]`, then verify the form state.
- For similar labels, prefer exact text match. `Delivery` and `(ISD only) Delivery` are easy to confuse with partial matching.

```javascript
const options = [...document.querySelectorAll('[role="option"]')].filter(option => option.offsetParent);
const exact = options.find(option => option.innerText.trim() === 'Delivery');
if (exact) exact.click();
```

## Overlays and Dialogs

- `cdk-global-overlay-wrapper` can remain after selection and block later clicks. Send `Escape` or click the next trigger directly.
- Scope all form queries to the active visible overlay/dialog. A broad `document.querySelector('form')` can grab an old dialog.

```javascript
const overlays = [...document.querySelectorAll('.cdk-overlay-pane, mat-dialog-container')]
  .filter(dialog => dialog.offsetParent);
const activeForm = overlays[overlays.length - 1]?.querySelector('form');
```

## Save Buttons

- A button can be enabled while the form silently fails validation. Verify persisted state after clicking.
- Before bulk `page.evaluate` actions, reset date/tab/filter selection and close leftover overlays.
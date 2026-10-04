# TreeView Implementation

Sidebar entry points and tree views for a VS Code extension.

## package.json Configuration

```json
"contributes": {
  "viewsContainers": {
    "activitybar": [{
      "id": "myExtContainer",
      "title": "My Extension",
      "icon": "images/icon.svg"
    }]
  },
  "views": {
    "myExtContainer": [{
      "id": "myExtView",
      "name": "Items"
    }]
  }
}
```

**View locations:**

| Container  | Description             |
| ---------- | ----------------------- |
| `explorer` | File Explorer sidebar   |
| `scm`      | Source Control sidebar  |
| `debug`    | Debug sidebar           |
| `test`     | Testing sidebar         |
| Custom ID  | Activity bar (new icon) |

## Entry Point and Upgrade Checks

- The manifest's top-level `icon` is for the listing. A left-hand entry needs `viewsContainers.activitybar` and `views[containerId]`; `views.explorer` places the view inside Explorer without a separate Activity Bar icon.
- Use a monochrome SVG, conventionally with a 24-by-24 viewBox, for the Activity Bar. Keep its path distinct from the listing PNG and verify that the actual VSIX contains the referenced file.
- Provide the primary management action in `view/title`, with a recognizable command icon, a view-specific `when` clause and English/Japanese labels; retain the Command Palette route.
- Preserve existing view IDs when relocating a view. VS Code may retain customized placements: offer Move View or enabling a hidden Activity Bar item first. Reset View Locations affects all views; explain its scope and never invoke it silently.
- Test manifest/container/view agreement and real container-open/view-focus commands in an isolated Extension Host. Opening navigation must not execute user tasks. A source edit is not an installed update; verify the intended installed version before diagnosing a missing icon.

## Implementation Notes

The `TreeDataProvider` / `createTreeView` API follows the official [Tree View guide](https://code.visualstudio.com/api/extension-guides/tree-view). Project rules:

- Prefer `vscode.window.createTreeView(id, { treeDataProvider, showCollapseAll })` over `registerTreeDataProvider` when you need `visible`, `reveal` or selection; push it to `context.subscriptions`.
- Refresh through an `EventEmitter` exposed as `onDidChangeTreeData`.
- Use codicons via `new vscode.ThemeIcon("<name>")` for item icons.
- Context menus go under `menus["view/item/context"]` with `when: "view == <viewId> && viewItem == <contextValue>"`.

## Production Contracts

- Custom `viewsContainers` IDs should use only letters, digits, `_`, and `-`; invalid IDs can be rejected or ignored by contribution validation. Prefix IDs for uniqueness, keep published IDs stable, and verify the container in an Extension Host.
- If clicking or pressing Enter must perform a specific action, set `TreeItem.command` with the node in `arguments`; do not rely on implicit expand behavior. Resolve the node's durable ID against current data before acting so a stale item cannot target a different record.
- Set `TreeItem.id` from a durable model key, not its label. Give child/detail rows deterministic IDs such as `<kind>:<parent-id>:<field>` and implement `getParent` when commands use `TreeView.reveal` or expansion state must survive refreshes.
- Use distinct `contextValue` values for item capabilities (for example, `item` and `itemWithAlias`) and match them in `view/item/context` `when` clauses. Hide commands that require a selected item from the Command Palette with a `menus.commandPalette` entry such as `{ "command": "myExt.itemAction", "when": "false" }`.
- For labels that age without data changes, refresh only while `TreeView.visible` is true. Apply the initial `treeView.visible` value after listener registration, stop timers when hidden, and cancel them again during disposal.
- Activity Bar SVGs should use `currentColor` rather than a fixed stroke/fill so light, dark, and high-contrast themes remain readable.

## Runtime Contract Tests

Test the provider itself inside an Extension Host, not only manifest strings. Assert:

- parent and detail `collapsibleState`, stable IDs, `contextValue`, tooltip, and accessibility label/role;
- `TreeItem.command.command` and the exact node passed in `arguments`;
- child count/order and `getParent(child)` returning the matching parent item whose durable ID is stable;
- `onDidChangeTreeData` firing for data replacement and presentation-only refresh;
- visible-only refresh scheduling and hidden/dispose cancellation; when labels are time-based, also test the rendered value across a time boundary.

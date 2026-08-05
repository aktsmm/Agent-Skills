# TreeView Implementation

Create sidebar views for your VS Code extension.

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

## TreeDataProvider Implementation

```typescript
import * as vscode from "vscode";

// Tree item class
class MyItem extends vscode.TreeItem {
  constructor(
    public readonly label: string,
    public readonly collapsibleState: vscode.TreeItemCollapsibleState,
    public readonly children?: MyItem[],
  ) {
    super(label, collapsibleState);
    this.tooltip = this.label;
    this.contextValue = "myItem"; // For context menu
  }
}

// Provider class
class MyTreeProvider implements vscode.TreeDataProvider<MyItem> {
  // Event emitter for refresh
  private _onDidChangeTreeData = new vscode.EventEmitter<MyItem | undefined>();
  readonly onDidChangeTreeData = this._onDidChangeTreeData.event;

  private data: MyItem[] = [
    new MyItem("Parent", vscode.TreeItemCollapsibleState.Expanded, [
      new MyItem("Child 1", vscode.TreeItemCollapsibleState.None),
      new MyItem("Child 2", vscode.TreeItemCollapsibleState.None),
    ]),
  ];

  refresh(): void {
    this._onDidChangeTreeData.fire(undefined);
  }

  getTreeItem(element: MyItem): vscode.TreeItem {
    return element;
  }

  getChildren(element?: MyItem): MyItem[] {
    return element ? element.children || [] : this.data;
  }
}
```

## Registration in extension.ts

```typescript
export function activate(context: vscode.ExtensionContext) {
  const provider = new MyTreeProvider();

  // Register provider
  vscode.window.registerTreeDataProvider("myExtView", provider);

  // Or use createTreeView for more control
  const treeView = vscode.window.createTreeView("myExtView", {
    treeDataProvider: provider,
    showCollapseAll: true,
  });
  context.subscriptions.push(treeView);

  // Refresh command
  context.subscriptions.push(
    vscode.commands.registerCommand("myExt.refresh", () => provider.refresh()),
  );
}
```

## Item Customization

```typescript
class MyItem extends vscode.TreeItem {
  constructor(label: string, isFolder: boolean) {
    super(
      label,
      isFolder
        ? vscode.TreeItemCollapsibleState.Collapsed
        : vscode.TreeItemCollapsibleState.None,
    );

    // Icon (codicon or file path)
    this.iconPath = new vscode.ThemeIcon(isFolder ? "folder" : "file");

    // Click action
    this.command = {
      command: "myExt.openItem",
      title: "Open",
      arguments: [this],
    };

    // Description (gray text after label)
    this.description = "(modified)";
  }
}
```

## Context Menu

```json
"contributes": {
  "menus": {
    "view/item/context": [{
      "command": "myExt.delete",
      "when": "view == myExtView && viewItem == myItem"
    }]
  }
}
```

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

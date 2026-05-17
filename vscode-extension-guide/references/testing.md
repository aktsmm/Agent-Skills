# Testing VS Code Extensions

Set up and run tests using @vscode/test-electron.

## Setup

```bash
npm install -D @vscode/test-electron mocha @types/mocha glob
```

## Project Structure

```
my-extension/
├── src/
│   └── extension.ts
├── test/
│   ├── runTest.ts           # Test runner entry
│   └── suite/
│       ├── index.ts         # Mocha configuration
│       └── extension.test.ts # Test file
├── tsconfig.json
└── tsconfig.test.json
```

## tsconfig.test.json

```json
{
  "extends": "./tsconfig.json",
  "compilerOptions": {
    "rootDir": ".",
    "outDir": "out"
  },
  "include": ["src/**/*", "test/**/*"]
}
```

## test/runTest.ts

```typescript
import * as path from "path";
import { runTests } from "@vscode/test-electron";

async function main() {
  try {
    const extensionDevelopmentPath = path.resolve(__dirname, "../../");
    const extensionTestsPath = path.resolve(__dirname, "./suite/index");

    await runTests({
      extensionDevelopmentPath,
      extensionTestsPath,
      // Optional: specify VS Code version
      // version: '1.85.0',
      // Optional: open specific workspace
      // launchArgs: ['--disable-extensions', path.resolve(__dirname, '../../test-workspace')],
    });
  } catch (err) {
    console.error("Failed to run tests");
    process.exit(1);
  }
}

main();
```

## test/suite/index.ts

```typescript
import * as path from "path";
import Mocha from "mocha";
import { glob } from "glob";

export async function run(): Promise<void> {
  const mocha = new Mocha({
    ui: "tdd",
    color: true,
    timeout: 10000,
  });

  const testsRoot = path.resolve(__dirname, ".");
  const files = await glob("**/**.test.js", { cwd: testsRoot });

  files.forEach((f) => mocha.addFile(path.resolve(testsRoot, f)));

  return new Promise((resolve, reject) => {
    mocha.run((failures) => {
      if (failures > 0) {
        reject(new Error(`${failures} tests failed.`));
      } else {
        resolve();
      }
    });
  });
}
```

## test/suite/extension.test.ts

```typescript
import * as assert from "assert";
import * as vscode from "vscode";

suite("Extension Test Suite", () => {
  vscode.window.showInformationMessage("Start all tests.");

  test("Extension should be present", () => {
    const ext = vscode.extensions.getExtension("publisher.extension-name");
    assert.ok(ext, "Extension not found");
  });

  test("Extension should activate", async () => {
    const ext = vscode.extensions.getExtension("publisher.extension-name");
    await ext?.activate();
    assert.ok(ext?.isActive, "Extension not activated");
  });

  test("Command should be registered", async () => {
    const commands = await vscode.commands.getCommands();
    assert.ok(commands.includes("myExt.hello"), "Command not registered");
  });

  test("Command should execute without error", async () => {
    await assert.doesNotReject(vscode.commands.executeCommand("myExt.hello"));
  });
});
```

## package.json Scripts

```json
{
  "scripts": {
    "compile": "tsc -p ./",
    "compile-tests": "tsc -p tsconfig.test.json",
    "pretest": "npm run compile && npm run compile-tests",
    "test": "node ./out/test/runTest.js"
  }
}
```

## Running Tests

```bash
# Run all tests
npm test

# Tests will:
# 1. Download VS Code (if needed)
# 2. Launch VS Code with extension loaded
# 3. Execute test suite
# 4. Exit with result code
```

## Risk-Based Regression Checks

Run a full compile first, then add targeted checks based on what changed.

| Change area                                   | Extra checks                                                                                                                                                                                                                                         |
| --------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Commands / settings / views in `package.json` | Verify manifest consistency, command IDs, setting keys, menu `when` clauses, and README setting tables                                                                                                                                               |
| `package.nls.json` or localized manifest text | Compare all localized key sets and confirm missing keys fail tests                                                                                                                                                                                   |
| Runtime logging / diagnostics                 | Verify logs go through an Output Channel logger instead of direct `console.*` calls in extension runtime paths                                                                                                                                       |
| Resource scanners / providers                 | Test with extension-host APIs available and with missing/empty roots; avoid relying on local filesystem guesses; if you scan installed extensions, cover both known `resources/*` roots and manifest-declared `chatAgents` / `chatPromptFiles` paths |
| Installer / updater / index merge logic       | Run focused regression scripts plus a broader smoke test because these paths often cross manifest, filesystem, and network boundaries                                                                                                                |
| Generated marker sections                     | Test duplicate marker handling and confirm the final file contains exactly one generated section pair                                                                                                                                                |

For small fixes, a good baseline is `npm run compile` plus the smallest script or test file that exercises the changed behavior. For shared manifest, installer, updater, or scanner code, prefer adding one regression test over relying only on manual verification.

## Common Test Patterns

### Testing with Documents

```typescript
test("Should modify document", async () => {
  const doc = await vscode.workspace.openTextDocument({
    content: "hello",
    language: "plaintext",
  });
  const editor = await vscode.window.showTextDocument(doc);

  await editor.edit((editBuilder) => {
    editBuilder.insert(new vscode.Position(0, 5), " world");
  });

  assert.strictEqual(doc.getText(), "hello world");
});
```

### Testing Settings

```typescript
test("Should read configuration", () => {
  const config = vscode.workspace.getConfiguration("myExt");
  const value = config.get<string>("greeting");
  assert.strictEqual(value, "Hello");
});
```

### Waiting for Events

```typescript
test("Should handle file save", async () => {
  const doc = await vscode.workspace.openTextDocument({ content: "test" });

  const savePromise = new Promise<void>((resolve) => {
    const disposable = vscode.workspace.onDidSaveTextDocument((saved) => {
      if (saved === doc) {
        disposable.dispose();
        resolve();
      }
    });
  });

  await doc.save();
  await savePromise;
});
```

## CI Integration

**.github/workflows/test.yml:**

```yaml
name: Test
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - run: npm ci
      - run: xvfb-run -a npm test
```

Note: `xvfb-run` is required on Linux for headless VS Code testing.

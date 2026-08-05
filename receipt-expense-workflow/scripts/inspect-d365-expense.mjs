/** Dynamics 365 Expense - current report state inspector (read-only). */
import { createRequire } from "node:module";
import { join } from "node:path";
import { pathToFileURL } from "node:url";

const CDP_URL = process.env.D365_CDP_URL ?? "http://localhost:9222";
const reportArgIndex = process.argv.indexOf("--report");
const requestedReport =
  reportArgIndex >= 0 ? process.argv[reportArgIndex + 1] : "";

function loadPlaywright() {
  try {
    return createRequire(import.meta.url)("playwright");
  } catch (skillError) {
    try {
      return createRequire(join(process.cwd(), "package.json"))("playwright");
    } catch {
      throw new Error(
        `Playwright is required in the skill or current project: ${skillError.message}`,
      );
    }
  }
}

async function findD365Page(browser, timeoutMs = 5000) {
  const deadline = Date.now() + timeoutMs;
  do {
    const page = browser
      .contexts()
      .flatMap((context) => context.pages())
      .find((candidate) =>
        candidate.url().includes("myexpense.operations.dynamics.com"),
      );
    if (page) return page;
    await new Promise((resolve) => setTimeout(resolve, 250));
  } while (Date.now() < deadline);
  return null;
}

async function openRequestedReport(page, reportNumber) {
  if (!reportNumber) return;
  if (!/^[A-Z0-9-]+$/.test(reportNumber)) {
    throw new Error("Invalid --report value.");
  }
  if (
    (await page
      .locator(`form[aria-label*="${reportNumber}"]:visible`)
      .count()) > 0
  ) {
    return;
  }

  const reportsTabs = page.getByRole("tab", { name: "Reports", exact: true });
  for (let index = 0; index < (await reportsTabs.count()); index += 1) {
    const tab = reportsTabs.nth(index);
    if (await tab.isVisible()) {
      await tab.click();
      break;
    }
  }

  const reportInputs = page.locator(
    '[aria-label="Expense report number"]:visible',
  );
  await reportInputs.first().waitFor({ state: "visible", timeout: 5000 });
  let target = null;
  for (let index = 0; index < (await reportInputs.count()); index += 1) {
    const input = reportInputs.nth(index);
    if ((await input.inputValue()) === reportNumber) {
      target = input;
      break;
    }
  }
  if (!target) throw new Error(`Expense report not found: ${reportNumber}`);
  await target.click();
  await page
    .locator(`form[aria-label*="${reportNumber}"]:visible`)
    .waitFor({ state: "visible", timeout: 5000 });
}

async function inspectLines(page, formLabel) {
  return page.evaluate((expectedFormLabel) => {
    const root = Array.from(document.querySelectorAll("form")).find(
      (element) =>
        element.offsetParent !== null &&
        element.getAttribute("aria-label") === expectedFormLabel,
    );
    if (!root) return [];
    const value = (row, label) => {
      const element = row.querySelector(`[aria-label="${label}"]`);
      return (element?.value || element?.textContent || "").trim();
    };
    return Array.from(root.querySelectorAll('[role="row"]'))
      .map((row) => ({
        date: value(row, "Date"),
        category: value(row, "Expense category"),
        merchant: value(row, "Merchant"),
        amount: value(row, "Amount"),
        receiptsAttached: value(row, "Receipts attached"),
        policyCompliant: Boolean(
          row.querySelector(
            '[aria-label*="This expense does not have any policy violations."]',
          ),
        ),
      }))
      .filter((row) => row.amount && row.merchant);
  }, formLabel);
}

async function inspectReceiptCards(page, formLabel) {
  return page.evaluate((expectedFormLabel) => {
    const root = Array.from(document.querySelectorAll("form")).find(
      (element) =>
        element.offsetParent !== null &&
        element.getAttribute("aria-label") === expectedFormLabel,
    );
    if (!root) return [];
    return Array.from(root.querySelectorAll('[id^="ExpenseReportGroup_"]'))
      .filter((card) => card.offsetParent !== null)
      .map((card) => {
        const value = (label) =>
          (card.querySelector(`[aria-label="${label}"]`)?.value || "").trim();
        const checkbox = card.querySelector('[role="checkbox"]');
        return {
          fileName: value("File name"),
          attachmentStatus: value("getAttachmentStatus"),
          note: value("Note"),
          selected: checkbox?.getAttribute("aria-checked") === "true",
        };
      });
  }, formLabel);
}

export function classifyReceiptCards(cards) {
  const attachedNames = new Set(
    cards
      .filter((card) => card.attachmentStatus === "Attached to expense")
      .map((card) => card.fileName),
  );
  return {
    safeDuplicateCandidates: cards.filter(
      (card) => !card.attachmentStatus && attachedNames.has(card.fileName),
    ),
    reviewCandidates: cards.filter(
      (card) => !card.attachmentStatus && !attachedNames.has(card.fileName),
    ),
  };
}

async function main() {
  const { chromium } = loadPlaywright();
  const browser = await chromium.connectOverCDP(CDP_URL, { timeout: 15000 });
  const page = await findD365Page(browser);
  if (!page) {
    throw new Error("No D365 Expense page is open on the CDP endpoint.");
  }

  const bodyText = await page.locator("body").innerText();
  if (
    page.url().includes("login.microsoftonline.com") ||
    bodyText.includes("Session ended")
  ) {
    throw new Error(
      "D365 session is not active; reauthenticate before inspection.",
    );
  }

  await openRequestedReport(page, requestedReport);

  const report = await page.evaluate(() => {
    const form = Array.from(document.querySelectorAll("form")).find(
      (element) =>
        element.offsetParent !== null &&
        (element.getAttribute("aria-label") || "").startsWith(
          "Expense report:",
        ),
    );
    const value = (label) => {
      const scoped = form?.querySelector(`[aria-label="${label}"]`);
      const fieldName = label === "Status" ? "ReportStatus" : "";
      const named = fieldName
        ? form?.querySelector(`[name="${fieldName}"]`)
        : null;
      const element =
        scoped ||
        named ||
        Array.from(document.querySelectorAll(`[aria-label="${label}"]`)).find(
          (candidate) => candidate.offsetParent !== null,
        );
      return (element?.value || element?.textContent || "").trim();
    };
    return {
      formLabel: form?.getAttribute("aria-label") || "",
      status: value("Status"),
      toBePaid: value("To be paid"),
      receiptCount: value("Receipts"),
      finalApprover: value("Final approver"),
    };
  });

  const initialTab = await page
    .locator('[role="tab"][aria-selected="true"]')
    .first()
    .textContent()
    .catch(() => "");
  const expensesTab = page.getByRole("tab", { name: "Expenses", exact: true });
  const receiptsTab = page.getByRole("tab", { name: "Receipts", exact: true });

  let lines = [];
  let receiptCards = [];
  const reportOpen = report.formLabel.startsWith("Expense report:");
  if (reportOpen && (await expensesTab.count()) > 0) {
    await expensesTab.click();
    await page
      .getByRole("tabpanel", { name: "Expenses", exact: true })
      .waitFor({ state: "visible", timeout: 5000 });
    lines = await inspectLines(page, report.formLabel);
  }
  if (reportOpen && (await receiptsTab.count()) > 0) {
    await receiptsTab.click();
    await page
      .getByRole("tabpanel", { name: "Receipts", exact: true })
      .waitFor({ state: "visible", timeout: 5000 });
    receiptCards = await inspectReceiptCards(page, report.formLabel);
  }

  if (initialTab === "Expenses" && (await expensesTab.count()) > 0) {
    await expensesTab.click();
  } else if (initialTab === "Receipts" && (await receiptsTab.count()) > 0) {
    await receiptsTab.click();
  }

  const cleanup = classifyReceiptCards(receiptCards);
  const result = {
    inspectedAt: new Date().toISOString(),
    page: { url: page.url(), title: await page.title() },
    report,
    lines,
    receiptCards,
    cleanup,
    checks: {
      allLinesHaveReceipts:
        lines.length > 0 &&
        lines.every((line) => line.receiptsAttached === "Yes"),
      allLinesPolicyCompliant:
        lines.length > 0 && lines.every((line) => line.policyCompliant),
      allCardsAttached:
        receiptCards.length > 0 &&
        receiptCards.every(
          (card) => card.attachmentStatus === "Attached to expense",
        ),
      noSelectedCards: receiptCards.every((card) => !card.selected),
    },
  };
  process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
  process.exit(0);
}

const isMain =
  process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href;
if (isMain) {
  main().catch((error) => {
    process.stderr.write(
      `${JSON.stringify({ status: "error", error: error.message })}\n`,
    );
    process.exit(1);
  });
}

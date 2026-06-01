import http.client
import json
import os
import shutil
import subprocess
import sys
import urllib.parse
from collections import defaultdict


def get_access_token() -> str:
    token_from_env = os.environ.get("AZURE_ACCESS_TOKEN")
    if token_from_env:
        return token_from_env.strip()

    az_executable = shutil.which("az.cmd") or shutil.which("az.exe") or shutil.which("az")
    if not az_executable:
        raise FileNotFoundError("Azure CLI executable was not found in PATH.")

    result = subprocess.run(
        [
            az_executable,
            "account",
            "get-access-token",
            "--resource",
            "https://management.azure.com/",
            "--query",
            "accessToken",
            "-o",
            "tsv",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def fetch_json(connection: http.client.HTTPSConnection, url: str, token: str) -> dict:
    if url.startswith("/"):
        request_target = url
    else:
        parsed_url = urllib.parse.urlsplit(url)
        request_target = parsed_url.path
        if parsed_url.query:
            request_target += "?" + parsed_url.query

    request_target = request_target.replace(" ", "%20")

    connection.request("GET", request_target, headers={"Authorization": f"Bearer {token}"})
    response = connection.getresponse()
    payload = response.read()

    if response.status >= 400:
        raise RuntimeError(payload.decode("utf-8", errors="replace"))

    return json.loads(payload.decode("utf-8"))


def build_initial_url(subscription_id: str, start_date: str, end_date: str, page_size: int) -> str:
    filter_value = f"properties/usageStart ge '{start_date}' and properties/usageEnd le '{end_date}'"
    query = urllib.parse.urlencode(
        {
            "metric": "ActualCost",
            "$filter": filter_value,
            "$top": str(page_size),
            "api-version": "2019-10-01",
        }
    )
    return (
        f"https://management.azure.com/subscriptions/{subscription_id}"
        f"/providers/Microsoft.Consumption/usageDetails?{query}"
    )


def main() -> int:
    if len(sys.argv) != 5:
        print(
            "Usage: py -3 scripts/get-legacy-usage-summary.py <subscription_id> <start_date> <end_date> <output_path>",
            file=sys.stderr,
        )
        return 2

    subscription_id, start_date, end_date, output_path = sys.argv[1:5]
    token = get_access_token()
    next_url = build_initial_url(subscription_id, start_date, end_date, 100)
    connection = http.client.HTTPSConnection("management.azure.com", timeout=60)

    total_cost = 0.0
    currency = None
    item_count = 0
    page_count = 0
    service_totals = defaultdict(float)

    try:
        while next_url:
            print(f"FETCH_PAGE={page_count + 1}", flush=True)
            payload = fetch_json(connection, next_url, token)
            page_count += 1
            print(f"PAGE_ITEMS={len(payload.get('value', []))}", flush=True)

            for item in payload.get("value", []):
                properties = item.get("properties", {})
                cost = float(properties.get("cost") or 0.0)
                service_name = (
                    properties.get("consumedService")
                    or properties.get("product")
                    or properties.get("resourceName")
                    or "Unknown"
                )
                billing_currency = properties.get("billingCurrency")

                total_cost += cost
                service_totals[service_name] += cost
                item_count += 1

                if not currency and billing_currency:
                    currency = billing_currency

            next_url = payload.get("nextLink")
    finally:
        connection.close()

    top_services = [
        {
            "serviceName": service_name,
            "cost": round(cost, 4),
        }
        for service_name, cost in sorted(service_totals.items(), key=lambda pair: pair[1], reverse=True)[:10]
    ]

    summary = {
        "subscriptionId": subscription_id,
        "startDate": start_date,
        "endDate": end_date,
        "currency": currency,
        "totalCost": round(total_cost, 4),
        "itemCount": item_count,
        "pageCount": page_count,
        "topServices": top_services,
    }

    with open(output_path, "w", encoding="utf-8") as file_handle:
        json.dump(summary, file_handle, ensure_ascii=False, indent=2)

    print(f"TOTAL={summary['totalCost']}")
    print(f"CURRENCY={summary['currency']}")
    print(f"ITEMS={summary['itemCount']}")
    print(f"PAGES={summary['pageCount']}")
    for index, item in enumerate(top_services, start=1):
        print(f"TOP{index}={item['serviceName']}|{item['cost']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

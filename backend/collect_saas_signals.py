import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

NIMBLE_API_KEY = os.getenv("NIMBLE_API_KEY")
NIMBLE_ENDPOINT = "https://api.nimbleway.com/api/v1/"

COMPETITORS = {
    "Notion": {
        "pricing": "https://www.notion.so/pricing",
        "reviews": "https://www.g2.com/products/notion/reviews",
        "activity": "https://www.notion.so/careers",
        "case_studies": "https://www.notion.so/customers"
    },
    "HubSpot": {
        "pricing": "https://www.hubspot.com/pricing",
        "reviews": "https://www.g2.com/products/hubspot/reviews",
        "activity": "https://www.hubspot.com/careers",
        "case_studies": "https://www.hubspot.com/case-studies"
    },
    "Airtable": {
        "pricing": "https://www.airtable.com/pricing",
        "reviews": "https://www.g2.com/products/airtable/reviews",
        "activity": "https://www.airtable.com/careers",
        "case_studies": "https://www.airtable.com/customers"
    },
    "Asana": {
        "pricing": "https://asana.com/pricing",
        "reviews": "https://www.g2.com/products/asana/reviews",
        "activity": "https://asana.com/jobs",
        "case_studies": "https://asana.com/customers"
    },
    "Monday": {
        "pricing": "https://monday.com/pricing",
        "reviews": "https://www.g2.com/products/monday-com/reviews",
        "activity": "https://monday.com/careers",
        "case_studies": "https://monday.com/customers"
    }
}


def scrape_with_nimble(url: str) -> dict:
    if not NIMBLE_API_KEY:
        raise ValueError("Missing NIMBLE_API_KEY in .env")

    try:
        response = requests.post(
            NIMBLE_ENDPOINT,
            headers={
                "Authorization": f"Bearer {NIMBLE_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "url": url,
                "render": True
            },
            timeout=30
        )

        print("\n========================")
        print("SCRAPING URL:", url)
        print("STATUS CODE:", response.status_code)
        print("RAW RESPONSE PREVIEW:")
        print(response.text[:1000])
        print("========================\n")

        try:
            data = response.json()
        except Exception as json_error:
            return {
                "success": False,
                "status_code": response.status_code,
                "url": url,
                "error": f"JSON parse failed: {json_error}",
                "raw_response": response.text[:3000]
            }

        return {
            "success": True,
            "status_code": response.status_code,
            "url": url,
            "data": data
        }

    except requests.exceptions.Timeout:
        return {
            "success": False,
            "url": url,
            "error": "Request timed out"
        }

    except Exception as e:
        return {
            "success": False,
            "url": url,
            "error": str(e)
        }


def extract_text(nimble_response: dict) -> str:
    if not nimble_response.get("success"):
        return ""

    data = nimble_response.get("data", {})

    for key in ["text", "content", "body", "html"]:
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return value[:8000]

    return json.dumps(data)[:8000]


def collect_all_signals():
    results = []

    for company, sources in COMPETITORS.items():
        for signal_type, url in sources.items():
            print(f"Scraping {company} | {signal_type} | {url}")

            nimble_response = scrape_with_nimble(url)

            if not nimble_response.get("success"):
                results.append({
                    "company": company,
                    "signal_type": signal_type,
                    "source_url": url,
                    "scraped_at": datetime.utcnow().isoformat(),
                    "status_code": nimble_response.get("status_code"),
                    "error": nimble_response.get("error"),
                    "raw_response": nimble_response.get("raw_response", "")
                })
                continue

            raw_text = extract_text(nimble_response)

            results.append({
                "company": company,
                "signal_type": signal_type,
                "source_url": url,
                "scraped_at": datetime.utcnow().isoformat(),
                "status_code": nimble_response["status_code"],
                "raw_text": raw_text
            })

    return results


if __name__ == "__main__":
    data = collect_all_signals()

    with open("saas_competitor_signals.json", "w") as f:
        json.dump(data, f, indent=2)

    print("Done. Saved to saas_competitor_signals.json")
from nimble_python import Nimble
from dotenv import load_dotenv
from datetime import datetime
import os
import json

load_dotenv()

api_key = os.getenv("NIMBLE_API_KEY")

if not api_key:
    raise ValueError("Missing NIMBLE_API_KEY in .env")

nimble = Nimble(api_key=api_key)

# --------------------------------------------------
# CONFIG
# --------------------------------------------------

COMPETITORS = {
    "HubSpot": {
        "domain": "hubspot.com"
    },
    "Salesforce": {
        "domain": "salesforce.com"
    },
    "Notion": {
        "domain": "notion.so"
    },
    "Intercom": {
        "domain": "intercom.com"
    },
    "Monday.com": {
        "domain": "monday.com"
    }
}

REVIEW_DOMAINS = [
    "g2.com",
    "capterra.com",
    "trustradius.com"
]

ACTIVITY_DOMAINS = [
    "linkedin.com",
    "indeed.com",
    "greenhouse.io",
    "lever.co"
]

DATA_DIR = "data"


# --------------------------------------------------
# HELPERS
# --------------------------------------------------

def now_clickhouse():
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")


def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def safe_search(query, domains, search_depth="deep", time_range="month"):
    try:
        print(f"\nSearching: {query}")
        print(f"Domains: {domains}")

        result = nimble.search(
            query=query,
            include_domains=domains,
            search_depth=search_depth,
            time_range=time_range
        )

        return {
            "success": True,
            "result": result
        }

    except Exception as e:
        print("Search error:", e)

        return {
            "success": False,
            "error": str(e)
        }


def save_json(filename, rows):
    ensure_data_dir()

    path = os.path.join(DATA_DIR, filename)

    with open(path, "w") as f:
        json.dump(rows, f, indent=2, default=str)

    print(f"Saved {len(rows)} rows to {path}")


def result_to_text(search_result):
    """
    Converts Nimble result into text.
    This keeps your code safe even if Nimble returns different object formats.
    """
    try:
        return json.dumps(search_result, default=str)[:5000]
    except Exception:
        return str(search_result)[:5000]


# --------------------------------------------------
# TABLE 1: PRICING
# Schema:
# competitor_name, tier_name, price_usd,
# billing_frequency, free_trial, scraped_at
# --------------------------------------------------

def collect_pricing_rows():
    rows = []

    for competitor_name, config in COMPETITORS.items():
        domain = config["domain"]

        query = (
            f"{competitor_name} pricing update OR pricing change OR price increase "
            f"OR discount OR new pricing tier OR enterprise pricing OR free trial"
        )

        search = safe_search(
            query=query,
            domains=[domain],
            search_depth="deep",
            time_range="month"
        )

        raw_text = result_to_text(search)

        # Placeholder values for now.
        # Later Lapdog should extract the real tier_name, price_usd, etc. from raw_text.
        rows.append({
            "competitor_name": competitor_name,
            "tier_name": "Unknown",
            "price_usd": 0.0,
            "billing_frequency": "Unknown",
            "free_trial": False,
            "scraped_at": now_clickhouse(),

            # Optional debug fields. Remove before inserting into ClickHouse if table does not include them.
            "_query": query,
            "_raw_search_text": raw_text
        })

    return rows


# --------------------------------------------------
# TABLE 2: REVIEWS
# Schema:
# competitor_name, review_source, overall_score,
# review_count, common_praise, common_complaint, scraped_at
# --------------------------------------------------

def collect_review_rows():
    rows = []

    for competitor_name in COMPETITORS.keys():
        query = (
            f"{competitor_name} reviews customer sentiment complaints praise "
            f"pros cons pricing support features"
        )

        search = safe_search(
            query=query,
            domains=REVIEW_DOMAINS,
            search_depth="deep",
            time_range="month"
        )

        raw_text = result_to_text(search)

        rows.append({
            "competitor_name": competitor_name,
            "review_source": "G2 / Capterra / TrustRadius",
            "overall_score": 0.0,
            "review_count": 0,
            "common_praise": "Unknown",
            "common_complaint": "Unknown",
            "scraped_at": now_clickhouse(),

            # Optional debug fields. Remove before inserting into ClickHouse if table does not include them.
            "_query": query,
            "_raw_search_text": raw_text
        })

    return rows


# --------------------------------------------------
# TABLE 3: ACTIVITY
# Schema:
# competitor_name, activity_type, title,
# summary, published_at, scraped_at
# --------------------------------------------------

def collect_activity_rows():
    rows = []

    for competitor_name in COMPETITORS.keys():
        query = (
            f"{competitor_name} hiring jobs careers AI engineering product manager "
            f"sales marketing growth expansion changelog product update"
        )

        search = safe_search(
            query=query,
            domains=ACTIVITY_DOMAINS,
            search_depth="deep",
            time_range="month"
        )

        raw_text = result_to_text(search)

        rows.append({
            "competitor_name": competitor_name,
            "activity_type": "job_posting",
            "title": f"{competitor_name} activity signal",
            "summary": "Detected hiring, product, or growth activity signal.",
            "published_at": now_clickhouse(),
            "scraped_at": now_clickhouse(),

            # Optional debug fields. Remove before inserting into ClickHouse if table does not include them.
            "_query": query,
            "_raw_search_text": raw_text
        })

    return rows


# --------------------------------------------------
# TABLE 4: CASE STUDIES
# Schema:
# competitor_name, customer_name, industry,
# company_size, use_case, scraped_at
# --------------------------------------------------

def collect_case_study_rows():
    rows = []

    for competitor_name, config in COMPETITORS.items():
        domain = config["domain"]

        query = (
            f"{competitor_name} customer story OR case study OR customer research "
            f"enterprise ROI adoption transformation use case"
        )

        search = safe_search(
            query=query,
            domains=[domain],
            search_depth="deep",
            time_range="month"
        )

        raw_text = result_to_text(search)

        rows.append({
            "competitor_name": competitor_name,
            "customer_name": "Unknown",
            "industry": "Unknown",
            "company_size": "Unknown",
            "use_case": "Unknown",
            "scraped_at": now_clickhouse(),

            # Optional debug fields. Remove before inserting into ClickHouse if table does not include them.
            "_query": query,
            "_raw_search_text": raw_text
        })

    return rows


# --------------------------------------------------
# MAIN
# --------------------------------------------------

def main():
    ensure_data_dir()

    pricing_rows = collect_pricing_rows()
    review_rows = collect_review_rows()
    activity_rows = collect_activity_rows()
    case_study_rows = collect_case_study_rows()

    save_json("pricing.json", pricing_rows)
    save_json("reviews.json", review_rows)
    save_json("activity.json", activity_rows)
    save_json("case_studies.json", case_study_rows)

    print("\nDone.")
    print("Created:")
    print("data/pricing.json")
    print("data/reviews.json")
    print("data/activity.json")
    print("data/case_studies.json")


if __name__ == "__main__":
    main()
import json
import os

DATA_DIR = "data"

SCHEMAS = {
    "pricing.json": [
        "competitor_name",
        "tier_name",
        "price_usd",
        "billing_frequency",
        "free_trial",
        "scraped_at"
    ],
    "reviews.json": [
        "competitor_name",
        "review_source",
        "overall_score",
        "review_count",
        "common_praise",
        "common_complaint",
        "scraped_at"
    ],
    "activity.json": [
        "competitor_name",
        "activity_type",
        "title",
        "summary",
        "published_at",
        "scraped_at"
    ],
    "case_studies.json": [
        "competitor_name",
        "customer_name",
        "industry",
        "company_size",
        "use_case",
        "scraped_at"
    ]
}


def clean_file(filename, allowed_fields):
    path = os.path.join(DATA_DIR, filename)

    with open(path, "r") as f:
        rows = json.load(f)

    clean_rows = []

    for row in rows:
        clean_row = {}

        for field in allowed_fields:
            clean_row[field] = row.get(field)

        clean_rows.append(clean_row)

    clean_path = os.path.join(DATA_DIR, filename.replace(".json", "_clean.json"))

    with open(clean_path, "w") as f:
        json.dump(clean_rows, f, indent=2)

    print(f"Cleaned {filename} → {clean_path}")


def main():
    for filename, fields in SCHEMAS.items():
        clean_file(filename, fields)


if __name__ == "__main__":
    main()
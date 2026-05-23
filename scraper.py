import os
import datetime
import clickhouse_connect

client = clickhouse_connect.get_client(
    host=os.environ['CLICKHOUSE_HOST'],
    port=8443,
    username=os.environ['CLICKHOUSE_USER'],
    password=os.environ['CLICKHOUSE_PASSWORD'],
    secure=True
)

scraped_at = datetime.datetime.utcnow()

companies = ['HubSpot', 'Salesforce', 'Notion', 'Intercom', 'Monday.com']

rows = []
for company in companies:
    rows.append([
        company,
        'activity',
        'scheduled_scrape',
        f'{company} daily signal check',
        'Automated daily scrape triggered by Watchtower scheduler.',
        scraped_at,
        scraped_at
    ])

client.insert(
    'competitor_signals',
    rows,
    column_names=['competitor_name', 'signal_type', 'activity_type', 'title', 'summary', 'published_at', 'scraped_at']
)

print(f"Done. Inserted {len(rows)} rows into ClickHouse.")



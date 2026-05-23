import os
import datetime
import clickhouse_connect

host = 'n10e93bfd3.us-east-1.aws.clickhouse.cloud'
user = os.environ['CLICKHOUSE_USER']
password = os.environ['CLICKHOUSE_PASSWORD']

client = clickhouse_connect.get_client(
    host=host,
    port=8443,
    username=user,
    password=password,
    secure=True
)

scraped_at = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

companies = ['HubSpot', 'Salesforce', 'Notion', 'Intercom', 'Monday.com']

for company in companies:
    client.command(f"""
        INSERT INTO competitor_signals 
        (competitor_name, signal_type, activity_type, title, summary, published_at, scraped_at)
        VALUES (
            '{company}', 'activity', 'scheduled_scrape',
            '{company} daily signal check',
            'Automated daily scrape triggered by Watchtower scheduler.',
            '{scraped_at}', '{scraped_at}'
        )
    """)
    print(f"Inserted activity signal for {company}")

print("Done. All signals loaded into ClickHouse.")



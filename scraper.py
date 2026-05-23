import os
import datetime
import requests
import clickhouse_connect

NIMBLE_API_KEY = os.environ['NIMBLE_API_KEY']
CLICKHOUSE_HOST = os.environ['CLICKHOUSE_HOST']
CLICKHOUSE_USER = os.environ['CLICKHOUSE_USER']
CLICKHOUSE_PASSWORD = os.environ['CLICKHOUSE_PASSWORD']

client = clickhouse_connect.get_client(
    host=CLICKHOUSE_HOST,
    port=8443,
    username=CLICKHOUSE_USER,
    password=CLICKHOUSE_PASSWORD,
    secure=True
)

scraped_at = datetime.datetime.utcnow()

companies = {
    'HubSpot': {
        'pricing': 'https://www.hubspot.com/pricing',
        'reviews': 'https://www.g2.com/products/hubspot/reviews',
        'activity': 'https://www.hubspot.com/careers',
        'case_study': 'https://www.hubspot.com/case-studies'
    },
    'Salesforce': {
        'pricing': 'https://www.salesforce.com/editions-pricing',
        'reviews': 'https://www.g2.com/products/salesforce/reviews',
        'activity': 'https://www.salesforce.com/careers',
        'case_study': 'https://www.salesforce.com/customer-success-stories'
    },
    'Notion': {
        'pricing': 'https://www.notion.so/pricing',
        'reviews': 'https://www.g2.com/products/notion/reviews',
        'activity': 'https://www.notion.so/careers',
        'case_study': 'https://www.notion.so/customers'
    },
    'Intercom': {
        'pricing': 'https://www.intercom.com/pricing',
        'reviews': 'https://www.g2.com/products/intercom/reviews',
        'activity': 'https://www.intercom.com/careers',
        'case_study': 'https://www.intercom.com/customers'
    },
    'Monday': {
        'pricing': 'https://monday.com/pricing',
        'reviews': 'https://www.g2.com/products/monday-com/reviews',
        'activity': 'https://monday.com/careers',
        'case_study': 'https://monday.com/customers'
    }
}


def scrape_url(url):
    try:
        response = requests.post(
            'https://api.webit.live/api/v1/realtime/web',
            headers={
                'Authorization': 'Basic ' + NIMBLE_API_KEY,
                'Content-Type': 'application/json'
            },
            json={
                'url': url,
                'render': True,
                'country': 'US',
                'locale': 'en'
            },
            timeout=30
        )
        print('Status: ' + str(response.status_code))
        print('Response: ' + response.text[:200])
        if response.status_code == 200:
            data = response.json()
            return data.get('html_content', data.get('text', ''))
        return ''
    except Exception as e:
        print('Error scraping ' + url + ': ' + str(e))
        return ''



rows = []

for company, urls in companies.items():
    print('Scraping ' + company)
    for signal_type, url in urls.items():
        content = scrape_url(url)
        if content:
            summary = 'Scraped ' + url + '. Content length: ' + str(len(content)) + ' chars.'
        else:
            summary = 'No content returned for ' + url
        rows.append([
            company,
            signal_type,
            'web_scrape',
            company + ' ' + signal_type + ' update',
            summary,
            scraped_at,
            scraped_at
        ])
        print('  ' + signal_type + ': ' + str(len(content)) + ' chars')

client.insert(
    'competitor_signals',
    rows,
    column_names=[
        'competitor_name',
        'signal_type',
        'activity_type',
        'title',
        'summary',
        'published_at',
        'scraped_at'
    ]
)

print('Done. Inserted ' + str(len(rows)) + ' rows into ClickHouse.')



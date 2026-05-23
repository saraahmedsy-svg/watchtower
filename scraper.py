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
        'activity': 'ht


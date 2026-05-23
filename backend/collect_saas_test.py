def scrape_with_nimble(url: str) -> dict:
    if not NIMBLE_API_KEY:
        raise ValueError("Missing NIMBLE_API_KEY in .env")

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
    print("URL:", url)
    print("STATUS:", response.status_code)
    print("RAW RESPONSE:")
    print(response.text[:1000])
    print("========================\n")

    try:
        data = response.json()

    except Exception as e:
        return {
            "status_code": response.status_code,
            "error": f"JSON parse failed: {str(e)}",
            "raw_response": response.text[:2000]
        }

    return {
        "status_code": response.status_code,
        "url": url,
        "data": data
    }
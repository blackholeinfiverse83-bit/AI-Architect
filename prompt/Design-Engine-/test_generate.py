import asyncio
import httpx
import json

async def test_generate():
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjY5Yjc5NjAwMWU5NmY0MWQ4M2I1N2JlZSIsImlhdCI6MTc3NDg3NTI1NCwiZXhwIjoxNzc1NDgwMDU0fQ.61DGDLaKpvIXzSYmeeO-QdvMm5B2Tendmne9hnMrQTI"
    
    url = "http://127.0.0.1:8000/api/v1/generate"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    payload = {
        "user_id": "69b796001e96f41d83b57bee",
        "prompt": "Design a modern 2BHK apartment in Mumbai with a large balcony and open kitchen.",
        "city": "Mumbai",
        "style": "modern"
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            print(f"Sending POST request to {url}...")
            response = await client.post(url, headers=headers, json=payload)
            print(f"Status: {response.status_code}")
            
            if response.status_code in (200, 201):
                data = response.json()
                print("Success! Response Keys:")
                print(list(data.keys()))
                print(f"spec_id: {data.get('spec_id')}")
            else:
                print("Error Response:")
                print(response.text)
        except Exception as e:
            print(f"Request failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_generate())

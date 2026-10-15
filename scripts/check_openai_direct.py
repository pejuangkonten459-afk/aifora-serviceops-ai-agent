import os
import json
import urllib.request
import urllib.error

request = urllib.request.Request(
    "https://api.openai.com/v1/models",
    headers={"Authorization": "Bearer " + os.environ["OPENAI_API_KEY"]},
)

try:
    with urllib.request.urlopen(request, timeout=20) as response:
        data = json.load(response)
        print("HTTP status:", response.status)
        print("Jumlah model:", len(data.get("data", [])))
        print("API langsung berhasil.")

except urllib.error.HTTPError as exc:
    print("HTTP status:", exc.code)
    print("Response:", exc.read().decode("utf-8", errors="replace")[:2000])

except Exception as exc:
    print("Jenis error:", type(exc).__name__)
    print("Detail:", str(exc))

from openai import OpenAI, APIStatusError, APIConnectionError

try:
    client = OpenAI()
    response = client.responses.create(
        model="gpt-4.1-mini",
        input="Balas hanya dengan kata OK."
    )
    print("Koneksi berhasil.")
    print("Jawaban:", response.output_text)

except APIStatusError as exc:
    print("HTTP status:", exc.status_code)
    print("Detail:", exc.message)
    print("Request ID:", exc.request_id)
    print("Response:", repr(exc.response.text))

except APIConnectionError as exc:
    print("Koneksi gagal:", str(exc))

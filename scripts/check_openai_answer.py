from openai import OpenAI, APIStatusError, APIConnectionError

try:
    client = OpenAI()
    response = client.responses.create(
        model="gpt-4.1-mini",
        input="Balas hanya dengan kata OK."
    )
    print("Model:", response.model)
    print("Jawaban:", response.output_text)

except APIStatusError as exc:
    print("HTTP status:", exc.status_code)
    print("Detail:", exc.message)
    print("Response:", repr(exc.response.text))

except APIConnectionError as exc:
    print("Koneksi gagal:", str(exc))

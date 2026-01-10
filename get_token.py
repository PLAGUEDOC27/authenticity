import requests

# PASTE YOUR TOKEN HERE
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc2ODAzNDc3OCwianRpIjoiZDdlZDczOTMtYjNlYy00NTE0LTkyNTctYmNiZTZkYzI5YTBlIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjEiLCJuYmYiOjE3NjgwMzQ3NzgsImNzcmYiOiJhNzhlMmU1OS03NWRlLTRkYTQtODUzYy1iNjM3ZDJhOGZhYTMiLCJleHAiOjE3NjgwMzU2Nzh9.0lg1vZpd9EQ9SCp8EfPjkTt_DnYLTt6Wv8ffaMEP8KI"

url = "http://127.0.0.1:5000/documents/upload"

headers = {
    "Authorization": f"Bearer {token}"
}

files = {
    "file": open(r"U:\csta26\Authenticity\dummy.pdf","rb")
}

response = requests.post(url, headers=headers, files=files)

print("Status:", response.status_code)
print("Response:", response.text)

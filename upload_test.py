import requests
import os
import json

# --- Step 1: Ask for JWT token ---
token = input("Enter your JWT token: ").strip()
if not token:
    print("Token cannot be empty!")
    exit(1)

# --- Step 2: Ask for file path ---
file_path = input("Enter the full path of the file to upload: ").strip()
if not os.path.isfile(file_path):
    print(f"File not found: {file_path}")
    exit(1)

# --- Step 3: Prepare request ---
url = "http://127.0.0.1:5000/documents/upload"
headers = {"Authorization": f"Bearer {token}"}
files = {"file": open(file_path, "rb")}

# --- Step 4: Send POST request ---
try:
    response = requests.post(url, headers=headers, files=files)
except Exception as e:
    print("Error uploading file:", e)
    exit(1)
finally:
    files["file"].close()

# --- Step 5: Display results ---
print("\n--- Upload Response ---")
print("Status Code:", response.status_code)

try:
    data = response.json()
    print(json.dumps(data, indent=4))
except Exception:
    print(response.text)

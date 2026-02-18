import requests
from datetime import datetime

# Mistral AI API key (replace with your actual key)
API_KEY = "Lmm2Fh2US5tddtJLaKS6ccyscQEV8mDE"

# Mistral API endpoint
MISTRAL_URL = "https://api.mistral.ai/v1/chat/completions"


def get_today_date():
    """Returns today's date in YYYY-MM-DD format."""
    return datetime.today().strftime("%Y-%m-%d")


# Define the function to call Mistral AI
def call_mistral(prompt):
    """Sends a prompt to Mistral AI and returns the response."""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "mistral-small-latest",  # Replace with the correct model
        "messages": [{"role": "user", "content": prompt}]
    }

    response = requests.post(MISTRAL_URL, headers=headers, json=data)
    return response.json()


# Check if the user is asking for the date
def process_user_input(user_input):
    """Determines if the user is asking for the date and calls the appropriate function."""
    if "today's date" in user_input.lower() or "current date" in user_input.lower():
        return get_today_date()  # Call AI agent directly
    else:
        return call_mistral(user_input)  # Call Mistral AI


# Example Usage
user_query = "What is today's date?"
response = process_user_input(user_query)

print("Response:", response)

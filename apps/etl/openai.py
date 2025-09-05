import requests
import yaml
import os

# Load config from config.yaml
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.yaml')
with open(CONFIG_PATH, 'r') as f:
    config = yaml.safe_load(f)

USE_MODEL = config.get('use_model', 'github_models')

if USE_MODEL == 'github_models':
    AI_MODEL_ENDPOINT = config['github_models']['endpoint']
    API_TOKEN = config['github_models']['token']
    DEFAULT_MODEL = config['github_models'].get('default_model', 'openai/gpt-4o')
elif USE_MODEL == 'gemini':
    AI_MODEL_ENDPOINT = config['gemini']['endpoint']
    API_TOKEN = config['gemini']['api_key']
    DEFAULT_MODEL = config['gemini'].get('default_model', 'gemini-2.0-flash')
else:
    raise ValueError(f"Unknown model type in config.yaml: {USE_MODEL}")

def ask_model(prompt, model_id=None):
    """
    Sends a prompt to the selected AI model API and returns the response.

    Args:
        prompt (str): The user's question or data.
        model_id (str): The ID of the model to use. If None, uses value from config.yaml.

    Returns:
        str: The AI model's response content.
    """
    if not API_TOKEN:
        print("Error: API token not set in config.yaml.")
        return None
    if not model_id:
        model_id = DEFAULT_MODEL

    if USE_MODEL == 'github_models':
        payload = {
            "model": model_id,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        headers = {
            "Authorization": f"Bearer {API_TOKEN}",
            "Content-Type": "application/json"
        }
    elif USE_MODEL == 'gemini':
        payload = {
            "contents": [
                {"parts": [
                    {"text": prompt}
                ]}
            ]
        }
        headers = {
            "Content-Type": "application/json",
            "X-goog-api-key": API_TOKEN
        }
    else:
        raise ValueError(f"Unknown model type: {USE_MODEL}")

    try:
        response = requests.post(AI_MODEL_ENDPOINT, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        if USE_MODEL == 'github_models':
            if data.get('choices'):
                return data['choices'][0]['message']['content']
            else:
                return f"Received an unexpected response format: {data}"
        elif USE_MODEL == 'gemini':
            # Gemini returns 'candidates' with 'content' and 'parts'
            if data.get('candidates'):
                candidate = data['candidates'][0]
                if 'content' in candidate and 'parts' in candidate['content'] and candidate['content']['parts']:
                    return candidate['content']['parts'][0].get('text', '')
                else:
                    return ''
            else:
                return f"Received an unexpected response format: {data}"
    except requests.exceptions.RequestException as e:
        print(f"Error calling AI Model API: {e}")
        return None
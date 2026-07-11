import os
from openai import OpenAI
from resistor_llm.timeout_guard import run_with_timeout

# HARDCODE YOUR KEY HERE FOR THE HACKATHON
# Paste your actual key between the quotes below!
FIREWORKS_API_KEY = "fw_Sp3BFVxGChm9LJkedfA3TU"

client = OpenAI(
    base_url="https://api.fireworks.ai/inference/v1",
    api_key=FIREWORKS_API_KEY,
)

def _call_fireworks(prompt, model="accounts/fireworks/models/gpt-oss-120b", max_tokens=500):
    """Internal function that actually hits the Fireworks API."""
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a world-class computational biologist analyzing drug resistance mutations."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=max_tokens,
        temperature=0.2 
    )
    return response.choices[0].message.content.strip()

def ask_llm(prompt, timeout=10.0):
    """
    Public function wrapped in our Hackathon Timeout Guard.
    """
    if not FIREWORKS_API_KEY or FIREWORKS_API_KEY == "PASTE_YOUR_ACTUAL_API_KEY_HERE":
        print("[ERROR] Fireworks API Key is missing!")
        return None
        
    print("[INFO] Contacting Fireworks AI API...")
    result = run_with_timeout(_call_fireworks, args=(prompt,), timeout_seconds=timeout)
    return result
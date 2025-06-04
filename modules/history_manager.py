import json
import os
from datetime import datetime

HISTORY_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'history.json')

def save_history_entry(category, score, feedback):
    os.makedirs(os.path.dirname(HISTORY_PATH), exist_ok=True)
    history = load_history()
    history.append({
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M'),
        "category": category,
        "score": score,
        "feedback": feedback
    })
    with open(HISTORY_PATH, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=4)

def load_history():
    if os.path.exists(HISTORY_PATH):
        with open(HISTORY_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

# modules/evaluator.py

import json
import os
import re
from textblob import TextBlob
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize

# Ensure NLTK data is available
nltk.download('punkt', quiet=True)

# Path to your reference keywords JSON
REF_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'reference_answers.json')

def load_reference():
    try:
        with open(REF_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

reference_data = load_reference()

# Common disfluency fillers
FILLERS = {"um", "uh", "like", "you know", "so", "actually", "basically", "just", "well", "hmm"}

def count_filler_words(text):
    tokens = word_tokenize(text.lower())
    return sum(1 for t in tokens if t in FILLERS)

def vocabulary_score(text):
    tokens = [t.lower() for t in word_tokenize(text) if t.isalpha()]
    if not tokens:
        return 0.0
    return len(set(tokens)) / len(tokens)  # type–token ratio

def sentiment_score(text):
    # Polarity in [-1,1] → normalize to [0,1]
    polarity = TextBlob(text).sentiment.polarity
    return (polarity + 1) / 2

def structure_score(text):
    # Ideal avg sentence length ~15 words
    sentences = sent_tokenize(text)
    if not sentences:
        return 0.0
    lengths = [len(word_tokenize(s)) for s in sentences]
    avg_len = sum(lengths) / len(lengths)
    return max(0, 1 - abs(avg_len - 15) / 15)  # perfect at 15 words

def keyword_match_score(questions, text):
    scores = []
    lower = text.lower()
    for q in questions:
        keys = reference_data.get(q, [])
        if not keys:
            continue
        matches = sum(1 for k in keys if k.lower() in lower)
        scores.append(matches / len(keys))
    return sum(scores) / len(scores) if scores else 0.0

def evaluate_transcript(questions, transcript):
    """
    Returns a dict with individual metric scores and overall:
      {
        'fluency': float,    # 0–10
        'vocabulary': float, # 0–10
        'confidence': float, # 0–10
        'structure': float,  # 0–10
        'factual': float,    # 0–10
        'overall': float,    # 0–10
        'feedback': str
      }
    """
    txt = transcript.strip()
    tokens = word_tokenize(txt)
    total_words = len(tokens) or 1

    # Fluency = (1 - filler_rate) * 10
    fillers = count_filler_words(txt)
    fluency_raw = 1 - min(fillers / total_words, 1.0)
    fluency = round(fluency_raw * 10, 1)

    # Vocabulary = type–token ratio * 10
    vocab_raw = vocabulary_score(txt)
    vocabulary = round(vocab_raw * 10, 1)

    # Confidence = sentiment_score * 10
    conf_raw = sentiment_score(txt)
    confidence = round(conf_raw * 10, 1)

    # Structure = structure_score * 10
    struct_raw = structure_score(txt)
    structure = round(struct_raw * 10, 1)

    # Factual = keyword_match_score * 10
    factual_raw = keyword_match_score(questions, txt)
    factual = round(factual_raw * 10, 1)

    # Overall weighted combination
    overall_raw = (
        0.25 * fluency_raw +
        0.25 * vocab_raw +
        0.20 * conf_raw +
        0.20 * struct_raw +
        0.10 * factual_raw
    )
    overall = round(overall_raw * 10, 1)

    # Feedback suggestions
    tips = []
    if fluency_raw < 0.7:
        tips.append("Try to reduce filler words for smoother speech.")
    if vocab_raw < 0.3:
        tips.append("Use a wider range of vocabulary.")
    if conf_raw < 0.5:
        tips.append("Speak with more confidence and energy.")
    if struct_raw < 0.7:
        tips.append("Structure your answers into clear, complete sentences.")
    if factual_raw < 0.3:
        tips.append("Include more relevant points from the question prompt.")

    feedback = "\n".join(tips) if tips else "Great job! Your communication skills look strong."

    return {
        'fluency': fluency,
        'vocabulary': vocabulary,
        'confidence': confidence,
        'structure': structure,
        'factual': factual,
        'overall': overall,
        'feedback': feedback
    }

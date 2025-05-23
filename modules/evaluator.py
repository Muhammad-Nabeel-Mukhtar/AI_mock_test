import json
import re
import os
from collections import Counter

REFERENCE_PATH = os.path.join(os.path.dirname(__file__), '../data/reference_answers.json')

FILLER_WORDS = ["um", "uh", "like", "you know", "so", "actually", "basically"]

# Load reference key-points
with open(REFERENCE_PATH, 'r', encoding='utf-8') as f:
    REFERENCE = json.load(f)

def keyword_match_score(question, transcript, keywords):
    """Returns float score based on how many reference keywords appear in transcript."""
    transcript = transcript.lower()
    match_count = sum(1 for kw in keywords if re.search(r"\\b" + re.escape(kw.lower()) + r"\\b", transcript))
    return match_count / len(keywords) if keywords else 0

def filler_word_penalty(transcript):
    words = transcript.lower().split()
    counts = Counter(words)
    total = sum(counts.values())
    fillers = sum(counts[w] for w in FILLER_WORDS)
    return fillers / total if total > 0 else 0

def sentence_complexity_score(transcript):
    sentences = [s.strip() for s in transcript.split('.') if s.strip()]
    if not sentences:
        return 0
    avg_len = sum(len(s.split()) for s in sentences) / len(sentences)
    return min(avg_len / 15, 1)  # Reward average sentence length ~15 words

def evaluate_transcript(questions, transcript):
    total_score = 0
    count = 0
    remarks = []

    for q in questions:
        if q in REFERENCE:
            score = keyword_match_score(q, transcript, REFERENCE[q])
            total_score += score
            count += 1
    factual_score = (total_score / count) * 10 if count else 5

    # Soft skill analysis
    filler_penalty = filler_word_penalty(transcript)  # 0 to ~0.1 typical
    sentence_score = sentence_complexity_score(transcript) * 10

    # Combine all
    final_score = 0.6 * factual_score + 0.2 * (10 - filler_penalty * 100) + 0.2 * sentence_score
    final_score = max(0, min(final_score, 10))

    # Feedback summary
    remarks.append(f"Relevance & correctness: {factual_score:.1f}/10")
    remarks.append(f"Filler usage penalty: -{filler_penalty * 100:.1f}%")
    remarks.append(f"Sentence clarity: {sentence_score:.1f}/10")

    summary = "\n".join(remarks)
    summary += "\n\nTips: Focus on using fewer filler words, and structure your answers clearly."

    return round(final_score, 2), summary


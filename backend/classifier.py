import json
import os

# Load ratio_config.json dynamically from file
with open("ratio_config.json", "r") as f:
    ratio_config = json.load(f)

def get_ratio_str(w, h):
    """Simplify width/height to a ratio string like '343:221'."""
    def gcd(a, b):
        while b:
            a, b = b, a % b
        return a
    g = gcd(w, h)
    return f"{w // g}:{h // g}"

def get_closest_class(w, h):
    """Return the closest matching document type based on width and height."""
    input_ratio = w / h
    best_match = None
    min_diff = float('inf')
    for doc_type, ratio_str in ratio_config.items():
        rw, rh = map(int, ratio_str.split(':'))
        expected_ratio = rw / rh
        diff = abs(expected_ratio - input_ratio)
        if diff < min_diff:
            min_diff = diff
            best_match = doc_type
    return best_match, get_ratio_str(w, h)

import json
import os
import cv2
import pytesseract
import numpy as np
from pdf2image import convert_from_bytes
from difflib import SequenceMatcher
from utils.date_normalizer import normalize_date_fields

# Load field coordinate configuration
with open("config.json", "r") as f:
    config = json.load(f)

expected_label_map = {
    "passport": "PASSPORT",
    "driver_license": "DRIVER LICENSE",
    "ead_card": "EMPLOYMENT AUTHORIZATION CARD"
}

def load_image(file_bytes: bytes, file_ext: str):
    """Convert file bytes to RGB image."""
    if file_ext.lower() == ".pdf":
        image = convert_from_bytes(file_bytes, dpi=300)[0]
        img = np.array(image)
    else:
        nparr = np.frombuffer(file_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img

def remove_white_borders(img):
    """Crop out white borders from the image."""
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
    coords = cv2.findNonZero(thresh)
    if coords is not None:
        x, y, w, h = cv2.boundingRect(coords)
        return img[y:y+h, x:x+w]
    return img

def resize_to_target(img, target_ratio_str):
    """Resize image to match a given ratio's width and height."""
    h, w = img.shape[:2]
    rw, rh = map(int, target_ratio_str.split(":"))
    scale_w = rw / w
    scale_h = rh / h
    scale = min(scale_w, scale_h)
    new_w = int(w * scale)
    new_h = int(h * scale)
    return cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)

def verify_class(img, doc_type):
    """Check whether OCR result in 'field_name' matches expected label."""
    if "field_name" not in config[doc_type]:
        return False
    x1, y1, x2, y2 = config[doc_type]["field_name"]
    roi = img[y1:y2, x1:x2]
    text = pytesseract.image_to_string(roi, config='--psm 6').strip().upper()
    confidence = SequenceMatcher(None, text, expected_label_map[doc_type]).ratio()
    print(f"OCR Field Name: {text}")
    print(f"Match Confidence with '{expected_label_map[doc_type]}': {confidence:.2f}")
    return confidence > 0.5

def extract_fields(img, doc_type):
    """Extract field text values using OCR."""
    data = {}
    for field, (x1, y1, x2, y2) in config[doc_type].items():
        if field == "field_name":
            continue
        roi = img[y1:y2, x1:x2]
        text = pytesseract.image_to_string(roi, config='--psm 6').strip()
        data[field] = text
    # Normalizes date fields
    return normalize_date_fields(data)

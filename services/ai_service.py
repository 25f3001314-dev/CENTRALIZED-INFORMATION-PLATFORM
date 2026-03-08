import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Training data embedded in code
TRAINING_DATA = [
    # Roads
    ("pothole on main road damaged vehicle", "Roads"),
    ("road has large cracks and potholes", "Roads"),
    ("broken road surface needs repair", "Roads"),
    ("road damage after rain flooding", "Roads"),
    ("street needs resurfacing potholes everywhere", "Roads"),
    ("road construction blocking traffic", "Roads"),
    ("damaged footpath road pavement broken", "Roads"),
    ("manhole cover missing road danger", "Roads"),
    # Water
    ("water supply cut off for three days", "Water"),
    ("broken water pipe leaking on street", "Water"),
    ("no water in tap shortage", "Water"),
    ("water contamination dirty brown water", "Water"),
    ("pipeline burst flooding basement", "Water"),
    ("water meter not working", "Water"),
    ("sewage mixing with drinking water", "Water"),
    ("low water pressure in building", "Water"),
    # Sanitation
    ("garbage not collected for days overflow", "Sanitation"),
    ("open drainage blocked flooding sewage", "Sanitation"),
    ("public toilet not cleaned stinking", "Sanitation"),
    ("waste dumping illegal site smell", "Sanitation"),
    ("drainage blocked sewage overflow on road", "Sanitation"),
    ("garbage bin overflowing health hazard", "Sanitation"),
    ("street sweeping not done dirty area", "Sanitation"),
    ("dead animal on road not removed", "Sanitation"),
    # Electrical
    ("street light not working dark road", "Electrical"),
    ("power outage no electricity building", "Electrical"),
    ("electric wire hanging dangerously low", "Electrical"),
    ("transformer fault no power supply", "Electrical"),
    ("street lights broken column damage", "Electrical"),
    ("electricity bill overcharged wrong reading", "Electrical"),
    ("short circuit sparks from pole dangerous", "Electrical"),
    ("faulty wiring fire hazard building", "Electrical"),
    # Parks
    ("park bench broken dangerous to sit", "Parks"),
    ("garden area not maintained overgrown weeds", "Parks"),
    ("playground equipment damaged children hurt", "Parks"),
    ("park lights not working unsafe at night", "Parks"),
    ("tree branches falling park hazard", "Parks"),
    ("park fountain not working broken", "Parks"),
    ("public space encroachment illegal", "Parks"),
    ("park grass not mowed overgrown", "Parks"),
    # Infrastructure
    ("building wall cracked structural damage", "Infrastructure"),
    ("bridge needs inspection cracks visible", "Infrastructure"),
    ("boundary wall collapsed public safety", "Infrastructure"),
    ("storm drain blocked flooding basement", "Infrastructure"),
    ("public building roof leaking damage", "Infrastructure"),
    ("flyover crack detected structural issue", "Infrastructure"),
    ("retaining wall damaged land erosion", "Infrastructure"),
    ("civic amenity building in disrepair", "Infrastructure"),
]

DEPT_MAP = {
    "Roads": "Public Works Department",
    "Water": "Water Supply & Sewerage Board",
    "Sanitation": "Municipal Solid Waste Management",
    "Electrical": "Electricity Department",
    "Parks": "Parks & Recreation Department",
    "Infrastructure": "Urban Development Authority",
}

SEVERITY_MAP = {
    "Roads": "High",
    "Water": "High",
    "Sanitation": "Medium",
    "Electrical": "High",
    "Parks": "Low",
    "Infrastructure": "High",
}

RESOLUTION_DAYS = {
    "Roads": "5-7 days",
    "Water": "2-3 days",
    "Sanitation": "1-2 days",
    "Electrical": "2-4 days",
    "Parks": "7-10 days",
    "Infrastructure": "10-15 days",
}

PRIORITY_KEYWORDS = {
    'critical': ['danger', 'emergency', 'accident', 'death', 'injury', 'fire', 'explosion', 'collapse'],
    'high': ['urgent', 'safety', 'hazard', 'risk', 'children', 'hospital', 'flooding', 'burst'],
    'medium': ['broken', 'damaged', 'leaking', 'overflowing', 'blocked', 'not working'],
    'low': ['minor', 'small', 'slight', 'cosmetic', 'aesthetic']
}

_classifier = None
_vectorizer = None


def _get_classifier():
    global _classifier, _vectorizer
    if _classifier is not None:
        return _classifier, _vectorizer
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.naive_bayes import MultinomialNB
        texts = [t for t, _ in TRAINING_DATA]
        labels = [l for _, l in TRAINING_DATA]
        _vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
        X = _vectorizer.fit_transform(texts)
        _classifier = MultinomialNB()
        _classifier.fit(X, labels)
        logger.info("AI classifier trained successfully on %d samples", len(texts))
    except ImportError:
        logger.warning("sklearn not available, using keyword-based fallback")
        _classifier = None
        _vectorizer = None
    return _classifier, _vectorizer


def categorize_issue(text):
    """Categorize issue text using NLP classifier."""
    clf, vec = _get_classifier()
    if clf is not None:
        try:
            X = vec.transform([text.lower()])
            prediction = clf.predict(X)[0]
            proba = clf.predict_proba(X)[0]
            confidence = float(max(proba)) * 100
            return prediction, round(confidence, 1)
        except Exception as e:
            logger.error("Classification error: %s", e)
    # Keyword fallback
    text_lower = text.lower()
    scores = {cat: 0 for cat in DEPT_MAP}
    keyword_map = {
        'Roads': ['road', 'pothole', 'pavement', 'footpath', 'manhole', 'crack'],
        'Water': ['water', 'pipe', 'supply', 'leaking', 'tap', 'sewage', 'drain'],
        'Sanitation': ['garbage', 'waste', 'drain', 'toilet', 'sanitation', 'smell', 'stink'],
        'Electrical': ['electric', 'light', 'power', 'wire', 'transformer', 'street light'],
        'Parks': ['park', 'garden', 'tree', 'bench', 'playground', 'grass'],
        'Infrastructure': ['building', 'bridge', 'wall', 'structure', 'flyover'],
    }
    for cat, kws in keyword_map.items():
        for kw in kws:
            if kw in text_lower:
                scores[cat] += 1
    best = max(scores, key=scores.get)
    if scores[best] == 0:
        best = 'Infrastructure'
    return best, 65.0


def calculate_priority(text, category='Infrastructure'):
    """Calculate priority score 0-100 and return priority label."""
    text_lower = text.lower()
    score = 40  # base
    category_weights = {'Electrical': 20, 'Water': 20, 'Roads': 15, 'Infrastructure': 15, 'Sanitation': 10, 'Parks': 5}
    score += category_weights.get(category, 10)
    for kw in PRIORITY_KEYWORDS['critical']:
        if kw in text_lower:
            score += 15
    for kw in PRIORITY_KEYWORDS['high']:
        if kw in text_lower:
            score += 8
    for kw in PRIORITY_KEYWORDS['medium']:
        if kw in text_lower:
            score += 3
    for kw in PRIORITY_KEYWORDS['low']:
        if kw in text_lower:
            score -= 5
    score = max(0, min(100, score))
    if score >= 80:
        return 'Urgent', score
    elif score >= 60:
        return 'High', score
    elif score >= 40:
        return 'Medium', score
    else:
        return 'Low', score


def analyze_photo_metadata(filepath):
    """Extract EXIF/GPS data and do OCR on uploaded photo."""
    result = {'gps': None, 'ocr_text': '', 'dimensions': None, 'format': None}
    try:
        from PIL import Image
        from PIL.ExifTags import TAGS, GPSTAGS
        img = Image.open(filepath)
        result['dimensions'] = img.size
        result['format'] = img.format
        exif_data = img._getexif()
        if exif_data:
            for tag_id, value in exif_data.items():
                tag = TAGS.get(tag_id, tag_id)
                if tag == 'GPSInfo':
                    gps = {}
                    for gps_tag_id, gps_value in value.items():
                        gps_tag = GPSTAGS.get(gps_tag_id, gps_tag_id)
                        gps[gps_tag] = gps_value
                    if 'GPSLatitude' in gps and 'GPSLongitude' in gps:
                        lat = _dms_to_decimal(gps['GPSLatitude'], gps.get('GPSLatitudeRef', 'N'))
                        lng = _dms_to_decimal(gps['GPSLongitude'], gps.get('GPSLongitudeRef', 'E'))
                        result['gps'] = {'lat': lat, 'lng': lng}
    except Exception as e:
        logger.warning("EXIF extraction error: %s", e)
    try:
        import pytesseract
        from PIL import Image
        img = Image.open(filepath)
        result['ocr_text'] = pytesseract.image_to_string(img)
    except Exception:
        result['ocr_text'] = '(OCR not available)'
    return result


def _dms_to_decimal(dms, ref):
    """Convert degrees/minutes/seconds to decimal."""
    try:
        d = float(dms[0])
        m = float(dms[1])
        s = float(dms[2])
        decimal = d + m/60 + s/3600
        if ref in ['S', 'W']:
            decimal = -decimal
        return decimal
    except Exception:
        return 0.0


def compare_images(before_path, after_path):
    """Compare before/after images using average hash. Returns change percentage and verified status."""
    try:
        from PIL import Image
        import numpy as np

        def avg_hash(path, size=16):
            img = Image.open(path).convert('L').resize((size, size), Image.LANCZOS)
            arr = np.array(img)
            mean = arr.mean()
            return arr > mean

        before_hash = avg_hash(before_path)
        after_hash = avg_hash(after_path)
        diff = np.sum(before_hash != after_hash)
        total = before_hash.size
        change_pct = (diff / total) * 100
        verified = change_pct > 15
        confidence = min(99, change_pct * 2) if verified else max(1, 100 - change_pct * 3)
        return {
            'change_percentage': round(change_pct, 1),
            'verified': verified,
            'confidence': round(confidence, 1),
            'status': 'Verified Fix' if verified else 'Insufficient Change'
        }
    except Exception as e:
        logger.warning("Image comparison error: %s", e)
        return {'change_percentage': 0, 'verified': False, 'confidence': 0, 'status': 'Analysis Failed'}


def get_suggested_dept(category):
    return DEPT_MAP.get(category, 'General Administration')


def get_est_resolution(category):
    return RESOLUTION_DAYS.get(category, '5-7 days')


def get_severity(category):
    return SEVERITY_MAP.get(category, 'Medium')

from flask import Flask, render_template, request
import pytesseract
from PIL import Image
import os
import re

# 🔴 Tesseract Path (keep this correct)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
os.environ['TESSDATA_PREFIX'] = r'C:\Program Files\Tesseract-OCR\tessdata'

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ✅ Create uploads folder if not exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


# 🧠 ADVANCED AI LOGIC
def analyze_text(text):
    risk_score = 0
    reasons = []

    text_lower = text.lower()

    # ----------------------------
    # 1. Suspicious keywords
    # ----------------------------
    suspicious_words = ["fake", "scam", "urgent", "verify now", "click here"]

    for word in suspicious_words:
        if word in text_lower:
            risk_score += 25
            reasons.append(f"Suspicious keyword detected: '{word}'")

    # ----------------------------
    # 2. Very short content
    # ----------------------------
    if len(text.strip()) < 50:
        risk_score += 20
        reasons.append("Very little content detected")

    # ----------------------------
    # 3. Required fields check
    # ----------------------------
    required_fields = ["invoice", "date", "total", "amount"]

    missing = [field for field in required_fields if field not in text_lower]

    if missing:
        risk_score += 20
        reasons.append(f"Missing fields: {', '.join(missing)}")

    # ----------------------------
    # 4. Detect unrealistic numbers
    # ----------------------------
    numbers = re.findall(r'\d+', text)

    large_numbers = [int(num) for num in numbers if int(num) > 100000]

    if large_numbers:
        risk_score += 30
        reasons.append("Unrealistic large values detected")

    # ----------------------------
    # 5. No numeric data
    # ----------------------------
    if not any(char.isdigit() for char in text):
        risk_score += 10
        reasons.append("No numeric data found")

    # ----------------------------
    # 6. Email validation (smart)
    # ----------------------------
    if "email" in text_lower and "@" not in text:
        risk_score += 10
        reasons.append("Email mentioned but not found")

    # ----------------------------
    # 7. Structure check
    # ----------------------------
    words = text.split()

    if len(words) < 20:
        risk_score += 15
        reasons.append("Poor document structure")

    # ----------------------------
    # FINAL STATUS
    # ----------------------------
    if risk_score >= 50:
        status = "Fraud"
    elif risk_score >= 20:
        status = "Suspicious"
    else:
        status = "Valid"

    # ----------------------------
    # Default clean case
    # ----------------------------
    if risk_score == 0:
        risk_score = 5
        reasons.append("Document appears structurally valid")

    return risk_score, status, reasons


# 🌐 ROUTE
@app.route('/', methods=['GET', 'POST'])
def index():
    result = None

    if request.method == 'POST':
        file = request.files['file']

        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)

            # 🔍 OCR Extraction
            text = pytesseract.image_to_string(Image.open(filepath))

            # 🧠 AI Analysis
            risk, status, reasons = analyze_text(text)

            result = {
                "text": text,
                "risk": risk,
                "status": status,
                "reasons": reasons
            }

    return render_template('index.html', result=result)


# ▶️ RUN
if __name__ == '__main__':
    app.run(debug=True)
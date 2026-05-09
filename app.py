import os
import cohere
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import PyPDF2

app = Flask(__name__)

co = cohere.Client(os.environ.get('COHERE_API_KEY'))

# ===== عدل البيانات دي براحتك =====
VALID_ACTIVATION_CODE = "ANWAR2026"  # غيّر الكود ده كل شهر
SUBSCRIPTION_PRICE = "100 جنيه شهرياً"
ORANGE_CASH_NUMBER = "01289590022"
WHATSAPP_NUMBER = "201289590022"  # حط رقمك بواتساب بكود مصر
# ===================================

def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def generate_exam(text, exam_details):
    prompt = f"""
    أنت أستاذ خبير في وضع الامتحانات للمناهج المصرية. بناء على النص التالي من المنهج:

    --- النص ---
    {text[:12000]}
    --- انتهى النص ---

    المطلوب: اعمل امتحان احترافي بالمواصفات دي:
    1. الصف الدراسي: {exam_details['grade']}
    2. اسم الدرس أو الوحدة

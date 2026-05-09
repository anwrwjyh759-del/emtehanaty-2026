import os
import cohere
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import PyPDF2

app = Flask(__name__)

co = cohere.Client(os.environ.get('COHERE_API_KEY'))

VALID_ACTIVATION_CODE = "ANWAR2026"
SUBSCRIPTION_PRICE = "100 جنيه شهرياً"
ORANGE_CASH_NUMBER = "01289590022"
WHATSAPP_NUMBER = "201289590022"

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
    2. اسم الدرس أو الوحدة: {exam_details['lesson']}
    3. عدد أسئلة الاختيار من متعدد: {exam_details['mcq']}
    4. عدد الأسئلة المقالية: {exam_details['essay']}

    شروط مهمة جداً:
    - الأسئلة تكون من فهم النص وليست نسخ ولصق مباشر
    - سؤال الاختيار من متعدد له 4 اختيارات A, B, C, D
    - بعد ما تخلص الأسئلة اكتب عنوان "نموذج الإجابة" وتحته الإجابات الصحيحة
    - نسق الامتحان بشكل احترافي جاهز للطباعة مباشرة
    - ابدأ الامتحان بجملة "امتحان {exam_details['lesson']} - {exam_details['grade']}"
    """

    try:
        response = co.chat(
            model='command-r-plus',
            message=prompt,
            temperature=0.4
        )
        return response.text
    except Exception as e:
        return f"حصل خطأ في توليد الامتحان: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html',
                         price=SUBSCRIPTION_PRICE,
                         orange_number=ORANGE_CASH_NUMBER,
                         whatsapp_number=WHATSAPP_NUMBER)

@app.route('/generate', methods=['POST'])
def generate():
    activation_code = request.form.get('activation_code')
    if activation_code != VALID_ACTIVATION_CODE:
        return jsonify({
            'status': 'error',
            'message': f'كود التفعيل غير صحيح ❌\nللاشتراك {SUBSCRIPTION_PRICE}:\n1. حول على أورنج كاش: {ORANGE_CASH_NUMBER}\n2. ابعت صورة التحويل على واتساب: {ORANGE_CASH_NUMBER}\nوهنبعتلك الكود فوراً'
        })

    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'لازم ترفع ملف الكتاب أو المذكرة PDF'})

    file = request.files['file']
    exam_details = {
        'grade': request.form.get('grade'),
        'lesson': request.form.get('lesson'),
        'mcq': request.form.get('mcq', 10),
        'essay': request.form.get('essay', 3)
    }

    if not exam_details['grade'] or not exam_details['lesson']:
        return jsonify({'status': 'error', 'message': 'اكتب الصف واسم الدرس'})

    try:
        text = extract_text_from_pdf(file)
        if not text.strip():
            return jsonify({'status': 'error', 'message': 'الملف فاضي أو الملف PDF متصور صور مش نص'})

        exam = generate_exam(text, exam_details)

        return jsonify({
            'status': 'success',
            'exam': exam
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'حصل خطأ: تأكد إن الملف PDF نصي وسليم'
        })

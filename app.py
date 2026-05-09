from flask import Flask, render_template, request, jsonify
import PyPDF2
import cohere
import os

app = Flask(__name__)
co = cohere.Client(os.environ['COHERE_API_KEY'])

def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    # هنقرأ أول 20 صفحة بس
    max_pages = min(20, len(pdf_reader.pages))
    for i in range(max_pages):
        page = pdf_reader.pages[i]
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    # Cohere آخره 12 ألف حرف عشان ميضربش
    return text[:12000]

def generate_exam(text, exam_details):
    prompt = f"""
    أنت أستاذ خبير في وضع الامتحانات للمناهج المصرية. بناء على النص التالي:

    --- النص ---
    {text}
    --- انتهى النص ---

    المطلوب: اعمل امتحان احترافي بالمواصفات دي:
    1. الصف الدراسي: {exam_details['grade']}
    2. اسم الدرس: {exam_details['lesson']}
    3. عدد أسئلة الاختيار من متعدد: {exam_details['mcq']}
    4. عدد الأسئلة المقالية: {exam_details['essay']}

    شروط مهمة:
    - الأسئلة من فهم النص مش نسخ لصق
    - MCQ له 4 اختيارات A, B, C, D
    - بعد الأسئلة اكتب "نموذج الإجابة" وتحته الحل
    - نسق الامتحان للطباعة مباشرة
    - ابدأ بـ "امتحان {exam_details['lesson']} - {exam_details['grade']}"
    """

    try:
        response = co.chat(
            model='command-r-plus',
            message=prompt,
            temperature=0.4,
            max_tokens=2000
        )
        return response.text
    except Exception as e:
        return f"خطأ: الملف كبير أو السيرفر مشغول. جرب 10 صفحات بس من الدرس"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'ارفع ملف PDF'})

    file = request.files['file']
    activation_code = request.form.get('activation_code')

    if activation_code!= 'ANWAR2026':
        return jsonify({'status': 'error', 'message': 'كود التفعيل غلط. كلم الدعم 01289590022'})

    try:
        text = extract_text_from_pdf(file)
        if len(text) < 50:
            return jsonify({'status': 'error', 'message': 'الملف فاضي أو مقدرتش اقرأه'})

        exam_details = {
            'grade': request.form.get('grade'),
            'lesson': request.form.get('lesson'),
            'mcq': request.form.get('mcq'),
            'essay': request.form.get('essay')
        }

        exam = generate_exam(text, exam_details)
        return jsonify({'status': 'success', 'exam': exam})

    except Exception as e:
        return jsonify({'status': 'error', 'message': f'حصلت مشكلة: {str(e)}'})

if __name__ == '__main__':
    app.run()

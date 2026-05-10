from flask import Flask, request, jsonify
from flask_cors import CORS
import cohere
import PyPDF2
import os
import io
import json

app = Flask(__name__)
CORS(app)

co = cohere.Client(os.environ.get("COHERE_API_KEY"))
ORANGE_CASH_NUMBER = "01289590022"
SUBSCRIPTION_PRICE = "100 جنيه في الشهر"

@app.route('/api/generate', methods=['POST'])
def generate_exam():
    try:
        pdf_file = request.files['pdf']
        grade = request.form.get('grade')
        lesson = request.form.get('lesson')
        mcq_count = int(request.form.get('mcqCount', 5))
        essay_count = int(request.form.get('essayCount', 2))
        activation_code = request.form.get('activationCode')

        if activation_code!= 'ANWAR2026':
            return jsonify({
                "error": f"كود التفعيل غير صحيح. سعر الاشتراك {SUBSCRIPTION_PRICE}. للاشتراك حوّل على Orange Cash: {ORANGE_CASH_NUMBER} وابعتلنا صورة التحويل على واتساب"
            }), 401

        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file.read()))
        text_content = ""
        for page in pdf_reader.pages[:3]:
            text_content += page.extract_text()

        text_content = text_content[:4000]

        if len(text_content) < 50:
            return jsonify({"error": "الملف فاضي أو متصور. لازم نص"}), 400

        prompt = f"""انت مدرس شاطر. اعمل امتحان من النص ده.
الصف: {grade}
الدرس: {lesson}
المطلوب: {mcq_count} سؤال اختيار من متعدد بأربع اختيارات. و {essay_count} سؤال مقالي.
النص:
{text_content}

طلع النتيجة JSON بالشكل ده بالظبط بدون أي كلام تاني:
{{"mcq":[{{"q":"السؤال","choices":["أ","ب","ج","د"],"answer":"أ"}}],"essay":[{{"q":"السؤال","answer":"الإجابة النموذجية"}}]}}"""

        response = co.chat(
            model="command-r-plus",
            message=prompt,
            temperature=0.3,
            max_tokens=1500
        )
        
        exam_json = json.loads(response.text)
        return jsonify(exam_json)

    except json.JSONDecodeError:
        return jsonify({"error": "الموديل رجع رد مش مظبوط. جرب تاني"}), 500
    except Exception as e:
        print(e)
        return jsonify({"error": "الملف كبير أو السيرفر مشغول. جرب ملف أصغر"}), 500

if __name__ == '__main__':
    app.run()

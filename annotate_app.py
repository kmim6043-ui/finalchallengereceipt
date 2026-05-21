from flask import Flask, request, jsonify, render_template
from PIL import Image, ImageDraw, ImageFont
import pytesseract
import re
import base64
from io import BytesIO

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

app = Flask(__name__)

##home
@app.route('/')
def home():
    return render_template('index.html')    

##get data from receipt
@app.route('/get_receipt_data', methods=['POST'])
def get_receipt_data():
    photo = request.files['photo'] #photo from user
    image = Image.open(photo).convert('RGB') #open photo

    tax_rate = float(request.form['tax_rate']) 

    #get text OCR
    text = pytesseract.image_to_string(image)
    print(text)

    subtotal_match = re.search(
        r'(subtotal|sub total|item total)\s*\$?(\d+\.\d{2})',
        text, re.IGNORECASE
    )
    if subtotal_match:
        subtotal = float(subtotal_match.group(2))
    else:
        return jsonify({'error': 'Could not find Subtotal'})

    ##annotate
    draw = ImageDraw.Draw(image)
    new_total = subtotal * (1 + tax_rate / 100)
    message = (
        f'With a {tax_rate}% tax, '
        f'the total cost would be ${new_total:.2f}'
    )

    draw.rectangle([(20, 20), (650, 120)], fill=(108, 184, 174), outline='black', width=2)
    font = ImageFont.truetype("JimNightshade-Regular.ttf", 35)
    draw.text((40, 50), message, fill='black', font=font)

    buffer = BytesIO()
    image.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')

    #return json
    return jsonify({
        'subtotal': subtotal,
        'new_total': round(new_total, 2),
        'receipt': {
            'data': img_str,
            'media_type': 'image/png'
        }
    })


if __name__ == '__main__':
    app.run(debug=True)

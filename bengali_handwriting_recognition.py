import os
from google.cloud import vision
import io
from flask import Flask, render_template, request, flash
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from wtforms.validators import DataRequired
from werkzeug.utils import secure_filename
from PIL import Image, ImageDraw
import base64

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Replace with your own secret key

class UploadForm(FlaskForm):
    image = FileField('Image File', validators=[DataRequired()])
    submit = SubmitField('Recognize Text')

def recognize_bengali_handwriting(image_path):
    client = vision.ImageAnnotatorClient()

    with io.open(image_path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.document_text_detection(image=image, image_context={"language_hints": ["bn"]})
    document = response.full_text_annotation

    return document.text

@app.route('/', methods=['GET', 'POST'])
def index():
    form = UploadForm()
    recognized_text = None
    uploaded_image = None

    if form.validate_on_submit():
        image_file = form.image.data
        image_filename = secure_filename(image_file.filename)
        image_path = os.path.join(os.getcwd(), image_filename)
        image_file.save(image_path)

        with open(image_path, "rb") as img_file:
            encoded_img = base64.b64encode(img_file.read()).decode("utf-8")
            uploaded_image = f"data:image/png;base64,{encoded_img}"

        recognized_text = recognize_bengali_handwriting(image_path)
        os.remove(image_path)

    return render_template('index.html', form=form, recognized_text=recognized_text, uploaded_image=uploaded_image)

if __name__ == "__main__":
    app.run(debug=True)

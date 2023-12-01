# requires the following libraries and dependencies to function properly:
# pip install Flask  -----> for 
# pip install Werkzeug
# pip install face_recognition
# pip install Pillow

import os
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
import face_recognition
from PIL import Image

app = Flask(__name__)
app.template_folder = 'templates'

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

known_face_encodings = []
known_face_names = []

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_known_faces():
    # Load known faces from the 'output' directory
    output_folder = 'output'
    for person_folder in os.listdir(output_folder):
        person_folder_path = os.path.join(output_folder, person_folder)
        if os.path.isdir(person_folder_path):
            known_face_names.append(person_folder)

            face_image_path = os.path.join(person_folder_path, f"{person_folder}_1.jpg")

            # Check if the face image file exists before attempting to load it
            if os.path.exists(face_image_path):
                face_image = face_recognition.load_image_file(face_image_path)
                face_encoding = face_recognition.face_encodings(face_image)[0]
                known_face_encodings.append(face_encoding)

def find_person(face_encoding):
    # Compare the input face encoding with known face encodings
    matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
    for i, match in enumerate(matches):
        if match:
            return known_face_names[i]
    return None

def extract_faces(image_path, output_folder):
    image = face_recognition.load_image_file(image_path)
    face_locations = face_recognition.face_locations(image)
    face_encodings = face_recognition.face_encodings(image, face_locations)

    for i, (face_location, face_encoding) in enumerate(zip(face_locations, face_encodings)):
        person_name = find_person(face_encoding)

        if person_name is None:
            # If the person is not recognized, prompt the user for a name
            person_name = input(f"Enter the name for this face (person_{len(known_face_names) + 1}): ").strip() or f"person_{len(known_face_names) + 1}"
            known_face_names.append(person_name)
            known_face_encodings.append(face_encoding)

        person_folder = os.path.join(output_folder, person_name)

        if not os.path.exists(person_folder):
            os.makedirs(person_folder)

        output_path = os.path.join(person_folder, f"{person_name}_{i + 1}.jpg")
        pil_image = Image.fromarray(image[face_location[0]:face_location[2], face_location[3]:face_location[1]])
        pil_image.save(output_path)


# Define a Flask route for uploading images, processing them using face recognition, and displaying success or error messages in the HTML template.
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('index.html', error='No file part')

        file = request.files['file']

        if file.filename == '':
            return render_template('index.html', error='No selected file')

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            output_folder = 'output'
            extract_faces(file_path, output_folder)

            return render_template('index.html', success='File uploaded and faces extracted!')

    return render_template('index.html')

if __name__ == '__main__':
    load_known_faces()
    app.run(debug=True)
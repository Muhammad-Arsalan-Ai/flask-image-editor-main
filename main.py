# Import libraries
import cv2
import numpy as np
from flask import Flask, render_template, request, flash
from werkzeug.utils import secure_filename
import os

# Define upload folder and allowed extensions
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'webp', 'jpg', 'jpeg', 'gif'}

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to process image with various operations
def processImage(filename, operation):
    print(f"the operation is {operation} and filename is {filename}")
    img = cv2.imread(f"uploads/{filename}")

    # Define background removal function
    def remove_background(img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        max_area = 0
        max_contour = None
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > max_area:
                max_area = area
                max_contour = cnt
        mask = np.zeros_like(gray)
        cv2.drawContours(mask, [max_contour], -1, 255, -1)
        mask_inv = cv2.bitwise_not(mask)
        img_no_bg = cv2.bitwise_and(img, img, mask=mask_inv)
        return img_no_bg


    match operation:
        case "cgray":
            imgProcessed = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            newFilename = f"static/{filename}"
            cv2.imwrite(newFilename, imgProcessed)
            return newFilename
        case "cwebp":
            newFilename = f"static/{filename.split('.')[0]}.webp"
            cv2.imwrite(newFilename, img)
            return newFilename
        case "cjpg":
            newFilename = f"static/{filename.split('.')[0]}.jpg"
            cv2.imwrite(newFilename, img)
            return newFilename
        case "cpng":
            newFilename = f"static/{filename.split('.')[0]}.png"
            cv2.imwrite(newFilename, img)
            return newFilename
        case "cnobg":
            img_no_bg = remove_background(img)
            newFilename = f"static/{filename.split('.')[0]}_nobg.png"
            cv2.imwrite(newFilename, img_no_bg)
            return newFilename
        case _:
            # Handle unexpected operation
            return f"Invalid operation: {operation}"

# Homepage route
@app.route("/")
def home():
    return render_template("index.html")

# About route
@app.route("/about")
def about():
    return render_template("about.html")

# Edit route
@app.route("/edit", methods=["GET", "POST"])
def edit():
    if request.method == "POST":
        operation = request.form.get("operation")
        # Check for file in request
        if 'file' not in request.files:
            flash('No file part')
            return "error"
        file = request.files['file']
        # Check for empty filename
        if file.filename == '':
            flash('No selected file')
            return "error no selected file"
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            new_filename = processImage(filename, operation)
            flash(f"Your image has been processed and is available <a href='/{new_filename}' target='_blank'>here</a>")
            return render_template("index.html")

app.run(debug=True, port=5001)
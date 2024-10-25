from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import json
from werkzeug.utils import secure_filename
from index import process_uploaded_pdf
import time

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/test', methods=['GET'])
def test():
    return jsonify({'message': 'Server is working'}), 200

@app.route('/process-pdf', methods=['POST'])
def process_pdf():
    print("Received request to /process-pdf")  # Add this line for debugging
    start_time = time.time()
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        try:
            # Process the uploaded PDF
            result, json_filename = process_uploaded_pdf(file_path)
            
            # Clean up the uploaded file
            os.remove(file_path)
            
            end_time = time.time()
            print(f"Total API request processing time: {end_time - start_time:.2f} seconds")
            return jsonify({
                'message': 'PDF processed successfully',
                'data': result,
                'filename': json_filename
            }), 200
        except Exception as e:
            # Clean up the uploaded file in case of error
            if os.path.exists(file_path):
                os.remove(file_path)
            print(f"Error occurred. Total API request processing time: {time.time() - start_time:.2f} seconds")
            print(f"Error processing PDF: {e}")
            return jsonify({'error': 'Internal Server Error'}), 500
    else:
        return jsonify({'error': 'File type not allowed'}), 400

@app.route('/download_json/<filename>', methods=['GET'])
def download_json(filename):
    try:
        return send_file(filename, as_attachment=True)
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)

from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
db = SQLAlchemy(app)

# Define the PDF model
class PDFFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, server_default=db.func.now())

db.create_all()

PDF_FOLDER = 'pdfs'
os.makedirs(PDF_FOLDER, exist_ok=True)

@app.route('/pdfs', methods=['GET'])
def get_pdfs():
    pdf_files = PDFFile.query.all()
    pdf_list = [pdf.filename for pdf in pdf_files]
    return jsonify(pdf_list)

@app.route('/pdfs/<filename>', methods=['GET'])
def get_pdf(filename):
    return send_from_directory(PDF_FOLDER, filename)

@app.route('/pdfs', methods=['POST'])
def add_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    if file and file.filename.endswith('.pdf'):
        file.save(os.path.join(PDF_FOLDER, file.filename))
        new_pdf = PDFFile(filename=file.filename)
        db.session.add(new_pdf)
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'error': 'Invalid file format'})

@app.route('/pdfs/<filename>', methods=['DELETE'])
def delete_pdf(filename):
    pdf_file = PDFFile.query.filter_by(filename=filename).first()
    if pdf_file:
        db.session.delete(pdf_file)
        db.session.commit()
        os.remove(os.path.join(PDF_FOLDER, filename))
        return jsonify({'success': True})
    return jsonify({'error': 'File not found'})

@app.route('/pdfs/version/<filename>', methods=['POST'])
def version_control(filename):
    # Implement version control logic here
    pass

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

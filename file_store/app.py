from flask import Flask, request, jsonify
import os, uuid

app = Flask(__name__)
UPLOAD_DIR = "/app/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.route("/upload", methods=["POST"])
def upload():
    f = request.files["file"]
    file_id = uuid.uuid4().hex
    save_path = os.path.join(UPLOAD_DIR, file_id)
    f.save(save_path)
    return jsonify({
        "file_id": file_id,
        "filename": f.filename
    })

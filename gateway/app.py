from flask import Flask, request, jsonify
import os, requests

app = Flask(__name__)

FILE_STORE = os.environ["FILE_STORE_URL"]  # e.g. "http://file_store:5000"
ANALYSIS   = os.environ["ANALYSIS_URL"]    # e.g. "http://analysis:5000"

@app.route("/upload", methods=["POST"])
def upload():
    # grab the file
    f = request.files.get("file")
    if not f:
        return "no file provided", 400

    # 1) forward to file_store
    fs_resp = requests.post(
        f"{FILE_STORE}/upload",
        files={"file": (f.filename, f.stream, f.mimetype)}
    )
    if fs_resp.status_code != 200:
        return "file_store error", 502

    # assume it returns JSON { "file_id": "...", ... }
    file_info = fs_resp.json()

    # 2) ask analysis to process it
    an_resp = requests.post(
        f"{ANALYSIS}/analyze",
        json={"file_id": file_info["file_id"]}
    )
    if an_resp.status_code != 200:
        return "analysis error", 502

    result = an_resp.json()

    # 3) merge and return
    return jsonify({
      "file": file_info,
      "analysis": result
    }), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

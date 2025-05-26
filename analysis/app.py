# analysis/app.py
from flask import Flask, request, jsonify, abort
import sqlite3, os

DB_PATH = os.path.join(os.path.dirname(__file__), 'stats.db')

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect(DB_PATH)
    return conn

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    file_id = data.get("file_id")
    # … do your analysis lookup, stats.db queries, etc. …
    result = {
      "file_id": file_id,
      "score": 0.42,            # example payload
      "summary": "…",
    }
    return jsonify(result), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

@app.route('/stats', methods=['POST'])
def stats():
    payload = request.get_json()
    if not payload or 'text' not in payload:
        abort(400, "need JSON with 'text'")
    text = payload['text']
    length = len(text)
    words = len(text.split())

    db = get_db()
    cur = db.cursor()
    cur.execute('''
      CREATE TABLE IF NOT EXISTS stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        length INTEGER,
        words INTEGER
      )
    ''')
    cur.execute(
      'INSERT INTO stats(length,words) VALUES(?,?)',
      (length, words)
    )
    db.commit()
    rowid = cur.lastrowid
    return jsonify({'id': rowid, 'length': length, 'words': words})

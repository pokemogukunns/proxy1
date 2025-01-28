from flask import Flask, request, send_file, jsonify
import requests
from io import BytesIO

app = Flask(__name__)

@app.route('/proxy', methods=['GET'])
def proxy():
    link = request.args.get('url')
    if not link:
        return jsonify({"error": "URL is required"}), 400

    try:
        response = requests.get(link, stream=True, timeout=10)
        response.raise_for_status()  # HTTPエラーを例外として扱う
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Failed to fetch image", "details": str(e)}), 500

    content_type = response.headers.get('Content-Type', 'application/octet-stream')
    return send_file(
        BytesIO(response.content),
        mimetype=content_type
    )

if __name__ == '__main__':
    app.run(debug=True)

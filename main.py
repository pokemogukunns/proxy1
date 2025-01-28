from flask import Flask, request, jsonify
import subprocess
import re

app = Flask(__name__)

@app.route('/proxy', methods=['GET'])
def proxy():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "URL is required"}), 400

    # SafariのUser-Agentヘッダー
    safari_headers = [
        "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Version/14.1.2 Safari/537.36"
    ]

    try:
        # curlコマンドを実行してHTMLを取得
        curl_command = ["curl", "-L", "-H", safari_headers[0], url]
        result = subprocess.run(
            curl_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10
        )

        if result.returncode != 0:
            return jsonify({"error": "Failed to fetch URL", "details": result.stderr}), 500

        # HTMLレスポンスから画像URLを抽出
        html_content = result.stdout
        image_urls = re.findall(r'https?://[^\s"]+\.(?:jpg|jpeg|png|gif)', html_content)

        if not image_urls:
            return jsonify({"message": "No images found", "details": html_content[:500]}), 200

        return jsonify({"images": image_urls}), 200

    except Exception as e:
        return jsonify({"error": "Error executing curl", "details": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)

import requests
import subprocess
import re
import base64
from flask import Flask, request, jsonify, render_template_string
from PIL import Image
from io import BytesIO

app = Flask(__name__)

# SafariのUser-Agentを指定
SAFARI_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Version/14.1.2 Safari/537.36"
)

# HTMLテンプレート（画像を表示するためのもの）
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Image Viewer</title>
</head>
<body>
    <h1>Fetched Images</h1>
    {% for image in images %}
    <div>
        <img src="{{ image }}" alt="Image" style="max-width: 100%; height: auto;">
    </div>
    {% endfor %}
</body>
</html>
"""

def fetch_html_with_curl(url):
    try:
        # curlコマンドを実行してHTMLを取得
        curl_command = [
            "curl", "-s", "-L",
            "-A", SAFARI_USER_AGENT,  # SafariのUser-Agentを設定
            url
        ]
        result = subprocess.run(curl_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # エラーがあれば処理
        if result.returncode != 0:
            return {"error": result.stderr.strip()}

        # HTMLコンテンツを取得
        html_content = result.stdout

        return html_content

    except Exception as e:
        return {"error": str(e)}

def extract_images_from_html(html_content):
    # imgタグから画像URLを抽出
    image_urls = re.findall(r'<img[^>]+src="([^"]+)"', html_content)

    # 絶対URLを生成
    absolute_urls = [url if url.startswith("http") else url for url in image_urls]

    return absolute_urls

def fetch_and_display_image(image_url):
    try:
        # 画像を取得
        response = requests.get(image_url)
        response.raise_for_status()

        # 画像データをBase64にエンコード
        encoded_image = base64.b64encode(response.content).decode('utf-8')

        # Base64データをデコードして画像を復元
        decoded_image = base64.b64decode(encoded_image)
        image = Image.open(BytesIO(decoded_image))

        # 画像を表示
        image.show()

        return encoded_image

    except Exception as e:
        print(f"Error: {e}")
        return None

@app.route('/proxy', methods=['GET'])
def proxy():
    # クエリパラメータからURLを取得
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "URL is required"}), 400

    # curlでHTMLを取得
    html_content = fetch_html_with_curl(url)

    # エラーが発生した場合
    if isinstance(html_content, dict) and "error" in html_content:
        return jsonify(html_content), 500

    # 画像URLを抽出
    image_urls = extract_images_from_html(html_content)

    # Base64エンコードして画像を表示
    for img_url in image_urls[:5]:  # 最初の5つだけ試しに表示
        fetch_and_display_image(img_url)

    # HTMLページを生成して画像を表示
    return render_template_string(HTML_TEMPLATE, images=image_urls)

if __name__ == '__main__':
    app.run(debug=True)



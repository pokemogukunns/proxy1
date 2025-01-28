import requests
import subprocess
import re
import base64
from flask import Flask, request, Response
from PIL import Image
from io import BytesIO

app = Flask(__name__)

# SafariのUser-Agentを指定
SAFARI_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Version/14.1.2 Safari/537.36"
)



def fetch_html_with_curl(url):
    try:
        # curlコマンドを実行してHTMLを取得
        curl_command = [
            "curl", "-s", "-L",
            "-A", SAFARI_USER_AGENT,  # SafariのUser-Agentを設定
            "-H", "X-Location: Japan, Kanagawa, Sagamihara, Kamitsuruma",  # カスタムヘッダーを追加
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
    return image_urls

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

        # Base64エンコード済み画像URLを生成
        return f"data:image/jpeg;base64,{encoded_image}"

    except Exception as e:
        print(f"Error: {e}")
        return None

@app.route('/proxy', methods=['GET'])
def proxy():
    # クエリパラメータからURLを取得
    url = request.args.get('url')
    if not url:
        return {"error": "URL is required"}, 400

    # curlでHTMLを取得
    html_content = fetch_html_with_curl(url)

    # エラーが発生した場合
    if isinstance(html_content, dict) and "error" in html_content:
        return html_content, 500

    # 画像URLを抽出
    image_urls = extract_images_from_html(html_content)

    # 画像URLをBase64エンコードして表示
    for img_url in image_urls:
        encoded_image = fetch_and_display_image(img_url)
        if encoded_image:
            # HTMLのsrcにBase64エンコードされた画像URLを挿入
            html_content = html_content.replace(img_url, encoded_image)

    # 修正したHTMLをそのまま返す
    return Response(html_content, mimetype='text/html')

if __name__ == '__main__':
    app.run(debug=True)

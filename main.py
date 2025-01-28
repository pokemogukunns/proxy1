from flask import Flask, request, jsonify
import subprocess
import re

app = Flask(__name__)

# SafariのUser-Agentを指定
SAFARI_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Version/14.1.2 Safari/537.36"
)

def fetch_images_with_curl(url):
    try:
        # curlコマンドを実行
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

        # imgタグから画像URLを抽出
        image_urls = re.findall(r'<img[^>]+src="([^"]+)"', html_content)

        # 絶対URLを生成
        absolute_urls = [url if url.startswith("http") else url for url in image_urls]

        return absolute_urls

    except Exception as e:
        return {"error": str(e)}

@app.route('/proxy', methods=['GET'])
def proxy():
    # クエリパラメータからURLを取得
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "URL is required"}), 400

    # Curlを使用して画像を取得
    result = fetch_images_with_curl(url)

    # エラーが発生した場合
    if isinstance(result, dict) and "error" in result:
        return jsonify(result), 500

    # 画像が見つからなかった場合
    if not result:
        return jsonify({"message": "No images found"}), 200

    # 取得した画像URLを返す
    return jsonify({"images": result}), 200

if __name__ == '__main__':
    app.run(debug=True)

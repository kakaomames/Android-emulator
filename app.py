# app.py（初期構造テンプレート - Flask）

from flask import Flask, request, send_file, redirect, url_for, jsonify, render_template_string
import os
import shutil
import uuid
from apkutils2 import APK
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = './app_storage'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    apps = [d for d in os.listdir(UPLOAD_FOLDER) if os.path.isdir(os.path.join(UPLOAD_FOLDER, d))]
    return render_template_string("""
    <h1>アップロード</h1>
    <form method="post" action="/upload" enctype="multipart/form-data">
        <input type="file" name="apk">
        <input type="submit">
    </form>
    <hr>
    <h2>インストール済み</h2>
    {% for pkg in apps %}
      <div><a href="/app?i={{ pkg }}">{{ pkg }}</a></div>
    {% endfor %}
    """, apps=apps)

@app.route('/upload', methods=['POST'])
def upload_apk():
    apk_file = request.files['apk']
    if not apk_file:
        return 'No file uploaded', 400

    # 一意IDの生成と保存先決定
    tmp_path = os.path.join(app.config['UPLOAD_FOLDER'], 'tmp.apk')
    apk_file.save(tmp_path)

    apk = APK(tmp_path)
    pkg = apk.package_name
    app_dir = os.path.join(app.config['UPLOAD_FOLDER'], pkg)
    os.makedirs(app_dir, exist_ok=True)
    shutil.move(tmp_path, os.path.join(app_dir, 'base.apk'))

    # アイコン抽出（省略。あとで詳細）
    icon_path = os.path.join(app_dir, 'icon.png')
    try:
        icon = apk.icon_data
        with open(icon_path, 'wb') as f:
            f.write(icon)
    except:
        pass

    return redirect(url_for('index'))

@app.route('/icon')
def icon():
    pkg = request.args.get('i')
    icon_path = os.path.join(app.config['UPLOAD_FOLDER'], pkg, 'icon.png')
    if os.path.exists(icon_path):
        return send_file(icon_path, mimetype='image/png')
    return 'Icon not found', 404

@app.route('/app')
def app_detail():
    pkg = request.args.get('i')
    app_dir = os.path.join(app.config['UPLOAD_FOLDER'], pkg)
    if not os.path.exists(app_dir):
        return 'App not found', 404
    return render_template_string("""
    <h1>{{ pkg }}</h1>
    <img src="/icon?i={{ pkg }}" style="width:72px;height:72px"><br>
    <a href="/run?i={{ pkg }}">起動</a>
    """, pkg=pkg)

@app.route('/run')
def run_app():
    # 今はまだ未実装：ただの模擬表示
    pkg = request.args.get('i')
    return f"アプリ {pkg} を起動（模擬）"

if __name__ == '__main__':
    app.run(debug=True)

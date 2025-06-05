# app.py（初期構造テンプレート - Flask）

from flask import Flask, request, send_file, redirect, url_for, jsonify, render_template_string
import os
import shutil
import uuid
from apkutils2 import APK
from werkzeug.utils import secure_filename
import zipfile
import ctypes

app = Flask(__name__)
UPLOAD_FOLDER = './app_storage'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Java型→ctypes型の対応
java_to_ctypes = {
    "int": ctypes.c_int,
    "float": ctypes.c_float,
    "double": ctypes.c_double,
    "long": ctypes.c_long,
    "boolean": ctypes.c_bool,
    "byte": ctypes.c_byte,
    "char": ctypes.c_char,
    "String": ctypes.c_char_p,
    "jstring": ctypes.c_char_p,
    "jint": ctypes.c_int,
    "jboolean": ctypes.c_bool
}

# Java型→Python型の対応
java_to_python = {
    "int": int,
    "float": float,
    "double": float,
    "long": int,
    "boolean": lambda x: x.lower() == 'true',
    "byte": int,
    "char": lambda x: x[0],
    "String": str,
    "jstring": str,
    "jint": int,
    "jboolean": lambda x: x.lower() == 'true'
}

# クラス名と関数名からJNI名に変換
def to_jni_name(class_name, method_name):
    return "Java_" + class_name.replace('.', '_') + "_" + method_name

# 登録済みJavaクラスと関数
jni_registry = {}

@app.route('/register_class', methods=['POST'])
def register_class():
    data = request.json
    class_name = data['class']
    methods = data['methods']  # 例: [{"name": "sum", "args": ["int", "int"]}]

    if class_name not in jni_registry:
        jni_registry[class_name] = {}
    for method in methods:
        jni_name = to_jni_name(class_name, method['name'])
        jni_registry[class_name][method['name']] = {
            "jni": jni_name,
            "args": method['args']
        }

    return jsonify({"status": "registered", "jni_names": jni_registry[class_name]})

@app.route('/invoke', methods=['POST'])
def invoke_method():
    if request.is_json:
        data = request.get_json(force=True)
    else:
        data = {
            'package': request.form['package'],
            'class': request.form['class'],
            'method': request.form['method'],
            'args': request.form.get('args', '')
        }
        args_str = data['args'].strip()
        if args_str:
            class_name = data['class']
            method_name = data['method']
            method_info = jni_registry.get(class_name, {}).get(method_name)
            if not method_info:
                return jsonify({"error": "Class or method not registered"}), 400
            arg_types = method_info['args']
            try:
                data['args'] = [java_to_python.get(t, str)(v.strip()) for t, v in zip(arg_types, args_str.split(','))]
            except Exception as e:
                return jsonify({"error": f"Argument conversion error: {str(e)}"}), 400
        else:
            data['args'] = []

    pkg = data['package']
    class_name = data['class']
    method_name = data['method']
    args = data['args']

    app_dir = os.path.join(app.config['UPLOAD_FOLDER'], pkg)
    lib_files = find_libs(app_dir)

    if class_name not in jni_registry or method_name not in jni_registry[class_name]:
        return jsonify({"error": "Class or method not registered"}), 400

    jni_info = jni_registry[class_name][method_name]
    jni_name = jni_info['jni']
    arg_types = [java_to_ctypes.get(t, ctypes.c_void_p) for t in jni_info['args']]

    result = None
    error = None
    for lib_path in lib_files:
        try:
            lib = ctypes.CDLL(lib_path)
            func = getattr(lib, jni_name)
            func.restype = ctypes.c_int  # TODO: 返り値型も登録から取得できるようにする
            func.argtypes = arg_types
            result = func(*args)
            break
        except Exception as e:
            error = str(e)
    if result is not None:
        return jsonify({"result": result})
    return jsonify({"error": error}), 500

def extract_libs(apk_path, dest_dir):
    """APKからlibディレクトリにある.soファイルを展開する"""
    with zipfile.ZipFile(apk_path, 'r') as zf:
        for f in zf.namelist():
            if f.startswith('lib/') and f.endswith('.so'):
                target_path = os.path.join(dest_dir, f)
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                with open(target_path, 'wb') as out:
                    out.write(zf.read(f))

def find_libs(app_dir):
    """展開された.soファイルのパス一覧を返す"""
    lib_paths = []
    for root, _, files in os.walk(os.path.join(app_dir, 'lib')):
        for file in files:
            if file.endswith('.so'):
                lib_paths.append(os.path.join(root, file))
    return lib_paths

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

    tmp_path = os.path.join(app.config['UPLOAD_FOLDER'], 'tmp.apk')
    apk_file.save(tmp_path)

    apk = APK(tmp_path)
    pkg = apk.package_name
    app_dir = os.path.join(app.config['UPLOAD_FOLDER'], pkg)
    os.makedirs(app_dir, exist_ok=True)
    final_apk_path = os.path.join(app_dir, 'base.apk')
    shutil.move(tmp_path, final_apk_path)

    icon_path = os.path.join(app_dir, 'icon.png')
    try:
        icon = apk.icon_data
        with open(icon_path, 'wb') as f:
            f.write(icon)
    except:
        pass

    extract_libs(final_apk_path, app_dir)

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
    pkg = request.args.get('i')
    app_dir = os.path.join(app.config['UPLOAD_FOLDER'], pkg)
    lib_files = find_libs(app_dir)
    loaded = []
    for so_path in lib_files:
        try:
            ctypes.CDLL(so_path)
            loaded.append(os.path.basename(so_path))
        except Exception as e:
            loaded.append(f"{os.path.basename(so_path)}: failed ({e})")
    return render_template_string("""
    <h1>{{ pkg }} 実行</h1>
    <ul>
    {% for so in loaded %}
        <li>{{ so }}</li>
    {% endfor %}
    </ul>
    <hr>
    <form method="post" action="/invoke">
        <input type="hidden" name="package" value="{{ pkg }}">
        <input name="class" placeholder="クラス名">
        <input name="method" placeholder="メソッド名">
        <input name="args" placeholder="引数（カンマ区切り）">
        <input type="submit" value="JNI呼び出し">
    </form>
    """, pkg=pkg, loaded=loaded)

if __name__ == '__main__':
    app.run(debug=True)

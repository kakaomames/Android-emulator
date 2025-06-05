from apkutils import APK
import hashlib

def parse_apk(apk_path: str) -> dict:
    apk = APK(apk_path)

    manifest = apk.get_manifest()
    cert = apk.get_signature()

    package_info = {
        "package_name": manifest["@package"],
        "version_code": int(manifest["@android:versionCode"]),
        "version_name": manifest["@android:versionName"],
        "label": apk.get_app_name(),
        "icon_path": "",  # 省略: 抜き出し処理は別途対応
        "apk_path": apk_path,
        "activities": [],
        "permissions": apk.get_permissions(),
        "signatures": [hashlib.sha256(cert).hexdigest()] if cert else [],
    }

    for act in apk.get_activities():
        package_info["activities"].append({
            "name": act,
            "exported": False,  # 詳細取得は後で
            "intent_filters": "[]"
        })

    return package_info

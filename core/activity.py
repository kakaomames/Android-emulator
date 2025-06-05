from core.pm_db import get_package

def start_activity(package_name: str, activity_class: str = None):
    pkg = get_package(package_name)
    if not pkg:
        print(f"[ERROR] Package '{package_name}' not found.")
        return False

    print(f"[INFO] Launching Activity:")
    print(f" - Package: {package_name}")
    if activity_class:
        print(f" - Activity: {activity_class}")
    print(f" - Label: {pkg['label']}")
    print(f" - Icon: {pkg['icon_path']}")
    print(f" - APK: {pkg['apk_path']}")
    
    # 擬似実行: ここで JavaVM に渡して so を動かすでもいい
    # 現状はログ出力で表現（後にGUIやWebUIで置き換え可能）
    print(f"[DUMMY RUN] Launching simulated activity window... ✅")
    return True

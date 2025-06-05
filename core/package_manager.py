# core/package_manager.py

from core.broadcast_bus import BroadcastBus
from core.intent import Intent

class PackageManagerService:
    def __init__(self, broadcast_bus: BroadcastBus):
        self.installed_packages: Dict[str, PackageInfo] = {}
        self.broadcast_bus = broadcast_bus

    def install_package(self, apk_path: str) -> PackageInfo:
        package_info = parse_apk(apk_path)  # APKから情報取得
        package_name = package_info.package_name
        self.installed_packages[package_name] = package_info

        # ブロードキャスト送信！
        intent = Intent(
            action="android.intent.action.PACKAGE_ADDED",
            extras={"package": package_name}
        )
        self.broadcast_bus.send_broadcast(intent)

        return package_info

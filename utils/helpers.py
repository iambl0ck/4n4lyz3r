import subprocess
import platform

def run_hidden_subprocess(cmd_list, timeout=None):
    """
    Cross-platform subprocess executor.
    Crucially injects creationflags=subprocess.CREATE_NO_WINDOW on Windows
    to prevent annoying black console flashes (e.g. nvidia-smi, wmic).
    """
    kwargs = {
        "stdout": subprocess.PIPE,
        "stderr": subprocess.PIPE,
        "text": True
    }

    if platform.system() == "Windows":
        # python 3.7+ CREATE_NO_WINDOW
        kwargs["creationflags"] = 0x08000000

    if timeout is not None:
        kwargs["timeout"] = timeout

    return subprocess.run(cmd_list, **kwargs)

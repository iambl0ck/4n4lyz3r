<div align="center">

```text
  _  _          _  _   _             _____
 | || |        | || | | |           |____ |
 | || |_  _ __ | || |_| | _   _  ____   / /_ __
 |__   _|| '_ \|__   _| || | | ||_  /   \ \ '__|
    | |  | | | |  | | | || |_| | / /.___/ / |
    |_|  |_| |_|  |_| |_| \__, |/___|\____/|_|
                           __/ |
                          |___/
```

# 4n4lyz3r

**Enterprise-Grade System Monitor & Active Threat Defense**

[![Build Status](https://img.shields.io/github/actions/workflow/status/iambl0ck/4n4lyz3r/build.yml?branch=main&style=for-the-badge)](https://github.com/iambl0ck/4n4lyz3r/actions)
[![Python Version](https://img.shields.io/badge/python-3.12-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![OS Support](https://img.shields.io/badge/os-Windows%20%7C%20macOS%20%7C%20Linux-green?style=for-the-badge)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

</div>

---

## 👁️ The Vision

**4n4lyz3r** is an ultra-lightweight, cross-platform, enterprise-grade system monitor and active threat defense tool. Designed with a modern, glassmorphic cyberpunk aesthetic, it bypasses heavy Python wrappers by tapping directly into native C-level OS hooks to deliver microsecond-accurate hardware telemetry.

Built for System Administrators, Security Researchers, and Power Users who demand absolute control, **4n4lyz3r** actively hunts anomalous processes, fetches raw unrounded S.M.A.R.T. hardware data, and maintains a strict zero-memory-leak footprint during months of uninterrupted background uptime.

---

## 🚀 Ultimate Feature List

*   **⚡ Deep C-Level Kernel Polling:** Bypasses standard wrappers, utilizing direct OS hooks (`ctypes.windll` on Windows, `/proc/stat` on Linux) to drop CPU polling overhead to literal microseconds.
*   **🛡️ Active Threat Heuristics:** Intelligently analyzes running executable paths in real-time. Flags processes originating from suspicious directories (e.g., Temp folders, Downloads, hidden Unix folders) with a stark `[SUSPICIOUS]` tag.
*   **⚔️ Interactive Process Manager:** A dedicated **Active Defense** tab allowing users to securely `Kill` or `Suspend` anomalous processes instantly.
*   **💾 S.M.A.R.T. Hardware Fetching:** Dives beyond OS-level summaries. Reads raw S.M.A.R.T. data, Disk Health, and Motherboard/BIOS firmware details natively via subprocesses (`wmic`, `sysfs`, `lsblk`).
*   **🌐 Network Security & IP Masking:** Monitors active TCP/UDP connections and listening ports. Automatically masks external/public IP addresses for privacy during screen sharing, while leaving local LAN IPs visible for debugging.
*   **👻 Headless System Tray Mode:** Clicking 'Close' gracefully minimizes the app to the System Tray. All CustomTkinter GUI rendering is suspended, dropping CPU/GPU footprint to near 0% while background daemon threads continue logging and alerting.
*   **🧠 Zero Memory Leaks:** Employs extreme static caching (fetching hardware capacities only once) and strict bounded `collections.deque` histories to guarantee the RAM footprint never expands over time. Explicit `gc.collect()` triggers ensure pristine memory hygiene.
*   **🚨 Smart Alert System:** In-app sliding CustomTkinter toast notifications trigger on high CPU (>90%), RAM (>95%), and Core Temp (>85°C) with strict 5-minute cooldowns to prevent spam.
*   **📝 Background Event Logger:** Asynchronous, non-blocking `RotatingFileHandler` (max 5MB) quietly logs anomalies to disk without freezing the UI.
*   **🛰️ Fleet Management (Secure REST API):** A zero-dependency `http.server` daemon serves a read-only `/api/health` endpoint on port 40404. Secured via a randomly generated `Authorization: Bearer` API key, allowing the main UI to monitor remote "4n4lyz3r" nodes asynchronously.
*   **🤖 AI-Powered Threat Intelligence:** Includes an "Analyze with AI" audit engine that feeds the system report snapshot directly to OpenAI's API. Bypasses heavy Python SDKs by using raw `urllib.request` REST calls, ensuring a massive LLM diagnostic capability with absolute zero executable bloat.

---

## 📥 Installation & Usage

**4n4lyz3r** is compiled via our automated CI/CD pipeline into standalone, zero-dependency executables. **You do not need to install Python to use this tool.**

### 1. Download the Executable
1. Navigate to the [Actions / Releases Tab](https://github.com/iambl0ck/4n4lyz3r/actions) of this repository.
2. Select the latest successful workflow run.
3. Scroll down to **Artifacts** and download the binary for your operating system:
   * `4n4lyz3r-windows-x64.exe` (Windows)
   * `4n4lyz3r-macos-x64.zip` (macOS .app bundle)
   * `4n4lyz3r-linux-x64` (Linux Standalone)

### 2. Launching & Administrator Privileges

> **⚠️ IMPORTANT:** When launching on Windows, the executable will prompt for **Administrator Privileges (UAC)**. On macOS/Linux, it is highly recommended to run the binary via `sudo`.

**Why does 4n4lyz3r need Admin/Root?**
To deliver true enterprise-grade metrics, the application must hook into the OS kernel. Administrator rights are required to:
* Fetch raw Motherboard BIOS and S.M.A.R.T. disk data.
* Read the executable paths of all system processes (for Threat Heuristics).
* Monitor all active TCP/UDP network connections.
* Successfully execute `Kill` or `Suspend` commands on anomalous processes.

*Graceful Fallback:* If you decline the Administrator prompt, **4n4lyz3r** will still run! It will gracefully fall back to standard user permissions, displaying general CPU/RAM/Disk stats, but deep features (like the Kill button or S.M.A.R.T. data) will be disabled or grayed out.

---

## 🛠️ Building from Source (For Developers)

If you prefer to audit the code and build it yourself:

```bash
# Clone the repository
git clone https://github.com/iambl0ck/4n4lyz3r.git
cd 4n4lyz3r

# Install requirements
pip install -r requirements.txt
pip install pyinstaller

# Run the cross-platform build script
python build.py
```
The compiled executable will be waiting in the `dist/` directory!

---

<div align="center">
<i>Built with absolute precision by Jules. Stay Secure.</i>
</div>

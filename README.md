# 🏎️ Need for Speed: Most Wanted Telemetry Dashboard

![GitHub forks](https://img.shields.io/github/forks/muki01/NFS_Most_Wanted_Telemetry_Dashboard?style=flat)
![GitHub Repo stars](https://img.shields.io/github/stars/muki01/NFS_Most_Wanted_Telemetry_Dashboard?style=flat)
![GitHub Issues or Pull Requests](https://img.shields.io/github/issues/muki01/NFS_Most_Wanted_Telemetry_Dashboard?style=flat)
![GitHub License](https://img.shields.io/github/license/muki01/NFS_Most_Wanted_Telemetry_Dashboard?style=flat)
![GitHub last commit](https://img.shields.io/github/last-commit/muki01/NFS_Most_Wanted_Telemetry_Dashboard)

This project is a real-time telemetry dashboard and custom speedometer UI designed for **Need for Speed: Most Wanted (2005)**. It works by scanning the game's running process memory, extracting dynamic data on the fly, and rendering it onto a high-performance, modern graphical user interface (UI).

With this application, you can view live telemetry data synchronized perfectly with your gameplay, including **Speed, Engine RPM, Current Gear, and Nitro (NOS) capacity**.

> 💡 **Looking for the core logic?** If you want to learn the fundamental concepts behind reading/writing game memory and how to find these addresses yourself, check out my beginner-friendly guide here: [game-memory-hacking-tutorial](https://github.com/muki01/Game_Memory_Hacking_Tutorial).


## ⚙️ How It Works & Installation

The application hooks into the `speed.exe` process using Python memory manipulation libraries to safely read specific memory offsets. It handles dynamic memory pointers to guarantee stability across different game sessions without crashing.

### 🔹 Prerequisites
Before running the dashboard, make sure you have the required libraries installed:
```bash
pip install -r requirements.txt
```

*(Make sure to include libraries like pymem, pyqt5 or tkinter inside your requirements.txt file)*

### 🔹 Running the Dashboard
1. Launch **Need for Speed: Most Wanted (2005)**.
2. Run the main Python script:
   ```bash
   python main.py
   ```

The custom dashboard UI will overlay or open next to your game, instantly displaying live data as you drive.

> [!WARNING] 
> This tool is developed strictly for educational, reverse-engineering, and single-player modding purposes. I am not responsible for any issues, bans, or data corruption that may occur during your testing. Use at your own risk.


## 📱 Pictures of the Application
<img width=70% src="https://github.com/user-attachments/assets/ae1a7ef9-3e96-4fc6-9d11-1a8b6743a4e1" />

---

## ☕ Support My Work

If you enjoy my projects and want to support me, you can do so through the links below:

[![Buy Me A Coffee](https://img.shields.io/badge/-Buy%20Me%20a%20Coffee-FFDD00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://www.buymeacoffee.com/muki01)
[![PayPal](https://img.shields.io/badge/-PayPal-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://www.paypal.com/donate/?hosted_button_id=SAAH5GHAH6T72)
[![GitHub Sponsors](https://img.shields.io/badge/-Sponsor%20Me%20on%20GitHub-181717?style=for-the-badge&logo=github)](https://github.com/sponsors/muki01)

---

## 📬 Contact

For information, job offers, collaboration, or sponsorship, you can contact me via email.

📧 Email: muksin.muksin04@gmail.com

---

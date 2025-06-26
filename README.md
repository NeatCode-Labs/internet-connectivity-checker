# Internet Connectivity Checker

A **tiny system-tray tool** for Linux that keeps an eye on your internet connection and lets you know at a glance whether you're online or offline.

*   Runs quietly in the panel / system-tray – no full-screen windows.
*   Shows a *connected* icon when the internet is reachable.
*   Shows a *disconnected* icon that **blinks** when the connection is lost.
*   Works on most modern desktop environments (GNOME, Cinnamon, XFCE, etc.)
*   Written in plain Python 3 – no compiling required.

## Screenshots

| Connected | Disconnected (blinking) |
|-----------|------------------------|
| <img src="icons/gtk-connect.svg" width="64"/> | <img src="icons/gtk-disconnect.svg" width="64"/> |

## Installation

### Dependencies

Make sure the following libraries are installed (they are available in every mainstream distro repository):

```bash
# Debian / Ubuntu / Linux Mint
sudo apt update && sudo apt install python3-gi gir1.2-gtk-3.0 gir1.2-appindicator3-0.1

# Arch / Manjaro
sudo pacman -S python-gobject gtk3 libappindicator-gtk3
```

### Clone the project

```bash
git clone https://github.com/NeatCode-Labs/InternetConnectivityChecker.git
cd InternetConnectivityChecker
chmod +x internet_connectivity_checker.py  # make the script executable
```

That's it – no further build steps.

## Quick Start

Run manually:

```bash
./internet_connectivity_checker.py &
```

A small icon should now appear in your tray. Click it for a menu with "Check Now", "About", and "Quit".

## Auto-start on Login

You have **two** options – pick the one you're comfortable with.

### Option 1: Graphical (Startup Applications)

Most desktop environments provide a *Startup Applications* or *Session & Startup* settings panel.

1. Open that panel.
2. Click **Add → Custom command** (wording may differ).
3. Name: *Internet Connectivity Checker*  
   Command: `/full/path/to/internet_connectivity_checker.py`  
   Comment: *Shows online/offline status in the tray*
4. Save – you're done.

*Pros*: easiest, visual, no `sudo` required.  
*Cons*: only runs when **you** log in; if several users share the PC you must repeat for each.

### Option 2: Systemd Service (User)

If you prefer the command-line and want a slightly more "system" approach:

```bash
# 1. Copy the service file
mkdir -p ~/.config/systemd/user
cp internet-connectivity-checker.service ~/.config/systemd/user/

# 2. Enable & start
systemctl --user enable internet-connectivity-checker.service
systemctl --user start internet-connectivity-checker.service
```

You can check status with `systemctl --user status internet-connectivity-checker.service`.

*Pros*: managed by systemd – auto-restarts if it crashes.  
*Cons*: a couple of terminal commands; still runs only for the current Linux user (not system-wide).

> **Tip:** To remove, simply run `systemctl --user disable --now internet-connectivity-checker.service` and delete the copied file.

### Option 3: Desktop Entry

Copy the provided desktop entry into your personal autostart folder:

```bash
mkdir -p ~/.config/autostart
cp internet-connectivity-checker.desktop ~/.config/autostart/
chmod +x ~/.config/autostart/internet-connectivity-checker.desktop
```

## Configuration

If you want to tweak the check interval, blink speed, or test URL, edit these constants at the top of `internet_connectivity_checker.py`:

```python
CHECK_INTERVAL = 5        # seconds between connectivity checks
BLINK_INTERVAL = 0.5      # seconds between icon blinks when disconnected
MAX_ATTEMPTS   = 3        # how many times to retry before marking offline
TEST_URL       = "https://www.google.com"  # URL used for connectivity check
```

`MAX_ATTEMPTS` controls how forgiving the checker is:

* **3 (default)** – the script tries three quick HTTP requests (1 s apart). Only if **all three** fail will the state flip to *Disconnected*.
* **Increase** (e.g. 5–6) if your link drops packets sporadically and you get false-positive disconnections.
* **Decrease** to 1 if you prefer an immediate reaction at the risk of a few blinks on brief hiccups.

### Custom Icons

The two default icons live in the project's `icons/` folder:

```
icons/gtk-connect.svg      # shown when online
icons/gtk-disconnect.svg   # shown (blinking) when offline
```

You have two ways to use your own graphics:

1. **Rename & replace**  
   • Create/choose two square images (SVG or PNG work best).  
   • Name them **gtk-connect.svg/png** and **gtk-disconnect.svg/png**.  
   • Drop them into the `icons/` folder – replacing the originals – and restart the script.

2. **Point the script to differently-named files**  
   • Open `internet_connectivity_checker.py`.  
   • Near the top you'll find:
     ```python
     CONNECTED_ICON = os.path.join(SCRIPT_DIR, "icons/gtk-connect.svg")
     DISCONNECTED_ICON = os.path.join(SCRIPT_DIR, "icons/gtk-disconnect.svg")
     ```
   • Change the filenames (and/or paths) to match your own icons.  
   • Save and restart.

**Icon format & size**  
• **SVG** is recommended – it scales perfectly on HiDPI screens.  
• **PNG** also works; 24 × 24 px or 32 × 32 px are typical tray sizes.  
• Ensure the icons have a transparent background so they look good on any panel theme.

## Credits

**Author:** [NeatCode Labs](https://neatcodelabs.com/)

### Inspired by

Work by *Ian Crane* – see his original *Linux System Tray Internet Status* project and the PyGTK notebook example listed inside the *About → Inspired by* section of the app.

Open *About → Inspired by* for technical credits.

## License

This project is released under the **MIT License** – see `LICENSE` file.

---

<div align="center">

### Support NeatCode Labs

Visit us for more useful tools and projects!

[![Website](https://img.shields.io/badge/Website-neatcodelabs.com-blue?style=for-the-badge)](https://neatcodelabs.com)
[![Ko-fi](https://img.shields.io/badge/Ko--fi-Support%20Us-ff5e5b?style=for-the-badge&logo=ko-fi)](https://ko-fi.com/neatcodelabs)

</div>

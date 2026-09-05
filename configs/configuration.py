# Create  setting file locations
BATTERY = "/sys/class/power_supply/BAT0/capacity"
AC = "/sys/class/power_supply/AC0/online"
XDG_RUNTIME = os.environ.get("XDG_RUNTIME_DIR")
HYPR_SIG = os.environ.get("HYPRLAND_INSTANCE_SIGNATURE")
HYPR_SOCK = f"{XDG_RUNTIME}/hypr/{HYPR_SIG}/.socket.sock"

# Config file locations
CONFIG = "/home/justin/.config/DoomBar/"
APP_BUTTON = (f"{CONFIG}theme/gentoo/start.svg")
CC_BUTTON = (f"{CONFIG}theme/gentoo/settings.png")
CSS_STYLE = (f"{CONFIG}theme/gentoo/style.css")
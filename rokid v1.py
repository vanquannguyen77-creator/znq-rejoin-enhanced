import os, requests, json, time, subprocess, aiohttp, threading, psutil, sqlite3, shutil, logging, pytz, traceback, random
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.box import ROUNDED
from rich.console import Console
from threading import Lock, Event
from colorama import Fore, init
from datetime import datetime, timedelta, timezone
from flask import Flask, request, jsonify
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes

try:
    from prettytable import PrettyTable
except ImportError:
    os.system(f"pip install prettytable")
    from prettytable import PrettyTable

init(autoreset=True)

package_lock = Lock()

def log_error(error_message):
    with open("error_log.txt", "a") as error_log:
        error_log.write(f"{error_message}\n\n")

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

ANSI_RESET = "\033[0m"
ANSI_CYAN = "\033[96m"
ANSI_GREEN = "\033[92m"
ANSI_RED = "\033[91m"
ANSI_YELLOW = "\033[93m"
ANSI_BLUE = "\033[94m"

def clear_console():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

if not os.path.exists("Rokid Manager"):
    os.makedirs("Rokid Manager", exist_ok=True)
SERVER_LINKS_FILE = "Rokid Manager/server-link.txt"
ACCOUNTS_FILE = "Rokid Manager/account.txt"
CONFIG_FILE = "Rokid Manager/config-wh.json"

interval = None
stop_webhook_thread = False
webhook_thread = None
webhook_url = None
device_name = None
status_lock = Lock()
rejoin_lock = Lock()

app = Flask(__name__)

package_statuses = {}
boot_time = psutil.boot_time()

globals()["_disable_ui"] = "0"
globals()["package_statuses"] = {}
globals()["_uid_"] = {}
globals()["_user_"] = {}
globals()["is_runner_ez"] = False
globals()["check_exec_enable"] = "1"

executors = {
    "Fluxus": "/storage/emulated/0/Fluxus/",
    "Codex": "/storage/emulated/0/Codex/",
    "Codex Clone 001": "/storage/emulated/0/RobloxClone001/Codex/",
    "Codex Clone 002": "/storage/emulated/0/RobloxClone002/Codex/",
    "Codex Clone 003": "/storage/emulated/0/RobloxClone003/Codex/",
    "Codex Clone 004": "/storage/emulated/0/RobloxClone004/Codex/",
    "Codex Clone 005": "/storage/emulated/0/RobloxClone005/Codex/",
    "Codex Clone 006": "/storage/emulated/0/RobloxClone006/Codex/",
    "Codex Clone 007": "/storage/emulated/0/RobloxClone007/Codex/",
    "Codex Clone 008": "/storage/emulated/0/RobloxClone008/Codex/",
    "Codex Clone 009": "/storage/emulated/0/RobloxClone009/Codex/",
    "Codex Clone 010": "/storage/emulated/0/RobloxClone010/Codex/",
    "Codex Clone 011": "/storage/emulated/0/RobloxClone011/Codex/",
    "Codex Clone 012": "/storage/emulated/0/RobloxClone012/Codex/",
    "Codex Clone 013": "/storage/emulated/0/RobloxClone013/Codex/",
    "Codex Clone 014": "/storage/emulated/0/RobloxClone014/Codex/",
    "Codex Clone 015": "/storage/emulated/0/RobloxClone015/Codex/",
    "Codex Clone 016": "/storage/emulated/0/RobloxClone016/Codex/",
    "Codex Clone 017": "/storage/emulated/0/RobloxClone017/Codex/",
    "Codex Clone 018": "/storage/emulated/0/RobloxClone018/Codex/",
    "Codex Clone 019": "/storage/emulated/0/RobloxClone019/Codex/",
    "Codex Clone 020": "/storage/emulated/0/RobloxClone020/Codex/",
    "Codex VNG Clone 001": "/storage/emulated/0/RobloxVNGClone001/Codex/",
    "Codex VNG Clone 002": "/storage/emulated/0/RobloxVNGClone002/Codex/",
    "Codex VNG Clone 003": "/storage/emulated/0/RobloxVNGClone003/Codex/",
    "Codex VNG Clone 004": "/storage/emulated/0/RobloxVNGClone004/Codex/",
    "Codex VNG Clone 005": "/storage/emulated/0/RobloxVNGClone005/Codex/",
    "Codex VNG Clone 006": "/storage/emulated/0/RobloxVNGClone006/Codex/",
    "Codex VNG Clone 007": "/storage/emulated/0/RobloxVNGClone007/Codex/",
    "Codex VNG Clone 008": "/storage/emulated/0/RobloxVNGClone008/Codex/",
    "Codex VNG Clone 009": "/storage/emulated/0/RobloxVNGClone009/Codex/",
    "Codex VNG Clone 010": "/storage/emulated/0/RobloxVNGClone010/Codex/",
    "Codex VNG Clone 011": "/storage/emulated/0/RobloxVNGClone011/Codex/",
    "Codex VNG Clone 012": "/storage/emulated/0/RobloxVNGClone012/Codex/",
    "Codex VNG Clone 013": "/storage/emulated/0/RobloxVNGClone013/Codex/",
    "Codex VNG Clone 014": "/storage/emulated/0/RobloxVNGClone014/Codex/",
    "Codex VNG Clone 015": "/storage/emulated/0/RobloxVNGClone015/Codex/",
    "Codex VNG Clone 016": "/storage/emulated/0/RobloxVNGClone016/Codex/",
    "Codex VNG Clone 017": "/storage/emulated/0/RobloxVNGClone017/Codex/",
    "Codex VNG Clone 018": "/storage/emulated/0/RobloxVNGClone018/Codex/",
    "Codex VNG Clone 019": "/storage/emulated/0/RobloxVNGClone019/Codex/",
    "Codex VNG Clone 020": "/storage/emulated/0/RobloxVNGClone020/Codex/",
    "Arceus X": "/storage/emulated/0/Arceus X/",
    "Arceus X Clone 001": "/storage/emulated/0/RobloxClone001/Arceus X/",
    "Arceus X Clone 002": "/storage/emulated/0/RobloxClone002/Arceus X/",
    "Arceus X Clone 003": "/storage/emulated/0/RobloxClone003/Arceus X/",
    "Arceus X Clone 004": "/storage/emulated/0/RobloxClone004/Arceus X/",
    "Arceus X Clone 005": "/storage/emulated/0/RobloxClone005/Arceus X/",
    "Arceus X Clone 006": "/storage/emulated/0/RobloxClone006/Arceus X/",
    "Arceus X Clone 007": "/storage/emulated/0/RobloxClone007/Arceus X/",
    "Arceus X Clone 008": "/storage/emulated/0/RobloxClone008/Arceus X/",
    "Arceus X Clone 009": "/storage/emulated/0/RobloxClone009/Arceus X/",
    "Arceus X Clone 010": "/storage/emulated/0/RobloxClone010/Arceus X/",
    "Arceus X Clone 011": "/storage/emulated/0/RobloxClone011/Arceus X/",
    "Arceus X Clone 012": "/storage/emulated/0/RobloxClone012/Arceus X/",
    "Arceus X Clone 013": "/storage/emulated/0/RobloxClone013/Arceus X/",
    "Arceus X Clone 014": "/storage/emulated/0/RobloxClone014/Arceus X/",
    "Arceus X Clone 015": "/storage/emulated/0/RobloxClone015/Arceus X/",
    "Arceus X Clone 016": "/storage/emulated/0/RobloxClone016/Arceus X/",
    "Arceus X Clone 017": "/storage/emulated/0/RobloxClone017/Arceus X/",
    "Arceus X Clone Gabriela18": "/storage/emulated/0/RobloxClone018/Arceus X/",
    "Arceus X Clone 019": "/storage/emulated/0/RobloxClone019/Arceus X/",
    "Arceus X Clone 020": "/storage/emulated/0/RobloxClone020/Arceus X/",
    "Arceus X VNG Clone 001": "/storage/emulated/0/RobloxVNGClone001/Arceus X/",
    "Arceus X VNG Clone 002": "/storage/emulated/0/RobloxVNGClone002/Arceus X/",
    "Arceus X VNG Clone 003": "/storage/emulated/0/RobloxVNGClone003/Arceus X/",
    "Arceus X VNG Clone 004": "/storage/emulated/0/RobloxVNGClone004/Arceus X/",
    "Arceus X VNG Clone 005": "/storage/emulated/0/RobloxVNGClone005/Arceus X/",
    "Arceus X VNG Clone 006": "/storage/emulated/0/RobloxVNGClone006/Arceus X/",
    "Arceus X VNG Clone 007": "/storage/emulated/0/RobloxVNGClone007/Arceus X/",
    "Arceus X VNG Clone 008": "/storage/emulated/0/RobloxVNGClone008/Arceus X/",
    "Arceus X VNG Clone 009": "/storage/emulated/0/RobloxVNGClone009/Arceus X/",
    "Arceus X VNG Clone 010": "/storage/emulated/0/RobloxVNGClone010/Arceus X/",
    "Arceus X VNG Clone 011": "/storage/emulated/0/RobloxVNGClone011/Arceus X/",
    "Arceus X VNG Clone 012": "/storage/emulated/0/RobloxVNGClone012/Arceus X/",
    "Arceus X VNG Clone 013": "/storage/emulated/0/RobloxVNGClone013/Arceus X/",
    "Arceus X VNG Clone 014": "/storage/emulated/0/RobloxVNGClone014/Arceus X/",
    "Arceus X VNG Clone 015": "/storage/emulated/0/RobloxVNGClone015/Arceus X/",
    "Arceus X VNG Clone 016": "/storage/emulated/0/RobloxVNGClone016/Arceus X/",
    "Arceus X VNG Clone 017": "/storage/emulated/0/RobloxVNGClone017/Arceus X/",
    "Arceus X VNG Clone 018": "/storage/emulated/0/RobloxVNGClone018/Arceus X/",
    "Arceus X VNG Clone 019": "/storage/emulated/0/RobloxVNGClone019/Arceus X/",
    "Arceus X VNG Clone 020": "/storage/emulated/0/RobloxVNGClone020/Arceus X/",
    "Delta": "/storage/emulated/0/Delta/",
    "Cryptic": "/storage/emulated/0/Cryptic/",
    "KRNL": "/storage/emulated/0/krnl/",
    "Trigon": "/storage/emulated/0/Trigon/",
    "Cubix": "/storage/emulated/0/Cubix/"
}

workspace_paths = []
for executor, base_path in executors.items():
    workspace_paths.append(f"{base_path}Workspace")
    workspace_paths.append(f"{base_path}workspace")

globals()["workspace_paths"] = workspace_paths
globals()["executors"] = executors

version = "True V2.2"

def print_header(version):
    console = Console()
    header = Text(r"""
  ____       _    _     _   __  __                                   
 |  _ \ ___ | | _(_) __| | |  \/  | __ _ _ __   __ _  __ _  ___ _ __ 
 | |_) / _ \| |/ / |/ _` | | |\/| |/ _` | '_ \ / _` |/ _` |/ _ \ '__| 
 |  _ < (_) |   <| | (_| | | |  | | (_| | | | | (_| | (_| |  __/ |   
 |_| \_\___/|_|\_\_|\__,_| |_|  |_|\__,_|_| |_|\__,_|\__, |\___|_|   
                                                     |___/                            
    """, style="bold yellow")

    config_file = os.path.join("Rokid Manager", "config-wh.json")
    check_executor = "1"

    if os.path.exists(config_file):
        try:
            with open(config_file, "r") as f:
                config = json.load(f)
                check_executor = config.get("check_executor", "0")
        except Exception as e:
            console.print(f"[bold red][ Rokid Manager ] - Error reading {config_file}: {e}[/bold red]")

    console.print(header)
    console.print(f"[bold yellow]- Version: [/bold yellow][bold white]{version}[/bold white]")
    console.print("[bold yellow]- Credit: [/bold yellow][bold white]Rokid Manager[/bold white]")

    if check_executor == "1":
        console.print("[bold yellow]- Method: [/bold yellow][bold white]Check Executor[/bold white]\n")
    else:
        console.print("[bold yellow]- Method: [/bold yellow][bold white]Check Online[/bold white]\n")

def get_cookie():
    try:
        current_dir = os.getcwd()
        cookie_txt_path = os.path.join(current_dir, "cookie.txt")
        new_dir_path = os.path.join(current_dir, "Rokid Manager/RokidManager - Cookie Data")
        new_cookie_path = os.path.join(new_dir_path, "cookie.txt")

        if not os.path.exists(new_dir_path):
            os.makedirs(new_dir_path)

        if not os.path.exists(cookie_txt_path):
            print("\033[1;31m[ Rokid Manager ] - cookie.txt not found in the current directory!\033[0m")
            log_error("cookie.txt not found in the current directory.")
            return False

        cookies = []
        org = []

        with open(cookie_txt_path, "r") as file:
            for line in file.readlines():
                parts = str(line).strip().split(":")
                if len(parts) == 4:
                    ck = ":".join(parts[2:])
                else:
                    ck = str(line).strip()
                if ck.startswith("_|WARNING:"):
                    org.append(str(line).strip())
                    cookies.append(ck)

        if len(cookies) == 0:
            print("\033[1;31m[ Rokid Manager ] - No valid cookies found in cookie.txt. Please add cookies.\033[0m")
            log_error("No valid cookies found in cookie.txt.")
            return False

        cookie = cookies.pop(0)
        original_line = org.pop(0)

        with open(new_cookie_path, "a") as new_file:
            new_file.write(original_line + "\n")

        with open(cookie_txt_path, "w") as file:
            file.write("\n".join(org))

        return cookie

    except Exception as e:
        print(f"\033[1;31m[ Rokid Manager ] - Error: {e}\033[0m")
        log_error(f"Error in get_cookie: {e}")
        return False

def capture_screenshot():
    screenshot_path = "/storage/emulated/0/Download/screenshot.png"
    try:
        os.system(f"/system/bin/screencap -p {screenshot_path}")
        if not os.path.exists(screenshot_path):
            raise FileNotFoundError("Screenshot file was not created.")
        return screenshot_path
    except Exception as e:
        print(f"\033[1;31m[ Rokid Manager ] - Error capturing screenshot: {e}\033[0m")
        log_error(f"Error capturing screenshot: {e}")
        return None

def get_uptime():
    current_time = time.time()
    uptime_seconds = current_time - boot_time
    days = int(uptime_seconds // (24 * 3600))
    hours = int((uptime_seconds % (24 * 3600)) // 3600)
    minutes = int((uptime_seconds % 3600) // 60)
    seconds = int(uptime_seconds % 60)
    return f"{days}d {hours}h {minutes}m {seconds}s"

def roblox_processes():
    roblox_package_names = get_roblox_packages()
    processes = []

    for proc in psutil.process_iter(['name', 'pid', 'memory_info']):
        try:
            proc_name = proc.info['name'].lower()
            if proc_name in roblox_package_names:
                mem_usage = round(proc.info['memory_info'].rss / (1024 ** 2), 2)
                full_name = proc.info['name']
                if '.' not in full_name:
                    full_name = f"com.{full_name}"
                processes.append(f"{full_name} (PID: {proc.pid}, Mem: {mem_usage}MB)")
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return processes

def get_system_info():
    try:
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_info = psutil.virtual_memory()
        system_info = {
            "cpu_usage": cpu_usage,
            "memory_total": round(memory_info.total / (1024 ** 3), 2),
            "memory_used": round(memory_info.used / (1024 ** 3), 2),
            "memory_percent": memory_info.percent,
            "uptime": get_uptime(),
            "roblox_packages": roblox_processes(),
        }
        return system_info
    except Exception as e:
        print(f"\033[1;31m[ Rokid Manager ] - Error retrieving system information: {e}\033[0m")
        log_error(f"Error retrieving system information: {e}")
        return False

def _load_config():
    global webhook_url, device_name, interval
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as file:
                config = json.load(file)
                webhook_url = config.get("webhook_url", None)
                device_name = config.get("device_name", None)
                interval = config.get("interval", None)
                globals()["_disable_ui"] = config.get("disable_ui", "0")
                globals()["check_exec_enable"] = config.get("check_executor", "1")
        else:
            webhook_url, device_name, interval = None, None, None
            globals()["_disable_ui"] = "0"
            globals()["check_exec_enable"] = "1"
    except Exception as e:
        print(f"\033[1;31m[ Rokid Manager ] - Error loading configuration: {e}\033[0m")
        log_error(f"Error loading configuration: {e}")

def save_config():
    try:
        config = {
            "webhook_url": webhook_url,
            "device_name": device_name,
            "interval": interval,
            "disable_ui": globals().get("_disable_ui", "0"),
            "check_executor": globals()["check_exec_enable"]
        }
        with open(CONFIG_FILE, "w") as file:
            json.dump(config, file)
    except Exception as e:
        print(f"\033[1;31m[ Rokid Manager ] - Error saving configuration: {e}\033[0m")
        log_error(f"Error saving configuration: {e}")

def start_webhook_thread():
    global webhook_thread, stop_webhook_thread
    if (webhook_thread is None or not webhook_thread.is_alive()) and not stop_webhook_thread:
        stop_webhook_thread = False
        webhook_thread = threading.Thread(target=send_webhook)
        webhook_thread.start()

def send_webhook():
    global stop_webhook_thread
    while not stop_webhook_thread:
        try:
            screenshot_path = capture_screenshot()
            if not screenshot_path:
                continue

            info = get_system_info()
            if not info:
                continue

            cpu = f"{info['cpu_usage']:.1f}%"
            mem_used = f"{info['memory_used']:.2f} GB"
            mem_total = f"{info['memory_total']:.2f} GB"
            mem_percent = f"{info['memory_percent']:.1f}%"
            uptime = info['uptime']
            roblox_count = len(info['roblox_packages'])
            roblox_status = f"Running: {roblox_count} instance{'s' if roblox_count != 1 else ''}"
            roblox_details = "\n".join(info['roblox_packages']) if info['roblox_packages'] else "None"

            if roblox_count > 0:
                status_text = f"🟢 Online"
            else:
                status_text = "🔴 Offline"

            random_color = random.randint(0, 16777215)

            embed = {
                "color": random_color,
                "title": "📈 System Status Monitor",
                "description": f"Real-time report for **{device_name}**",
                "fields": [
                    {"name": "🏷️ Device", "value": f"```{device_name}```", "inline": True},
                    {"name": "💾 Total Memory", "value": f"```{mem_total}```", "inline": True},
                    {"name": "⏰ Uptime", "value": f"```{uptime}```", "inline": True},
                    {"name": "⚡ CPU Usage", "value": f"```{cpu}```", "inline": True},
                    {"name": "📊 Memory Usage", "value": f"```{mem_used} ({mem_percent})```", "inline": True},
                    {"name": "🎮 Roblox Status", "value": f"```{roblox_status}```", "inline": True},
                    {"name": "🔍 Roblox Details", "value": f"```{roblox_details}```", "inline": False},
                    {"name": "✅ Status", "value": f"```{status_text}```", "inline": True}
                ],
                "thumbnail": {"url": "https://i.imgur.com/5yXNxU4.png"},
                "image": {"url": "attachment://screenshot.png"},
                "footer": {"text": f"Rokid Manager • Last Update: {time.strftime('%Y-%m-%d %H:%M:%S UTC')}", 
                           "icon_url": "https://i.imgur.com/5yXNxU4.png"},
                "author": {"name": "Rokid Manager", 
                           "url": "https://discord.gg/rokidmanager", 
                           "icon_url": "https://i.imgur.com/5yXNxU4.png"}
            }

            with open(screenshot_path, "rb") as file:
                response = requests.post(
                    webhook_url,
                    data={"payload_json": json.dumps({"embeds": [embed], "username": device_name})},
                    files={"file": ("screenshot.png", file)}
                )

            if response.status_code not in (200, 204):
                print(f"\033[1;31m[ Rokid Manager ] - Error sending device info: {response.status_code}\033[0m")
                log_error(f"Error sending webhook: Status code {response.status_code}")

        except Exception as e:
            print(f"\033[1;31m[ Rokid Manager ] - Webhook error: {e}\033[0m")
            log_error(f"Error in webhook thread: {e}")

        time.sleep(interval * 60)

def stop_webhook():
    global stop_webhook_thread
    stop_webhook_thread = True

def setup_webhook():
    global webhook_url, device_name, interval, stop_webhook_thread
    try:
        stop_webhook_thread = True
        webhook_url = input("\033[1;35m[ Rokid Manager ] - Enter your Webhook URL: \033[0m")
        device_name = input("\033[1;35m[ Rokid Manager ] - Enter your device name: \033[0m")
        interval = int(input("\033[1;35m[ Rokid Manager ] - Enter the interval to send Webhook (minutes): \033[0m"))
        save_config()
        stop_webhook_thread = False
        threading.Thread(target=send_webhook).start()
    except Exception as e:
        print(f"\033[1;31m[ Rokid Manager ] - Error during webhook setup: {e}\033[0m")
        log_error(f"Error during webhook setup: {e}")

def create_dynamic_menu(options):
    console = Console()

    table = Table(
        header_style="bold white", 
        border_style="bright_white", 
        box=ROUNDED
    )
    table.add_column("No", justify="center", style="bold cyan", width=6)
    table.add_column("Service Name", style="bold magenta", justify="left")

    for i, service in enumerate(options, start=1):
        table.add_row(f"[bold yellow][ {i} ][/bold yellow]", f"[bold blue]{service}[/bold blue]")

    panel = Panel(
        table,
        title="[bold yellow]discord.gg/rokidmanager - Premium Edition[/bold yellow]",
        border_style="yellow",
        box=ROUNDED
    )

    console.print(Align.left(panel))

def create_dynamic_table(headers, rows):
    table = PrettyTable(field_names=headers, border=True, align="l")
    for huy in rows:
        table.add_row(list(huy))
    print(table)

def update_status_table():
    table_packages = PrettyTable(field_names=["Package", "Username", "Package Status"], border=True, align="l")

    for package, info in globals().get("package_statuses", {}).items():
        username = str(info.get("Username", "Unknown"))

        if username != "Unknown":
            obfuscated_username = "******" + username[6:] if len(username) > 6 else "******"
            username = obfuscated_username

        table_packages.add_row([
            str(package),
            username,
            str(info.get("Status", "Unknown"))
        ])

    clear_screen()
    print_header(version)
    print(table_packages)

def check_user_online(user_id, cookie=None):
    max_retries = 2
    delay = 2
    body = {"userIds": [user_id]}
    headers = {"Content-Type": "application/json"}
    if cookie is not None:
        headers["Cookie"] = f".ROBLOSECURITY={cookie}"
    for attempt in range(max_retries):
        try:
            with requests.Session() as session:
                primary_response = session.post("https://presence.roblox.com/v1/presence/users", headers=headers, json=body, timeout=7)
            primary_response.raise_for_status()
            primary_data = primary_response.json()
            primary_presence_type = primary_data["userPresences"][0]["userPresenceType"]
            return primary_presence_type

        except requests.exceptions.RequestException as e:
            print(f"\033[1;31mError checking online status for user {user_id} (Attempt {attempt + 1}) for Roblox API: {e}\033[0m")
            if attempt < max_retries - 1:
                time.sleep(delay)
                delay *= 2

    headers = {"Content-Type": "application/json"}
    for attempt in range(max_retries):
        try:
            with requests.Session() as session:
                primary_response = session.post("https://presence.roproxy.com/v1/presence/users", headers=headers, json=body, timeout=7)
            primary_response.raise_for_status()
            primary_data = primary_response.json()
            primary_presence_type = primary_data["userPresences"][0]["userPresenceType"]
            return primary_presence_type

        except requests.exceptions.RequestException as e:
            print(f"\033[1;31mError checking online status for user {user_id} (Attempt {attempt + 1}) for RoProxy API: {e}\033[0m")
            if attempt < max_retries - 1:
                time.sleep(delay)
                delay *= 2
            else:
                return None

def verify_cookie(cookie_value):
    try:
        headers = {
            'Cookie': f'.ROBLOSECURITY={cookie_value}',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; Mobile) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Mobile Safari/537.36',
            'Referer': 'https://www.roblox.com/',
            'Origin': 'https://www.roblox.com',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        }

        time.sleep(1)

        response = requests.get('https://users.roblox.com/v1/users/authenticated', headers=headers)

        if response.status_code == 200:
            print("\033[1;32m[ Rokid Manager ] - Cookie is valid! User is authenticated.\033[0m")
            return response.json().get("id", False)
        elif response.status_code == 401:
            print("\033[1;31m[ Rokid Manager ] - Invalid cookie. The user is not authenticated.\033[0m")
            return False
        else:
            error_message = f"Error verifying cookie: {response.status_code} - {response.text}"
            print(f"\033[1;31m[ Rokid Manager ] - {error_message}\033[0m")
            log_error(error_message)
            return False

    except requests.RequestException as e:
        error_message = f"Request exception occurred while verifying cookie: {e}"
        print(f"\033[1;31m[ Rokid Manager ] - {error_message}\033[0m")
        log_error(error_message)
        return False

    except Exception as e:
        error_message = f"Unexpected exception occurred while verifying cookie: {e}"
        print(f"\033[1;31m[ Rokid Manager ] - {error_message}\033[0m")
        log_error(error_message)
        return False

def download_file(url, destination, binary=False):
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            mode = 'wb' if binary else 'w'
            with open(destination, mode) as file:
                if binary:
                    shutil.copyfileobj(response.raw, file)
                else:
                    file.write(response.text)
            print(f"\033[1;32m[ Rokid Manager ] - {os.path.basename(destination)} downloaded successfully.\033[0m")
            return destination
        else:
            error_message = f"Failed to download {os.path.basename(destination)}. Status code: {response.status_code}"
            print(f"\033[1;31m[ Rokid Manager ] - {error_message}\033[0m")
            log_error(error_message)
            return None
    except requests.RequestException as e:
        error_message = f"Request exception while downloading {os.path.basename(destination)}: {e}"
        print(f"\033[1;31m[ Rokid Manager ] - {error_message}\033[0m")
        log_error(error_message)
        return None
    except Exception as e:
        error_message = f"Unexpected error while downloading {os.path.basename(destination)}: {e}"
        print(f"\033[1;31m[ Rokid Manager ] - {error_message}\033[0m")
        log_error(error_message)
        return None

def replace_cookie_value_in_db(db_path, new_cookie_value):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE cookies SET value = ?, last_access_utc = ?, expires_utc = ? WHERE host_key = '.roblox.com' AND name = '.ROBLOSECURITY'", (new_cookie_value, int(time.time()+11644473600)*1000000, int(time.time()+11644473600+31536000)*1000000))
        conn.commit()
        conn.close()
        print("\033[1;32mCookie value replaced successfully in the database!\033[0m")
    except sqlite3.OperationalError as e:
        print(f"\033[1;31mDatabase error during cookie replacement: {e}\033[0m")
    except Exception as e:
        print(f"\033[1;31mError replacing cookie value in database: {e}\033[0m")

def inject_cookies_and_appstorage():
    kill_roblox_processes()
    db_url = "https://raw.githubusercontent.com/Wraith1vs11/Extension/refs/heads/main/Cookies.db"
    appstorage_url = "https://raw.githubusercontent.com/Wraith1vs11/Extension/refs/heads/main/appStorage.json"

    downloaded_db_path = download_file(db_url, "Cookies.db", binary=True)
    downloaded_appstorage_path = download_file(appstorage_url, "appStorage.json", binary=False)

    if not downloaded_db_path or not downloaded_appstorage_path:
        print("\033[1;31m[ Rokid Manager ] - Failed to download necessary files. Exiting.\033[0m")
        log_error("Failed to download necessary files for cookie and appStorage injection.")
        return

    packages = get_roblox_packages()
    for package_name in packages:
        try:
            cookie = get_cookie()
            if not cookie:
                print(f"\033[1;31m[ Rokid Manager ] - Failed to retrieve a cookie for {package_name}. Skipping...\033[0m")
                break
            
            if verify_cookie(cookie):
                print(f"\033[1;32m[ Rokid Manager ] - Cookie for {package_name} is valid!\033[0m")
            else:
                print(f"\033[1;31m[ Rokid Manager ] - Cookie for {package_name} is invalid. Skipping injection...\033[0m")
                continue
                
            print(f"\033[1;32m[ Rokid Manager ] - Injecting cookie for {package_name}: {cookie}\033[0m")
            
            destination_db_dir = f"/data/data/{package_name}/app_webview/Default/"
            destination_appstorage_dir = f"/data/data/{package_name}/files/appData/LocalStorage/"
            os.makedirs(destination_db_dir, exist_ok=True)
            os.makedirs(destination_appstorage_dir, exist_ok=True)
            
            destination_db_path = os.path.join(destination_db_dir, "Cookies")
            shutil.copyfile(downloaded_db_path, destination_db_path)
            print(f"\033[1;32m[ Rokid Manager ] - Copied Cookies.db to {destination_db_path}\033[0m")
            
            destination_appstorage_path = os.path.join(destination_appstorage_dir, "appStorage.json")
            shutil.copyfile(downloaded_appstorage_path, destination_appstorage_path)
            print(f"\033[1;32m[ Rokid Manager ] - Copied appStorage.json to {destination_appstorage_path}\033[0m")
            
            replace_cookie_value_in_db(destination_db_path, cookie)
            
            subprocess.run(["/system/bin/am", "start", "--activity-brought-to-front", 
                          "--windowingMode", "5", "-n", 
                          f"{package_name}/com.roblox.client.startup.ActivitySplash"], 
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(5)

        except Exception as e:
            error_message = f"Error injecting cookie for {package_name}: {e}"
            print(f"\033[1;31m[ Rokid Manager ] - {error_message}\033[0m")
            log_error(error_message)
    
    print("\033[1;32m[ Rokid Manager ] - Cookie and appStorage injection completed for all packages.\033[0m")

def get_roblox_packages():
    package_file = "package.json"

    if not os.path.exists(package_file):
        with open(package_file, "w") as f:
            f.write("com.roblox")
        package_prefix = "com.roblox"
    else:
        with open(package_file, "r") as f:
            package_prefix = f.read().strip()

    packages = []
    try:
        result = subprocess.run(
            f"pm list packages {package_prefix} | sed 's/package://'",
            shell=True,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            for line in result.stdout.strip().splitlines():
                name = line.strip()
                if package_prefix in name:
                    packages.append(name)
        else:
            print("\033[1;31m[ Rokid Manager ] - Failed to retrieve packages.\033[0m")
            log_error(f"Failed to retrieve packages. Return code: {result.returncode}")
    except Exception as e:
        print(f"\033[1;31m[ Rokid Manager ] - Error retrieving packages: {e}\033[0m")
        log_error(f"Error retrieving packages: {e}")
    return packages

def delete_cache_for_package(package_name):
    cache_path = f'/data/data/{package_name}/cache/'

    if os.path.exists(cache_path):
        try:
            shutil.rmtree(cache_path)
            print(f"\033[1;96m[ Rokid Manager ] - Cache cleared for package:\033[0m {package_name}")
        except Exception as e:
            print(f"\033[1;31m[ Rokid Manager ] - Error while deleting cache for package {package_name}: {e}\033[0m")
            log_error(f"Error while deleting cache for package {package_name}: {e}")
    else:
        print(f"\033[1;93m[ Rokid Manager ] - Cache folder not found for package {package_name}\033[0m")

def kill_roblox_processes():
    print("\033[1;96m[ Rokid Manager ] - Killing all Roblox processes...\033[0m")
    try:
        package_names = get_roblox_packages()
        for package_name in package_names:
            print(f"\033[1;96m[ Rokid Manager ] - Trying to kill process for package:\033[0m {package_name}")
            delete_cache_for_package(package_name)
            os.system(f"nohup /system/bin/am force-stop {package_name} > /dev/null 2>&1 &")
        time.sleep(2)
    except Exception as e:
        print(f"\033[1;31m[ Rokid Manager ] - Error killing Roblox processes: {e}\033[0m")
        log_error(f"Error killing Roblox processes: {e}")

def kill_roblox_process(package_name):
    print(f"\033[1;96m[ Rokid Manager ] - Killing Roblox process for {package_name}...\033[0m")
    try:
        subprocess.run(
            ["/system/bin/am", "force-stop", package_name],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"\033[1;32m[ Rokid Manager ] - Killed process for {package_name}\033[0m")
        time.sleep(2)
    except subprocess.CalledProcessError as e:
        print(f"\033[1;31m[ Rokid Manager ] - Error killing process for {package_name}: {e}\033[0m")
        log_error(f"Error killing process for {package_name}: {e}")

def launch_roblox(package_name, server_link):
    try:
        kill_roblox_process(package_name)
        time.sleep(2)

        with status_lock:
            globals()["_uid_"][globals()["_user_"][package_name]] = time.time()
            globals()["package_statuses"][package_name]["Status"] = f"\033[1;36mOpening Roblox for {package_name}...\033[0m"
            update_status_table()

        subprocess.run([
            'am', 'start',
            '-a', 'android.intent.action.MAIN',
            '-n', f'{package_name}/com.roblox.client.startup.ActivitySplash'
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        time.sleep(10)

        with status_lock:
            globals()["package_statuses"][package_name]["Status"] = f"\033[1;36mJoining Roblox for {package_name}...\033[0m"
            update_status_table()

        subprocess.run([
            'am', 'start',
            '-a', 'android.intent.action.VIEW',
            '-n', f'{package_name}/com.roblox.client.ActivityProtocolLaunch',
            '-d', server_link
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        time.sleep(20)
        with status_lock:
            globals()["package_statuses"][package_name]["Status"] = "\033[1;32mJoined Roblox\033[0m"
            update_status_table()

    except Exception as e:
        error_message = f"Error launching Roblox for {package_name}: {e}"
        with status_lock:
            globals()["package_statuses"][package_name]["Status"] = f"\033[1;31m{error_message}\033[0m"
            update_status_table()
        print(f"\033[1;31m[ Rokid Manager ] - {error_message}\033[0m")
        log_error(error_message)

def format_server_link(input_link):
    if 'roblox.com' in input_link:
        return input_link
    elif input_link.isdigit():
        return f'roblox://placeID={input_link}'
    else:
        print("\033[1;31m[ Rokid Manager ] - Invalid input! Please enter a valid game ID or private server link.\033[0m")
        return None

def save_server_links(server_links):
    try:
        os.makedirs(os.path.dirname(SERVER_LINKS_FILE), exist_ok=True)
        with open(SERVER_LINKS_FILE, "w") as file:
            for package, link in server_links:
                file.write(f"{package},{link}\n")
        print("\033[1;32m[ Rokid Manager ] - Server links saved successfully.\033[0m")
    except IOError as e:
        print(f"\033[1;31m[ Rokid Manager ] - Error saving server links: {e}\033[0m")
        log_error(f"Error saving server links: {e}")

def load_server_links():
    server_links = []
    if os.path.exists(SERVER_LINKS_FILE):
        with open(SERVER_LINKS_FILE, "r") as file:
            for line in file:
                package, link = line.strip().split(",", 1)
                server_links.append((package, link))
    return server_links

def save_accounts(accounts):
    with open(ACCOUNTS_FILE, "w") as file:
        for package, user_id in accounts:
            file.write(f"{package},{user_id}\n")

def load_accounts():
    accounts = []
    if os.path.exists(ACCOUNTS_FILE):
        with open(ACCOUNTS_FILE, "r") as file:
            for line in file:
                line = line.strip()
                if line:
                    try:
                        package, user_id = line.split(",", 1)
                        globals()["_user_"][package] = user_id
                        accounts.append((package, user_id))
                    except ValueError:
                        print(f"\033[1;31m[ Rokid Manager ] - Invalid line format: {line}. Expected format 'package,user_id'.\033[0m")
    return accounts

def find_userid_from_file(file_path):
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            userid_start = content.find('"UserId":"')
            if userid_start == -1:
                print("\033[1;31m[ Rokid Manager ] - Userid not found\033[0m")
                return None

            userid_start += len('"UserId":"')
            userid_end = content.find('"', userid_start)
            if userid_end == -1:
                print("\033[1;31m[ Rokid Manager ] - Userid end quote not found\033[0m")
                return None

            userid = content[userid_start:userid_end]
            return userid

    except IOError as e:
        print(f"\033[1;31m[ Rokid Manager ] - Error reading file: {e}\033[0m")
        return None

def get_username(user_id):
    user = load_saved_username(user_id)
    if user is not None:
        return user
    retry_attempts = 2
    for attempt in range(retry_attempts):
        try:
            url = f"https://users.roblox.com/v1/users/{user_id}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            username = data.get("name", "Unknown")
            if username != "Unknown":
                save_username(user_id, username)
                return username
        except requests.exceptions.RequestException as e:
            print(f"\033[1;31m[ Rokid Manager ] - Attempt {attempt + 1} failed for Roblox Users API: {e}\033[0m")
            time.sleep(2 ** attempt)

    for attempt in range(retry_attempts):
        try:
            url = f"https://users.roproxy.com/v1/users/{user_id}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            username = data.get("name", "Unknown")
            if username != "Unknown":
                save_username(user_id, username)
                return username
        except requests.exceptions.RequestException as e:
            print(f"\033[1;31m[ Rokid Manager ] - Attempt {attempt + 1} failed for RoProxy API: {e}\033[0m")
            time.sleep(2 ** attempt)

    return "Unknown"

def save_username(user_id, username):
    try:
        if not os.path.exists("usernames.json"):
            with open("usernames.json", "w") as file:
                json.dump({user_id: username}, file)
        else:
            with open("usernames.json", "r+") as file:
                try:
                    data = json.load(file)
                except json.JSONDecodeError:
                    data = {}
                data[user_id] = username
                file.seek(0)
                json.dump(data, file)
                file.truncate()
    except (IOError, json.JSONDecodeError) as e:
        print(f"\033[1;31m[ Rokid Manager ] - Error saving username: {e}\033[0m")

def load_saved_username(user_id):
    try:
        with open("usernames.json", "r") as file:
            data = json.load(file)
            return data.get(user_id, None)
    except (FileNotFoundError, json.JSONDecodeError, IOError) as e:
        print(f"\033[1;31m[ Rokid Manager ] - Error loading username: {e}\033[0m")
        return None

def select_check_user():
    while True:
        ask = str(input(f"""\033[1;32mChoose your check online method:\033[0m
\033[1;35m[1]\033[1;36m Check Executor(Recommend)\033[0m
\033[1;35m[2]\033[1;36m Check Online(Not Recommend)\033[0m
\033[1;32mEnter your choice (1-2): \033[0m"""))
        if ask == "1":
            globals()["check_exec_enable"] = "1"
            break
        elif ask == "2":
            globals()["check_exec_enable"] = "0"
            break
        else:
            continue
    save_config()

def xuat(file):
    try:
        con = sqlite3.connect(file)
        cur = con.cursor()
        cur.execute("SELECT value FROM cookies WHERE name='.ROBLOSECURITY'")
        cookie = cur.fetchone()
        con.close()
        if cookie:
            return cookie[0]
        else:
            return None
    except:
        return None

def toggle_check_ui():
    global lua_script_template
    while True:
        print("\033[1;35m[1]\033[1;32m Rokid Check\033[0m\n\033[1;35m[2]\033[1;33m Banana Check\033[0m")
        choice = input("\033[1;32m[ Rokid Manager ] - Select (1-2): \033[0m")
        
        if choice == "1":
            while True:
                print("\033[1;35m[1]\033[1;32m On\033[0m\n\033[1;35m[2]\033[1;31m Off\033[0m")
                sub_choice = input("\033[1;32m[ Rokid Manager ] - Enable UI? (1-2): \033[0m")
                if sub_choice in ("1", "2"):
                    globals()["_disable_ui"] = "0" if sub_choice == "1" else "1"
                    lua_script_template = f'getgenv().disable_ui = {"false" if sub_choice == "1" else "true"}\nloadstring(game:HttpGet("https://raw.githubusercontent.com/RokidManager/neyoshiiuem/refs/heads/main/Rokid-CheckUI.lua"))()'
                    print(f"\033[1;{'32' if sub_choice == '1' else '31'}m[ Rokid Manager ] - Rokid Check UI is now {'enabled' if sub_choice == '1' else 'disabled'}.\033[0m")
                    break
                print("\033[1;31m[ Rokid Manager ] - Invalid choice.\033[0m")
            break
        elif choice == "2":
            lua_script_template = 'loadstring(game:HttpGet("https://raw.githubusercontent.com/obiiyeuem/vthangsitink/refs/heads/main/checkonline.lua"))()'
            print("\033[1;33m[ Rokid Manager ] - Banana Check selected.\033[0m")
            break
        print("\033[1;31m[ Rokid Manager ] - Invalid choice.\033[0m")

    detect_and_write_lua_script()
    print("\033[1;36m[ Rokid Manager ] - Lua scripts updated.\033[0m")

    config_file = os.path.join("Rokid Manager", "checkui.lua")
    try:
        with open(config_file, "w") as f:
            f.write(lua_script_template)
        print(f"\033[1;36m[ Rokid Manager ] - Config saved to {config_file}\033[0m")
    except Exception as e:
        print(f"\033[1;31m[ Rokid Manager ] - Error saving config: {e}\033[0m")

def detect_executors():
    console = Console()
    detected_executors = []

    for executor_name, base_path in executors.items():
        possible_autoexec_paths = [
            os.path.join(base_path, "Autoexec"),
            os.path.join(base_path, "Autoexecute"),
            os.path.join(base_path, "autoexec")
        ]

        for path in possible_autoexec_paths:
            if os.path.exists(path):
                detected_executors.append(executor_name)
                console.print(f"[bold green][ Rokid Manager ] - Detected executor: {executor_name}[/bold green]")
                break

    return detected_executors

def write_lua_script(detected_executors):
    console = Console()
    config_file = os.path.join("Rokid Manager", "checkui.lua")

    try:
        with open(config_file, "r") as f:
            lua_script_content = f.read()
    except Exception as e:
        console.print(f"[bold red][ Rokid Manager ] - Error reading config from {config_file}: {e}[/bold red]")
        return

    for executor_name in detected_executors:
        base_path = executors[executor_name]
        possible_autoexec_paths = [
            os.path.join(base_path, "Autoexec"),
            os.path.join(base_path, "Autoexecute"),
            os.path.join(base_path, "autoexec")
        ]

        lua_written = False

        for path in possible_autoexec_paths:
            if os.path.exists(path):
                lua_script_path = os.path.join(path, "executor_check.lua")
                
                try:
                    with open(lua_script_path, 'w') as file:
                        file.write(lua_script_content)
                    lua_written = True
                    console.print(f"[bold green][ Rokid Manager ] - Lua script written to: {lua_script_path}[/bold green]")
                    break

                except Exception as e:
                    console.print(f"[bold red][ Rokid Manager ] - Error writing Lua script to {lua_script_path}: {e}[/bold red]")
                    log_error(f"Error writing Lua script to {lua_script_path}: {e}")

        if not lua_written:
            console.print(f"[bold yellow][ Rokid Manager ] - No valid path found to write Lua script for {executor_name}[/bold yellow]")

def detect_and_write_lua_script():
    console = Console()
    detected_executors = []

    for executor_name, base_path in executors.items():
        possible_autoexec_paths = [
            os.path.join(base_path, "Autoexec"),
            os.path.join(base_path, "Autoexecute"),
            os.path.join(base_path, "autoexec")
        ]

        lua_written = False

        for path in possible_autoexec_paths:
            if os.path.exists(path):
                lua_script_path = os.path.join(path, "executor_check.lua")
                
                try:
                    with open(lua_script_path, 'w') as file:
                        file.write(lua_script_template)
                    lua_written = True
                    console.print(f"[bold green][ Rokid Manager ] - Lua script written to: {lua_script_path}[/bold green]")
                    break

                except Exception as e:
                    console.print(f"[bold red][ Rokid Manager ] - Error writing Lua script to {lua_script_path}: {e}[/bold red]")
                    log_error(f"Error writing Lua script to {lua_script_path}: {e}")

        if lua_written:
            detected_executors.append(executor_name)

    return detected_executors

def check_and_create_cookie_file():
    folder_path = os.path.dirname(os.path.abspath(__file__))
    cookie_file_path = os.path.join(folder_path, 'cookie.txt')
    if not os.path.exists(cookie_file_path):
        with open(cookie_file_path, 'w') as f:
            f.write("")

def reset_executor_file(package_name):
    try:
        for workspace in globals()["workspace_paths"]:
            id = globals()["_user_"][package_name]
            file_path = os.path.join(workspace, f"{id}.main")
            if os.path.exists(file_path):
                os.remove(file_path)
            else:
                pass
    except:
        pass

def check_executor_status(package_name, continuous=True, max_wait_time=120):
    retry_timeout = time.time() + max_wait_time
    while True:
        for workspace in globals()["workspace_paths"]:
            id = globals()["_user_"][package_name]
            status_file = f"{id}.main"
            file_path = os.path.join(workspace, status_file)
            if os.path.exists(file_path):
                return True
        if continuous and time.time() > retry_timeout:
            return False
        time.sleep(1)

def check_executor_and_rejoin(package_name, server_link, next_package_event):
    user_id = globals()["_user_"][package_name]
    detected_executors = detect_executors()
    
    if len(detected_executors) > 0:
        write_lua_script(detected_executors)
        while True:
            reset_executor_file(package_name)
            try:
                start_time = time.time()
                executor_loaded = False
                
                while time.time() - start_time < 120:
                    if check_executor_status(package_name):
                        new_status = "\033[1;32mExecutor has loaded successfully\033[0m"
                        if globals()["package_statuses"][package_name]["Status"] != new_status:
                            globals()["package_statuses"][package_name]["Status"] = new_status
                            update_status_table()
                        executor_loaded = True
                        next_package_event.set()
                        break
                    time.sleep(0.5)
                
                if not executor_loaded:
                    new_status = "\033[1;31mExecutor didn't load. Rejoining...\033[0m"
                    if globals()["package_statuses"][package_name]["Status"] != new_status:
                        globals()["package_statuses"][package_name]["Status"] = new_status
                        update_status_table()
                        time.sleep(2)
                        reset_executor_file(package_name)
                        time.sleep(0.5)
                        kill_roblox_process(package_name)
                        time.sleep(5)
                        print(f"\033[1;33m[ Rokid Manager ] - Rejoining {package_name}...\033[0m")
                        globals()["package_statuses"][package_name]["Status"] = "\033[1;36mRejoining\033[0m"
                        update_status_table()
                        launch_roblox(package_name, server_link)
                        globals()["package_statuses"][package_name]["Status"] = "\033[1;32mJoined Roblox\033[0m"
                        update_status_table()
                    
                    with package_lock:
                        reset_executor_file(package_name)
                        time.sleep(0.5)
                        kill_roblox_process(package_name)
                        time.sleep(2)
                        print(f"\033[1;33m[ Rokid Manager ] - Rejoining {package_name}...\033[0m")
                        globals()["package_statuses"][package_name]["Status"] = "\033[1;36mRejoining\033[0m"
                        update_status_table()
                        launch_roblox(package_name, server_link)
                        globals()["package_statuses"][package_name]["Status"] = "\033[1;32mJoined Roblox\033[0m"
                        update_status_table()
                    continue
                    
            except Exception as e:
                new_status = f"\033[1;31mError checking executor for {package_name}: {e}\033[0m"
                if globals()["package_statuses"][package_name]["Status"] != new_status:
                    globals()["package_statuses"][package_name]["Status"] = new_status
                    update_status_table()
                    time.sleep(2)
                    reset_executor_file(package_name)
                    time.sleep(0.5)
                    kill_roblox_process(package_name)
                    time.sleep(5)
                    print(f"\033[1;33m[ Rokid Manager ] - Rejoining {package_name} after error...\033[0m")
                    globals()["package_statuses"][package_name]["Status"] = "\033[1;36mRejoining\033[0m"
                    update_status_table()
                    launch_roblox(package_name, server_link)
                    globals()["package_statuses"][package_name]["Status"] = "\033[1;32mJoined Roblox\033[0m"
                    update_status_table()
                
                with package_lock:
                    reset_executor_file(package_name)
                    time.sleep(0.5)
                    kill_roblox_process(package_name)
                    time.sleep(2)
                    print(f"\033[1;33m[ Rokid Manager ] - Rejoining {package_name} after error...\033[0m")
                    globals()["package_statuses"][package_name]["Status"] = "\033[1;36mRejoining\033[0m"
                    update_status_table()
                    launch_roblox(package_name, server_link)
                    globals()["package_statuses"][package_name]["Status"] = "\033[1;32mJoined Roblox\033[0m"
                    update_status_table()
    else:
        new_status = f"\033[1;32mJoined without executor for {user_id}\033[0m"
        if globals()["package_statuses"][package_name]["Status"] != new_status:
            globals()["package_statuses"][package_name]["Status"] = new_status
            update_status_table()
        next_package_event.set()

def launch_package_sequentially(server_links):
    for idx, (package_name, server_link) in enumerate(server_links):
        globals()["package_statuses"][package_name] = {
            "Status": "\033[1;36mInitializing\033[0m",
            "Username": get_username(globals().get("_user_", {}).get(package_name, "unknown")),
        }
        update_status_table()
        next_package_event = Event()

        with package_lock:
            print(f"\033[1;32m[ Rokid Manager ] - Starting {package_name}...\033[0m")
            try:
                globals()["package_statuses"][package_name]["Status"] = "\033[1;36mLaunching\033[0m"
                update_status_table()
                launch_roblox(package_name, server_link)
                globals()["package_statuses"][package_name]["Status"] = "\033[1;32mJoined Roblox\033[0m"
                update_status_table()
            except Exception as e:
                log_error(f"Error launching Roblox for {package_name}: {e}\n{traceback.format_exc()}")
                print(f"\033[1;31mError launching Roblox for {package_name}: {e}\033[0m")
                globals()["package_statuses"][package_name]["Status"] = "\033[1;31mLaunch failed\033[0m"
                update_status_table()

            if globals()["check_exec_enable"] == "1":
                threading.Thread(target=check_executor_and_rejoin, args=(package_name, server_link, next_package_event), daemon=True).start()
                print(f"\033[1;33m[ Rokid Manager ] - Waiting for {package_name} executor to load...\033[0m")
                next_package_event.wait()
                print(f"\033[1;32m[ Rokid Manager ] - {package_name} completed. {'All packages launched successfully!' if idx == len(server_links) - 1 else 'Moving to next package...'}\033[0m")

def monitor_presence(server_links, stop_event):
    while not stop_event.is_set():
        try:
            if globals()["check_exec_enable"] == "0":
                for package_name, server_link in server_links:
                    ckhuy = xuat(f"/data/data/{package_name}/app_webview/Default/Cookies")
                    presence_type = check_user_online(globals()["_user_"][package_name], ckhuy)
                    if presence_type != 2:
                        for i in range(3):
                            print(f"\033[1;31m{globals()['_user_'][package_name]} is offline, recheck({i+1}/3)\033[0m")
                            presence_type = check_user_online(globals()["_user_"][package_name], ckhuy)
                            if presence_type == 2:
                                break
                            time.sleep(5)
                    if presence_type == 2:
                        with status_lock:
                            globals()["package_statuses"][package_name]["Status"] = "\033[1;32mIn-Game\033[0m"
                            update_status_table()
                    else:
                        with status_lock:
                            globals()["package_statuses"][package_name]["Status"] = "\033[1;31mNot In-Game, Rejoining\033[0m"
                            update_status_table()
                        kill_roblox_process(package_name)
                        time.sleep(2)
                        threading.Thread(target=launch_roblox, args=[package_name, server_link], daemon=True).start()
            time.sleep(60)
        except Exception as e:
            log_error(f"Error in presence monitor: {e}")
            time.sleep(60)

def force_rejoin(server_links, interval, stop_event):
    start_time = time.time()
    while not stop_event.is_set():
        if interval != float('inf') and (time.time() - start_time >= interval):
            print("\033[1;31m[ Rokid Manager ] - Force killing Roblox processes due to time limit.\033[0m")
            kill_roblox_processes()
            start_time = time.time()
            print("\033[1;33m[ Rokid Manager ] - Waiting for 5 seconds before starting the rejoin process...\033[0m")
            time.sleep(5)
            launch_package_sequentially(server_links)
        time.sleep(60)

def main():
    global stop_webhook_thread
    _load_config()
    if webhook_url is not None and device_name is not None and interval is not None:
        print("\033[1;32m[ Rokid Manager ] - Configuration loaded. Starting webhook thread...\033[0m")
        start_webhook_thread()

    stop_main_event = threading.Event()

    while True:
        clear_screen()
        print_header(version)
        check_and_create_cookie_file()

        menu_options = [
            "Start Rejoin V2",
            "Different Server/Game ID",
            "Auto Setup User IDs",
            "Auto Login via Cookie",
            "Use Discord Webhook",
            "Select Check Online Method",
            "Setup Check UI",
            "Custom Package",
            "Exit"
        ]

        create_dynamic_menu(menu_options)
        setup_type = input("\033[1;93m[ Rokid Manager ] - Enter command: \033[0m")

        if setup_type == "1":
            # Load existing server links and accounts
            server_links = load_server_links()
            globals()["accounts"] = load_accounts()
            globals()["_uid_"] = {}

            # Auto setup User IDs if accounts are not set or need updating
            if not globals()["accounts"]:
                print("\033[1;32m[ Rokid Manager ] - Auto Setup User IDs from each package's appStorage.json...\033[0m")
                packages = get_roblox_packages()
                accounts = []

                for package_name in packages:
                    file_path = f'/data/data/{package_name}/files/appData/LocalStorage/appStorage.json'
                    try:
                        user_id = find_userid_from_file(file_path)
                        if user_id and user_id != "-1":
                            accounts.append((package_name, user_id))
                            globals()["_user_"][package_name] = user_id
                            print(f"\033[96m[ Rokid Manager ] - Found UserId for {package_name}: {user_id}\033[0m")
                        else:
                            print(f"\033[1;31m[ Rokid Manager ] - UserId not found for {package_name}. Make sure the file path is correct and the format is as expected.\033[0m")
                    except Exception as e:
                        print(f"\033[1;31m[ Rokid Manager ] - Error reading file for {package_name}: {e}\033[0m")
                        log_error(f"Error reading appStorage.json for {package_name}: {e}")

                if accounts:
                    save_accounts(accounts)
                    print("\033[1;32m[ Rokid Manager ] - User IDs saved from appStorage.json!\033[0m")
                    globals()["accounts"] = accounts
                else:
                    print("\033[1;31m[ Rokid Manager ] - No User IDs were found. Ensure the files are accessible and properly formatted.\033[0m")
                    input("\033[1;32m\nPress Enter to return to the menu...\033[0m")
                    continue

            # Check if server links are set
            if not server_links:
                print("\033[1;31m[ Rokid Manager ] - No game ID or private server link set up yet! Please set them up using option 2 before proceeding.\033[0m")
                input("\033[1;32m\nPress Enter to return to the menu...\033[0m")
                continue

            # Prompt for force rejoin interval
            try:
                force_rejoin_input = input("\033[1;93m[ Rokid Manager ] - Enter the force rejoin/kill Roblox interval in minutes (or 'q' to skip): \033[0m")
                if force_rejoin_input.lower() == 'q':
                    force_rejoin_interval = float('inf')
                    print("\033[1;32m[ Rokid Manager ] - Force rejoin/kill disabled.\033[0m")
                else:
                    force_rejoin_interval = int(force_rejoin_input) * 60
                    if force_rejoin_interval <= 0:
                        raise ValueError("\033[1;31m[ Rokid Manager ] - The interval must be a positive integer.\033[0m")
            except ValueError as ve:
                print(f"\033[1;31m[ Rokid Manager ] - Invalid input: {ve}. Please enter a valid interval in minutes or 'q' to skip.\033[0m")
                input("\033[1;32m[ Rokid Manager ] - Press Enter to return to the menu...\033[0m")
                continue

            kill_roblox_processes()
            time.sleep(5)
            launch_package_sequentially(server_links)
            globals()["is_runner_ez"] = True

            threading.Thread(target=monitor_presence, args=(server_links, stop_main_event), daemon=True).start()
            threading.Thread(target=force_rejoin, args=(server_links, force_rejoin_interval, stop_main_event), daemon=True).start()

            while not stop_main_event.is_set():
                time.sleep(500)
                with status_lock:
                    update_status_table()
        # Other setup_type cases remain unchanged
        elif setup_type == "2":
            try:
                packages = get_roblox_packages()
                if not packages:
                    print("\033[1;31m[ Rokid Manager ] - No Roblox packages detected. Please verify package configuration.\033[0m")
                    input("\033[1;32mPress Enter to return to the menu...\033[0m")
                    continue

                server_links = []
                for package_name in packages:
                    while True:
                        server_link = input(f"\033[93m[ Rokid Manager ] - Enter the game ID or private server link for {package_name}: \033[0m")
                        formatted_link = None

                        try:
                            formatted_link = format_server_link(server_link)
                        except Exception as e:
                            print(f"\033[1;31m[ Rokid Manager ] - Failed to format server link: {e}\033[0m")
                            log_error(f"Failed to format server link for {package_name}: {e}")
                            continue

                        if not formatted_link:
                            print("\033[1;31m[ Rokid Manager ] - Invalid server link provided. Please try again.\033[0m")
                        else:
                            server_links.append((package_name, formatted_link))
                            print(f"\033[1;32m[ Rokid Manager ] - Server link for {package_name} saved successfully.\033[0m")
                            break
                try:
                    save_server_links(server_links)
                    print("\033[1;32m[ Rokid Manager ] - All server links have been saved successfully.\033[0m")
                except Exception as e:
                    print(f"\033[1;31m[ Rokid Manager ] - Failed to save server links: {e}\033[0m")
                    log_error(f"Failed to save server links: {e}")

            except Exception as e:
                log_error(f"Unexpected error in setup_type '2': {e}")
                print("\033[1;31m[ Rokid Manager ] - An unexpected error occurred. Refer to error_log.txt for details.\033[0m")

            finally:
                input("\033[1;32m\nPress Enter to exit...\033[0m")
        elif setup_type == "3":
            try:
                print("\033[1;32m[ Rokid Manager ] - Auto Setup User IDs from each package's appStorage.json...\033[0m")
                packages = get_roblox_packages()
                accounts = []

                for package_name in packages:
                    file_path = f'/data/data/{package_name}/files/appData/LocalStorage/appStorage.json'
                    try:
                        user_id = find_userid_from_file(file_path)
                        if user_id and user_id != "-1":
                            accounts.append((package_name, user_id))
                            print(f"\033[96m[ Rokid Manager ] - Found UserId for {package_name}: {user_id}\033[0m")
                        else:
                            print(f"\033[1;31m[ Rokid Manager ] - UserId not found for {package_name}. Make sure the file path is correct and the format is as expected.\033[0m")
                    except Exception as e:
                        print(f"\033[1;31m[ Rokid Manager ] - Error reading file for {package_name}: {e}\033[0m")
                        log_error(f"Error reading appStorage.json for {package_name}: {e}")

                if accounts:
                    save_accounts(accounts)
                    print("\033[1;32m[ Rokid Manager ] - User IDs saved from appStorage.json!\033[0m")
                else:
                    print("\033[1;31m[ Rokid Manager ] - No User IDs were found. Ensure the files are accessible and properly formatted.\033[0m")
                    input("\033[1;32m\nPress Enter to return to the menu...\033[0m")
                    return

                while True:
                    print("\033[93m[ Rokid Manager ] - Select the game:\033[0m")
                    print(Fore.CYAN + "1. Blox Fruits")
                    print(Fore.CYAN + "2. Anime Defenders")
                    print(Fore.CYAN + "3. King Legacy")
                    print(Fore.CYAN + "4. Fisch")
                    print(Fore.CYAN + "5. Bee Swarm Simulator")
                    print(Fore.CYAN + "6. Anime Vanguards")
                    print(Fore.CYAN + "7. Pet GO")
                    print(Fore.CYAN + "8. Pet Simulator 99")
                    print(Fore.CYAN + "9. Meme Sea")
                    print(Fore.CYAN + "10. Anime Adventures")
                    print(Fore.CYAN + "11. Da Hood")
                    print(Fore.CYAN + "12. Da Hood VC")
                    print(Fore.CYAN + "13. Other game or Private Server Link")

                    choice = input("\033[93m[ Rokid Manager ] - Enter command: \033[0m").strip()

                    game_ids = {
                        "1": "2753915549",
                        "2": "17017769292",
                        "3": "4520749081",
                        "4": "16732694052",
                        "5": "1537690962",
                        "6": "16146832113",
                        "7": "18901165922",
                        "8": "8737899170",
                        "9": "10260193230",
                        "10": "8304191830",
                        "11": "2788229376",
                        "12": "7213786345"
                    }

                    if choice in game_ids:
                        server_link = game_ids[choice]
                        break
                    elif choice == "13":
                        server_link = input("\033[93m[ Rokid Manager ] - Enter the game ID or private server link: \033[0m")
                        break
                    else:
                        print("\033[1;31m[ Rokid Manager ] - Invalid choice, please try again.\033[0m")

                try:
                    formatted_link = format_server_link(server_link)
                    if formatted_link:
                        server_links = [(package_name, formatted_link) for package_name, id in accounts]
                        save_server_links(server_links)
                        print("\033[1;32m[ Rokid Manager ] - Game ID or private server link saved successfully!\033[0m")
                    else:
                        print("\033[1;31m[ Rokid Manager ] - Invalid server link provided. Could not save.\033[0m")
                except Exception as e:
                    print(f"\033[1;31m[ Rokid Manager ] - Error formatting or saving server link: {e}\033[0m")
                    log_error(f"Error formatting or saving server link: {e}")

            except Exception as e:
                log_error(f"Unexpected error in setup_type == '3': {e}")
                print("\033[1;31m[ Rokid Manager ] - An unexpected error occurred. Check error_log.txt for details.\033[0m")
            finally:
                input("\033[1;32m\nPress Enter to return to the menu...\033[0m")
        elif setup_type == "4":
            inject_cookies_and_appstorage()
            input("\033[1;32m\nPress Enter to exit...\033[0m")
        elif setup_type == "5":
            setup_webhook()
            input("\033[1;32m\nPress Enter to exit...\033[0m")
        elif setup_type == "6":
            select_check_user()
            input("\033[1;32m\nPress Enter to exit...\033[0m")
        elif setup_type == "7":
            toggle_check_ui()
            input("\033[1;32m\nPress Enter to exit...\033[0m")
        elif setup_type == "8":
            nexus = input("\033[1;93m[ Rokid Manager ] - Enter the package prefix (e.g., com.roblox, com.maru, com.anything): \033[0m").strip()

            with open("package.json", "w") as f:
                f.write(nexus)

            print(f"\033[1;92m[ Rokid Manager ] - package.json updated to: {nexus}\033[0m")
        elif setup_type == "9":
            print("\033[1;32m[ Rokid Manager ] - Exiting...\033[0m")
            stop_main_event.set()
            stop_webhook()
            break
        else:
            print("\033[1;31m[ Rokid Manager ] - Invalid choice. Please select a valid option.\033[0m")
            input("\033[1;32m\nPress Enter to continue...\033[0m")

if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
import os
import time
import subprocess
import json
import ssl
import shutil
import platform
import urllib.request
import threading
import sqlite3
from contextlib import contextmanager
from threading import Lock, Event, Thread
import sys
import signal
import atexit

# ====================== CẤU HÌNH CƠ BẢN ======================

APPLICATIONS = {
    '1. Roblox (Chính)': 'com.roblox.client',
}

CONFIG_FILE = 'roblox_config.json'
BRAND = "© ZNQ Enhanced"

# UI Configuration
UI_CLEAR_AFTER_TIMER = True
FOCUS_MODE_ON_START = True
TERMUX_WHITELIST = ["com.termux", "com.termux.api"]

# Performance settings
UPDATE_INTERVAL = 5  # seconds between UI updates
MAX_THREADS = 10
RETRY_ATTEMPTS = 3
TIMEOUT_SECONDS = 10

# ====================== GLOBAL STATE MANAGEMENT ======================

class GlobalState:
    def __init__(self):
        self._lock = Lock()
        self._package_statuses = {}
        self._running = False
        self._cleanup_handlers = []
        
    @contextmanager
    def lock(self):
        self._lock.acquire()
        try:
            yield
        finally:
            self._lock.release()
            
    def set_package_status(self, package, status):
        with self.lock():
            if package not in self._package_statuses:
                self._package_statuses[package] = {}
            self._package_statuses[package].update(status)
    
    def get_package_status(self, package):
        with self.lock():
            return self._package_statuses.get(package, {})
    
    def get_all_statuses(self):
        with self.lock():
            return self._package_statuses.copy()
    
    def register_cleanup(self, handler):
        self._cleanup_handlers.append(handler)
    
    def cleanup(self):
        for handler in self._cleanup_handlers:
            try:
                handler()
            except Exception as e:
                print(f"Error in cleanup handler: {e}")

# Global state instance
state = GlobalState()

# ====================== EXCEPTION CLASSES ======================

class ZNQError(Exception):
    """Base exception for ZNQ tool"""
    pass

class DatabaseError(ZNQError):
    """Database operation errors"""
    pass

class ProcessError(ZNQError):
    """Process management errors"""
    pass

class ConfigError(ZNQError):
    """Configuration errors"""
    pass

# ====================== UTILITY FUNCTIONS ======================

def ensure_dependencies():
    """Ensure required dependencies are installed"""
    try:
        import psutil
        return True
    except ImportError:
        print("\n❌ Missing required library 'psutil'")
        print("Install it with: pip install psutil")
        return False

def safe_subprocess_run(cmd, timeout=TIMEOUT_SECONDS, **kwargs):
    """Run subprocess with proper error handling"""
    try:
        if isinstance(cmd, str):
            cmd = cmd.split()
        
        result = subprocess.run(
            cmd, 
            timeout=timeout,
            capture_output=True,
            text=True,
            **kwargs
        )
        return result
    except subprocess.TimeoutExpired:
        raise ProcessError(f"Command timed out: {' '.join(cmd)}")
    except Exception as e:
        raise ProcessError(f"Command failed: {e}")

def term_width(default=80):
    """Get terminal width safely"""
    try:
        return shutil.get_terminal_size((default, 24)).columns
    except Exception:
        return default

def center_line(s: str, fill=' '):
    """Center text in terminal"""
    w = term_width()
    try:
        return s.center(w, fill) if fill != ' ' else s.center(w)
    except Exception:
        return s

def print_big_znq():
    """Display ZNQ banner"""
    banner = [
        "██████ ███   █ ██████",
        "     █ ████  █ █    █",
        "    █  █ ██ █ █    █",
        "   █   █  ███ █    █",
        "  █    █   ██ █    █",
        " █     █    █ █    █",
        "██████ █    █ ██████"
    ]
    
    print()
    for line in banner:
        print("\033[95m" + center_line(line) + "\033[0m")
    print(center_line("== ZNQ ENHANCED REJOIN =="))
    print(center_line("-" * 28))

# ====================== CONFIGURATION MANAGEMENT ======================

class ConfigManager:
    def __init__(self, config_file):
        self.config_file = config_file
        self._lock = Lock()
        
    def load_config(self):
        """Load configuration with proper error handling"""
        try:
            if not os.path.exists(self.config_file):
                return self._get_default_config()
                
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                return self._validate_config(config)
        except json.JSONDecodeError as e:
            raise ConfigError(f"Invalid JSON in config file: {e}")
        except Exception as e:
            raise ConfigError(f"Error loading config: {e}")
    
    def save_config(self, config):
        """Save configuration safely"""
        try:
            validated_config = self._validate_config(config)
            
            # Create backup
            if os.path.exists(self.config_file):
                backup_file = f"{self.config_file}.backup"
                shutil.copy2(self.config_file, backup_file)
            
            with self._lock:
                with open(self.config_file, 'w') as f:
                    json.dump(validated_config, f, indent=4)
            return True
        except Exception as e:
            raise ConfigError(f"Error saving config: {e}")
    
    def _get_default_config(self):
        """Get default configuration"""
        return {
            'packages': [],
            'place_id': '',
            'interval': 60,
            'pulse_delay': 2,
            'rejoin_every': 5,
            'auto_clear_cache': {
                'enabled': False,
                'minutes': 30,
                'packages': []
            },
            'webhook_heartbeat_minutes': 0,
            'discord_webhook': ""
        }
    
    def _validate_config(self, config):
        """Validate configuration structure"""
        default = self._get_default_config()
        
        # Ensure all required keys exist
        for key, default_value in default.items():
            if key not in config:
                config[key] = default_value
        
        # Validate data types
        if not isinstance(config.get('packages', []), list):
            config['packages'] = []
        
        if not isinstance(config.get('interval', 60), int) or config['interval'] <= 0:
            config['interval'] = 60
            
        if not isinstance(config.get('pulse_delay', 2), int) or config['pulse_delay'] < 0:
            config['pulse_delay'] = 2
        
        return config

# ====================== PROCESS MANAGEMENT ======================

class ProcessManager:
    def __init__(self):
        self._running_processes = set()
        
    def is_package_running(self, package_name):
        """Check if package is running - Android compatible"""
        try:
            # Method 1: Use ps command (most reliable on Android)
            result = safe_subprocess_run(['ps'], timeout=5)
            if result.returncode == 0 and package_name in result.stdout:
                return True
            
            # Method 2: Try pgrep if available
            try:
                result = safe_subprocess_run(['pgrep', '-f', package_name], timeout=5)
                return result.returncode == 0
            except ProcessError:
                pass
            
            # Method 3: Check /proc (fallback)
            try:
                for pid_dir in os.listdir('/proc'):
                    if pid_dir.isdigit():
                        cmdline_path = f'/proc/{pid_dir}/cmdline'
                        if os.path.exists(cmdline_path):
                            with open(cmdline_path, 'r') as f:
                                cmdline = f.read()
                                if package_name in cmdline:
                                    return True
            except (OSError, PermissionError):
                pass
            
            return False
        except Exception:
            return False
    
    def kill_package(self, package_name):
        """Kill package safely"""
        try:
            # Use Android's am command
            result = safe_subprocess_run(['am', 'force-stop', package_name])
            if result.returncode != 0:
                raise ProcessError(f"Failed to stop {package_name}: {result.stderr}")
            
            # Wait and verify
            for _ in range(5):
                time.sleep(1)
                if not self.is_package_running(package_name):
                    return True
            
            print(f"Warning: {package_name} may still be running")
            return False
        except Exception as e:
            raise ProcessError(f"Error killing {package_name}: {e}")
    
    def launch_package(self, package_name, uri):
        """Launch package with proper error handling"""
        try:
            # Kill first
            self.kill_package(package_name)
            time.sleep(2)
            
            # Launch main activity
            cmd_main = [
                'am', 'start',
                '-a', 'android.intent.action.MAIN',
                '-n', f'{package_name}/com.roblox.client.startup.ActivitySplash'
            ]
            result = safe_subprocess_run(cmd_main)
            if result.returncode != 0:
                raise ProcessError(f"Failed to launch {package_name}: {result.stderr}")
            
            time.sleep(10)  # Wait for app to load
            
            # Launch with URI
            cmd_uri = [
                'am', 'start',
                '-a', 'android.intent.action.VIEW',
                '-d', uri,
                '-p', package_name
            ]
            result = safe_subprocess_run(cmd_uri)
            if result.returncode != 0:
                print(f"Warning: URI launch may have failed: {result.stderr}")
            
            return True
        except Exception as e:
            raise ProcessError(f"Error launching {package_name}: {e}")

# ====================== DATABASE MANAGEMENT ======================

class DatabaseManager:
    @staticmethod
    @contextmanager
    def safe_db_connection(db_path):
        """Safe database connection with proper cleanup"""
        if not os.path.exists(db_path):
            raise DatabaseError(f"Database not found: {db_path}")
        
        conn = None
        try:
            conn = sqlite3.connect(db_path, timeout=10)
            conn.execute("PRAGMA journal_mode=WAL")  # Better concurrency
            yield conn
        except sqlite3.Error as e:
            raise DatabaseError(f"Database error: {e}")
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def update_cookie_in_db(db_path, new_cookie):
        """Update cookie in database safely"""
        try:
            with DatabaseManager.safe_db_connection(db_path) as conn:
                cursor = conn.cursor()
                
                # Check if cookie exists
                cursor.execute(
                    "SELECT COUNT(*) FROM cookies WHERE host_key = '.roblox.com' AND name = '.ROBLOSECURITY'"
                )
                if cursor.fetchone()[0] == 0:
                    raise DatabaseError("Cookie entry not found in database")
                
                # Update cookie
                current_time = int(time.time() + 11644473600) * 1000000
                expire_time = current_time + (365 * 24 * 3600 * 1000000)  # 1 year
                
                cursor.execute(
                    "UPDATE cookies SET value = ?, last_access_utc = ?, expires_utc = ? "
                    "WHERE host_key = '.roblox.com' AND name = '.ROBLOSECURITY'",
                    (new_cookie, current_time, expire_time)
                )
                
                if cursor.rowcount == 0:
                    raise DatabaseError("Cookie update failed")
                
                conn.commit()
                return True
        except Exception as e:
            raise DatabaseError(f"Failed to update cookie: {e}")

# ====================== SYSTEM MONITORING ======================

class SystemMonitor:
    def __init__(self):
        self._last_update = 0
        self._cached_info = None
        
    def get_system_info(self, packages, force_update=False):
        """Get system information with caching"""
        now = time.time()
        if not force_update and now - self._last_update < UPDATE_INTERVAL and self._cached_info:
            return self._cached_info
        
        try:
            import psutil
            
            # Get basic system info
            cpu = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            # Get running packages
            running_count = sum(1 for pkg in packages if ProcessManager().is_package_running(pkg))
            
            # Get uptime
            boot_time = psutil.boot_time()
            uptime_seconds = time.time() - boot_time
            uptime = self._format_uptime(uptime_seconds)
            
            # Get battery (if available)
            battery = self._get_battery_info()
            
            info = {
                'cpu': f"{cpu:.1f}%",
                'ram_pct': f"{memory.percent:.1f}%",
                'ram_avail': self._format_gb(memory.available),
                'ram_total': self._format_gb(memory.total),
                'battery': battery,
                'uptime': uptime,
                'running': running_count,
                'total': len(packages)
            }
            
            self._cached_info = info
            self._last_update = now
            return info
            
        except ImportError:
            return self._get_basic_system_info(packages)
        except Exception as e:
            print(f"Error getting system info: {e}")
            return self._get_basic_system_info(packages)
    
    def _format_uptime(self, seconds):
        """Format uptime in human readable format"""
        days = int(seconds // (24 * 3600))
        hours = int((seconds % (24 * 3600)) // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{days}d {hours}h {minutes}m"
    
    def _format_gb(self, bytes_value):
        """Format bytes to GB"""
        try:
            return f"{(bytes_value / (1024**3)):.2f} GB"
        except Exception:
            return "N/A"
    
    def _get_battery_info(self):
        """Get battery information"""
        try:
            import psutil
            if hasattr(psutil, "sensors_battery"):
                battery = psutil.sensors_battery()
                if battery and battery.percent is not None:
                    return f"{int(battery.percent)}%"
        except Exception:
            pass
        
        # Fallback to dumpsys
        try:
            result = safe_subprocess_run(['dumpsys', 'battery'], timeout=5)
            if result.returncode == 0:
                for line in result.stdout.splitlines():
                    if 'level:' in line.lower():
                        level = line.split(':')[1].strip()
                        return f"{level}%"
        except Exception:
            pass
        
        return "N/A"
    
    def _get_basic_system_info(self, packages):
        """Basic system info without psutil"""
        running_count = sum(1 for pkg in packages if ProcessManager().is_package_running(pkg))
        
        return {
            'cpu': "N/A",
            'ram_pct': "N/A",
            'ram_avail': "N/A", 
            'ram_total': "N/A",
            'battery': self._get_battery_info(),
            'uptime': "N/A",
            'running': running_count,
            'total': len(packages)
        }

# ====================== THREAD MANAGEMENT ======================

class ThreadManager:
    def __init__(self):
        self._threads = []
        self._stop_event = Event()
        
    def start_thread(self, target, args=(), name=None):
        """Start a managed thread"""
        if len(self._threads) >= MAX_THREADS:
            self._cleanup_finished_threads()
        
        thread = Thread(target=target, args=args, name=name, daemon=True)
        thread.start()
        self._threads.append(thread)
        return thread
    
    def stop_all(self, timeout=10):
        """Stop all managed threads"""
        self._stop_event.set()
        
        for thread in self._threads[:]:  # Create copy to avoid modification during iteration
            if thread.is_alive():
                thread.join(timeout=timeout)
                if thread.is_alive():
                    print(f"Warning: Thread {thread.name} did not stop gracefully")
    
    def _cleanup_finished_threads(self):
        """Remove finished threads from list"""
        self._threads = [t for t in self._threads if t.is_alive()]
    
    @property
    def should_stop(self):
        return self._stop_event.is_set()

# Global thread manager
thread_manager = ThreadManager()

# ====================== DASHBOARD UI ======================

class Dashboard:
    def __init__(self):
        self._last_content_hash = None
        self._last_update = 0
        
    def update_display(self, title, place_id, packages, system_info, package_statuses, start_time):
        """Update dashboard only if content changed"""
        current_time = time.time()
        
        # Rate limit updates
        if current_time - self._last_update < 2:  # Max 0.5 fps
            return
        
        content = self._generate_content(title, place_id, packages, system_info, package_statuses, start_time)
        content_hash = hash(str(content))
        
        if content_hash != self._last_content_hash:
            self._render_dashboard(content)
            self._last_content_hash = content_hash
            self._last_update = current_time
    
    def _generate_content(self, title, place_id, packages, system_info, package_statuses, start_time):
        """Generate dashboard content"""
        uptime = self._format_uptime(time.time() - start_time)
        date_str = time.strftime("%d/%m/%Y")
        
        rows = []
        for pkg in packages:
            status_info = package_statuses.get(pkg, {})
            running = ProcessManager().is_package_running(pkg)
            
            row = {
                'pkg': pkg,
                'status': 'Online' if running else 'Offline',
                'info': status_info.get('info', 'Monitoring...'),
                'time': status_info.get('time', time.strftime("%H:%M:%S"))
            }
            rows.append(row)
        
        return {
            'title': title,
            'date': date_str,
            'uptime': uptime,
            'place_id': place_id,
            'system_info': system_info,
            'rows': rows
        }
    
    def _render_dashboard(self, content):
        """Render dashboard to terminal"""
        self._clear_screen()
        
        # Calculate dimensions
        width = term_width(100)
        inner_width = max(70, min(140, width - 2))
        bar = "═" * inner_width
        
        # Header
        print(f"╔{bar}╗")
        title_line = f" {content['title']} ".center(inner_width)
        print(f"║{title_line}║")
        
        # Date and uptime
        left_info = f"Ngày: {content['date']}"
        right_info = f"Uptime: {content['uptime']}"
        padding = max(1, inner_width - len(left_info) - len(right_info))
        print(f"║{left_info}{' ' * padding}{right_info}║")
        
        # Separator
        print(f"╠{bar}╣")
        
        # System info
        sys_info = content['system_info']
        info_line = f"CPU: {sys_info['cpu']} | RAM: {sys_info['ram_pct']} | Battery: {sys_info['battery']} | Running: {sys_info['running']}/{sys_info['total']}"
        print(f"║{info_line.center(inner_width)}║")
        
        print(f"╠{bar}╣")
        
        # Table header
        col_widths = self._calculate_column_widths(inner_width)
        header = self._format_table_row(["Package", "Status", "Info", "Time"], col_widths)
        print(f"║{header}║")
        
        # Separator
        sep_parts = ["-" * w for w in col_widths]
        separator = "┼".join(sep_parts)
        print(f"╟{separator}╢")
        
        # Data rows
        for row in content['rows']:
            data_row = self._format_table_row([
                self._truncate(row['pkg'], col_widths[0]),
                self._truncate(row['status'], col_widths[1]), 
                self._truncate(row['info'], col_widths[2]),
                self._truncate(row['time'], col_widths[3])
            ], col_widths)
            print(f"║{data_row}║")
        
        # Footer
        footer_text = "Nhấn Ctrl+C để dừng | ZNQ Enhanced"
        print(f"╟{footer_text.ljust(inner_width)}╢")
        print(f"╚{bar}╝")
    
    def _calculate_column_widths(self, total_width):
        """Calculate optimal column widths"""
        separators = 3 * 3  # 3 separators of " | "
        available = total_width - separators
        
        # Allocate widths
        return [
            max(15, available // 4),      # Package
            max(12, available // 6),      # Status  
            max(20, available // 2),      # Info
            max(10, available // 8)       # Time
        ]
    
    def _format_table_row(self, items, widths):
        """Format a table row with proper spacing"""
        formatted_items = []
        for item, width in zip(items, widths):
            formatted_items.append(str(item).ljust(width))
        return " | ".join(formatted_items)
    
    def _truncate(self, text, max_length):
        """Truncate text with ellipsis"""
        text = str(text or "")
        if len(text) <= max_length:
            return text
        return text[:max_length-1] + "…"
    
    def _format_uptime(self, seconds):
        """Format uptime string"""
        seconds = int(seconds)
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours:02d}h{minutes:02d}m{secs:02d}s"
    
    def _clear_screen(self):
        """Clear screen efficiently"""
        print("\033[2J\033[H", end='')

# ====================== MAIN APPLICATION ======================

class ZNQRejoin:
    def __init__(self):
        self.config_manager = ConfigManager(CONFIG_FILE)
        self.process_manager = ProcessManager()
        self.system_monitor = SystemMonitor()
        self.dashboard = Dashboard()
        self.running = False
        
        # Register cleanup handler
        state.register_cleanup(self._cleanup)
        atexit.register(self._cleanup)
        
        # Handle signals
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle system signals for graceful shutdown"""
        print("\n\nReceived shutdown signal...")
        self.stop()
        sys.exit(0)
    
    def _cleanup(self):
        """Cleanup resources"""
        self.running = False
        thread_manager.stop_all()
        state.cleanup()
    
    def setup_configuration(self):
        """Interactive configuration setup"""
        print_big_znq()
        print(center_line("--- Cấu hình Tool ---"))
        
        try:
            config = self.config_manager.load_config()
            
            # Display current config if exists
            if config.get('packages') and config.get('place_id'):
                print(f"\nCấu hình hiện tại:")
                print(f"  Place ID: {config['place_id']}")
                print(f"  Packages: {', '.join(config['packages'])}")
                print(f"  Interval: {config['interval']}s")
                
                if input("\nDùng cấu hình cũ? (y/n): ").strip().lower() == 'y':
                    return config
            
            # Get new configuration
            place_id = input("\nNhập Place ID: ").strip()
            if not place_id.isdigit():
                raise ConfigError("Place ID phải là số")
            
            # Package selection
            print("\n--- Chọn ứng dụng ---")
            for key, value in APPLICATIONS.items():
                print(f"  {key}: {value}")
            
            packages = []
            selection = input("Chọn ứng dụng (1): ").strip() or "1"
            
            if selection == "1":
                packages = [APPLICATIONS['1. Roblox (Chính)']]
            else:
                print("Lựa chọn không hợp lệ, sử dụng mặc định")
                packages = [APPLICATIONS['1. Roblox (Chính)']]
            
            # Timing configuration
            try:
                interval = int(input("Chu kỳ kiểm tra (giây, mặc định=60): ").strip() or "60")
            except ValueError:
                interval = 60
                
            try:
                pulse_delay = int(input("Độ trễ giữa lần khởi chạy (giây, mặc định=2): ").strip() or "2")
            except ValueError:
                pulse_delay = 2
            
            # Create configuration
            new_config = {
                'place_id': place_id,
                'packages': packages,
                'interval': max(30, interval),  # Minimum 30 seconds
                'pulse_delay': max(0, pulse_delay),
                'rejoin_every': 5,
                'auto_clear_cache': {'enabled': False, 'minutes': 30, 'packages': []},
                'webhook_heartbeat_minutes': 0,
                'discord_webhook': ""
            }
            
            # Save configuration
            if self.config_manager.save_config(new_config):
                print("\n✅ Đã lưu cấu hình!")
                return new_config
            else:
                raise ConfigError("Không thể lưu cấu hình")
                
        except Exception as e:
            print(f"\n❌ Lỗi cấu hình: {e}")
            return None
    
    def start_monitoring(self, config):
        """Start the monitoring process"""
        if not ensure_dependencies():
            return False
        
        packages = config['packages']
        place_id = config['place_id']
        interval = config['interval']
        pulse_delay = config['pulse_delay']
        
        print(f"\n🚀 Bắt đầu giám sát {len(packages)} package(s)...")
        print("Nhấn Ctrl+C để dừng")
        
        self.running = True
        start_time = time.time()
        uri = f"roblox://placeId={place_id}"
        
        # Initialize package statuses
        for pkg in packages:
            state.set_package_status(pkg, {
                'status': 'Initializing',
                'info': 'Khởi tạo...',
                'time': time.strftime("%H:%M:%S")
            })
        
        # Initial launch
        self._initial_launch(packages, uri, pulse_delay)
        
        # Start monitoring thread
        monitor_thread = thread_manager.start_thread(
            target=self._monitoring_loop,
            args=(packages, uri, interval, start_time),
            name="MonitorLoop"
        )
        
        # Start UI update thread
        ui_thread = thread_manager.start_thread(
            target=self._ui_update_loop,
            args=(packages, place_id, start_time),
            name="UIUpdate"
        )
        
        # Wait for threads to finish
        try:
            while self.running and not thread_manager.should_stop:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n⏹️ Stopping...")
            self.stop()
        
        return True
    
    def _initial_launch(self, packages, uri, pulse_delay):
        """Launch all packages initially"""
        print("📱 Khởi chạy ban đầu...")
        
        for i, pkg in enumerate(packages, 1):
            try:
                print(f"  [{i}/{len(packages)}] Launching {pkg}...")
                
                state.set_package_status(pkg, {
                    'status': 'Launching',
                    'info': 'Đang khởi chạy...',
                    'time': time.strftime("%H:%M:%S")
                })
                
                self.process_manager.launch_package(pkg, uri)
                
                state.set_package_status(pkg, {
                    'status': 'Running',
                    'info': 'Đã khởi chạy thành công',
                    'time': time.strftime("%H:%M:%S")
                })
                
                if pulse_delay > 0:
                    time.sleep(pulse_delay)
                    
            except Exception as e:
                print(f"  ❌ Error launching {pkg}: {e}")
                state.set_package_status(pkg, {
                    'status': 'Error',
                    'info': f'Lỗi khởi chạy: {str(e)[:30]}...',
                    'time': time.strftime("%H:%M:%S")
                })
    
    def _monitoring_loop(self, packages, uri, interval, start_time):
        """Main monitoring loop"""
        cycle = 0
        
        while self.running and not thread_manager.should_stop:
            cycle += 1
            
            try:
                for pkg in packages:
                    if not self.running:
                        break
                    
                    is_running = self.process_manager.is_package_running(pkg)
                    current_time = time.strftime("%H:%M:%S")
                    
                    if not is_running:
                        # Package died, restart it
                        print(f"🔄 Package {pkg} stopped, restarting...")
                        
                        state.set_package_status(pkg, {
                            'status': 'Restarting',
                            'info': 'Package đã dừng, đang khởi động lại',
                            'time': current_time
                        })
                        
                        try:
                            self.process_manager.launch_package(pkg, uri)
                            state.set_package_status(pkg, {
                                'status': 'Running',
                                'info': 'Đã khởi động lại thành công',
                                'time': time.strftime("%H:%M:%S")
                            })
                        except Exception as e:
                            state.set_package_status(pkg, {
                                'status': 'Error',
                                'info': f'Lỗi khởi động lại: {str(e)[:30]}...',
                                'time': time.strftime("%H:%M:%S")
                            })
                    else:
                        # Package is running fine
                        state.set_package_status(pkg, {
                            'status': 'Running',
                            'info': f'Đang hoạt động (Cycle #{cycle})',
                            'time': current_time
                        })
                
                # Sleep for interval
                sleep_time = 0
                while sleep_time < interval and self.running and not thread_manager.should_stop:
                    time.sleep(1)
                    sleep_time += 1
                    
            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                time.sleep(10)  # Wait before retrying
    
    def _ui_update_loop(self, packages, place_id, start_time):
        """UI update loop"""
        while self.running and not thread_manager.should_stop:
            try:
                system_info = self.system_monitor.get_system_info(packages)
                package_statuses = state.get_all_statuses()
                
                self.dashboard.update_display(
                    "ZNQ Enhanced Rejoin Monitor",
                    place_id,
                    packages,
                    system_info,
                    package_statuses,
                    start_time
                )
                
                time.sleep(2)  # Update UI every 2 seconds
                
            except Exception as e:
                print(f"Error in UI update: {e}")
                time.sleep(5)
    
    def stop(self):
        """Stop the application gracefully"""
        print("🛑 Stopping ZNQ Rejoin...")
        self.running = False
        thread_manager.stop_all(timeout=5)
        print("✅ Stopped successfully")
    
    def run(self):
        """Main application entry point"""
        try:
            print_big_znq()
            
            config = self.setup_configuration()
            if not config:
                print("❌ Không thể thiết lập cấu hình")
                return False
            
            return self.start_monitoring(config)
            
        except KeyboardInterrupt:
            print("\n\n⏹️ Interrupted by user")
            return True
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            return False
        finally:
            self._cleanup()

# ====================== ENTRY POINT ======================

def main():
    """Application entry point"""
    app = ZNQRejoin()
    success = app.run()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())

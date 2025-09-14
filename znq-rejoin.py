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

# ====================== PACKAGE DETECTION ======================

def get_roblox_packages(prefix=None):
    """Dynamic package detection with configurable prefix"""
    if prefix is None:
        config = load_config()
        prefix = config.get('package_prefix', 'com.roblox')
    
    packages = []
    try:
        # Use pm command to list packages with prefix
        result = subprocess.run(
            f"pm list packages {prefix} | sed 's/package://'", 
            shell=True, 
            capture_output=True, 
            text=True
        )
        
        if result.returncode == 0:
            for line in result.stdout.strip().splitlines():
                name = line.strip()
                if name:  # Only add non-empty names
                    packages.append(name)
        else:
            print(f"⚠️  Failed to get packages with prefix: {prefix}")
            
    except Exception as e:
        print(f"❌ Error getting packages: {e}")
    
    return packages

def configure_package_prefix():
    """Interactive package prefix configuration"""
    config = load_config()
    current_prefix = config.get('package_prefix', 'com.roblox')
    
    print(f"\n🔧 Current package prefix: {current_prefix}")
    print("\n📱 Package prefix options:")
    print("  1. com.roblox    - Standard Roblox")
    print("  2. Custom prefix - Enter your own")
    
    choice = input("\nSelect option (1-2) or press Enter to keep current: ").strip()
    
    if choice == '1':
        new_prefix = 'com.roblox'
    elif choice == '2':
        new_prefix = input("Enter custom prefix: ").strip()
        if not new_prefix:
            print("❌ Empty prefix not allowed")
            return config
    elif choice == '':
        print("✅ Keeping current prefix")
        return config
    else:
        print("❌ Invalid choice")
        return config
    
    # Test new prefix
    print(f"\n🔍 Testing prefix: {new_prefix}")
    packages = get_roblox_packages(new_prefix)
    
    if packages:
        print(f"✅ Found {len(packages)} packages:")
        for pkg in packages[:5]:  # Show first 5
            print(f"  - {pkg}")
        if len(packages) > 5:
            print(f"  ... and {len(packages)-5} more")
        
        config['package_prefix'] = new_prefix
        save_config(config)
        print(f"\n✅ Package prefix updated to: {new_prefix}")
    else:
        print(f"❌ No packages found with prefix: {new_prefix}")
        print("❌ Keeping original prefix")
    
    return config

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

def load_config():
    """Load configuration with proper error handling"""
    try:
        if not os.path.exists(CONFIG_FILE):
            return get_default_config()
            
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            return validate_config(config)
    except json.JSONDecodeError as e:
        raise ConfigError(f"Invalid JSON in config file: {e}")
    except Exception as e:
        raise ConfigError(f"Error loading config: {e}")

def save_config(config):
    """Save configuration safely"""
    try:
        validated_config = validate_config(config)
        
        # Create backup
        if os.path.exists(CONFIG_FILE):
            backup_file = f"{CONFIG_FILE}.backup"
            shutil.copy2(CONFIG_FILE, backup_file)
        
        with open(CONFIG_FILE, 'w') as f:
            json.dump(validated_config, f, indent=4)
        return True
    except Exception as e:
        raise ConfigError(f"Error saving config: {e}")

def get_default_config():
    """Get default configuration"""
    return {
        'package_prefix': 'com.roblox',
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

def validate_config(config):
    """Validate configuration structure"""
    default = get_default_config()
    
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
    
    # Ensure package_prefix exists
    if 'package_prefix' not in config:
        config['package_prefix'] = 'com.roblox'
    
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

# ====================== MAIN APPLICATION ======================

class ZNQRejoin:
    def __init__(self):
        self.process_manager = ProcessManager()
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
        state.cleanup()
    
    def show_detected_packages(self):
        """Show all detected Roblox packages"""
        config = load_config()
        prefix = config.get('package_prefix', 'com.roblox')
        
        print(f"\n📱 Detecting packages with prefix: {prefix}")
        packages = get_roblox_packages()
        
        if packages:
            print(f"✅ Found {len(packages)} Roblox packages:")
            for i, pkg in enumerate(packages, 1):
                print(f"  {i}. {pkg}")
            return packages
        else:
            print("❌ No Roblox packages found!")
            print("💡 Try configuring package prefix first")
            return []
    
    def setup_configuration(self):
        """Interactive configuration setup"""
        print_big_znq()
        print(center_line("--- CẤU HÌNH TOOL ---"))
        
        while True:
            print("\n" + "="*50)
            print("🛠️  ZNQ REJOIN ENHANCED - SETUP MENU")
            print("="*50)
            print("1. 📱 Show Detected Packages")
            print("2. ⚙️  Configure Package Prefix")
            print("3. 🎮 Setup Place ID & Start Tool")
            print("4. 📊 Show Current Settings")
            print("0. ❌ Exit")
            print("="*50)
            
            choice = input("\n🎯 Enter choice: ").strip()
            
            if choice == '1':
                packages = self.show_detected_packages()
                if not packages:
                    print("\n💡 Tip: Try option 2 to configure package prefix")
                
            elif choice == '2':
                configure_package_prefix()
                
            elif choice == '3':
                return self.setup_place_id_and_start()
                
            elif choice == '4':
                self.show_current_settings()
                
            elif choice == '0':
                print("👋 Goodbye!")
                return None
                
            else:
                print("❌ Invalid choice")
            
            input("\nPress Enter to continue...")
    
    def setup_place_id_and_start(self):
        """Setup place ID and start monitoring"""
        try:
            config = load_config()
            
            # Check if we have packages
            packages = get_roblox_packages()
            if not packages:
                print("\n❌ No packages detected!")
                print("💡 Configure package prefix first (option 2)")
                return None
            
            print(f"\n✅ Found {len(packages)} packages:")
            for pkg in packages:
                print(f"  - {pkg}")
            
            # Get place ID
            current_place_id = config.get('place_id', '')
            if current_place_id:
                print(f"\nCurrent Place ID: {current_place_id}")
                use_current = input("Use current Place ID? (y/n): ").strip().lower()
                if use_current == 'y':
                    place_id = current_place_id
                else:
                    place_id = input("Enter new Place ID: ").strip()
            else:
                place_id = input("\nEnter Place ID: ").strip()
            
            if not place_id.isdigit():
                raise ConfigError("Place ID must be a number")
            
            # Timing configuration
            try:
                interval = int(input("Monitoring interval (seconds, default=60): ").strip() or "60")
            except ValueError:
                interval = 60
                
            try:
                pulse_delay = int(input("Delay between launches (seconds, default=2): ").strip() or "2")
            except ValueError:
                pulse_delay = 2
            
            # Save configuration
            config.update({
                'place_id': place_id,
                'packages': packages,
                'interval': max(30, interval),
                'pulse_delay': max(0, pulse_delay),
            })
            
            if save_config(config):
                print("\n✅ Configuration saved!")
                return config
            else:
                raise ConfigError("Failed to save configuration")
                
        except Exception as e:
            print(f"\n❌ Setup error: {e}")
            return None
    
    def show_current_settings(self):
        """Display current configuration"""
        config = load_config()
        print(f"\n📋 Current Settings:")
        print(f"  Package Prefix: {config.get('package_prefix', 'com.roblox')}")
        print(f"  Place ID: {config.get('place_id', 'Not set')}")
        print(f"  Packages: {len(config.get('packages', []))} detected")
        print(f"  Interval: {config.get('interval', 60)}s")
        print(f"  Pulse Delay: {config.get('pulse_delay', 2)}s")
        
        packages = config.get('packages', [])
        if packages:
            print(f"\n📦 Detected packages:")
            for pkg in packages[:3]:
                print(f"  - {pkg}")
            if len(packages) > 3:
                print(f"  ... and {len(packages)-3} more")
    
    def start_monitoring(self, config):
        """Start the monitoring process"""
        if not ensure_dependencies():
            return False
        
        packages = config['packages']
        place_id = config['place_id']
        interval = config['interval']
        pulse_delay = config['pulse_delay']
        
        print(f"\n🚀 Starting monitoring for {len(packages)} package(s)...")
        print("Press Ctrl+C to stop")
        
        self.running = True
        uri = f"roblox://placeId={place_id}"
        
        # Simple monitoring loop
        try:
            while self.running:
                for pkg in packages:
                    if not self.running:
                        break
                    
                    is_running = self.process_manager.is_package_running(pkg)
                    current_time = time.strftime("%H:%M:%S")
                    
                    if not is_running:
                        print(f"🔄 [{current_time}] Package {pkg} stopped, restarting...")
                        try:
                            self.process_manager.launch_package(pkg, uri)
                            print(f"✅ [{current_time}] Successfully restarted {pkg}")
                        except Exception as e:
                            print(f"❌ [{current_time}] Failed to restart {pkg}: {e}")
                    else:
                        print(f"✅ [{current_time}] Package {pkg} is running")
                
                # Sleep for interval
                sleep_time = 0
                while sleep_time < interval and self.running:
                    time.sleep(1)
                    sleep_time += 1
                    
        except KeyboardInterrupt:
            print("\n\n⏹️ Stopping...")
            self.stop()
        
        return True
    
    def stop(self):
        """Stop the application gracefully"""
        print("🛑 Stopping ZNQ Rejoin...")
        self.running = False
        print("✅ Stopped successfully")
    
    def run(self):
        """Main application entry point"""
        try:
            config = self.setup_configuration()
            if not config:
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

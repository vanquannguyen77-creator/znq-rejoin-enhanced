# 🚀 ZNQ Rejoin - Enhanced Roblox Auto-Rejoin Tool

[![Platform](https://img.shields.io/badge/Platform-Android%20%2F%20Termux-brightgreen)]()
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)]()
[![License](https://img.shields.io/badge/License-MIT-yellow)]()
[![Status](https://img.shields.io/badge/Status-Stable-success)]()

**ZNQ Rejoin** là công cụ tự động rejoin Roblox được tối ưu hóa cho Android/Termux với hiệu suất cao và độ ổn định tuyệt vời.

## ✨ Tính năng

- 🔄 **Auto Rejoin**: Tự động phát hiện và rejoin khi Roblox bị disconnect
- 📊 **System Monitoring**: Theo dõi CPU, RAM, battery, uptime realtime
- 🎨 **Beautiful Dashboard**: Giao diện terminal đẹp với Rich UI
- 🛡️ **Crash Protection**: Xử lý lỗi thông minh, không crash
- 🧵 **Multi-threading**: Hiệu suất cao với quản lý thread tối ưu
- 📱 **Android Optimized**: Tối ưu cho Android/Termux
- 🔒 **Safe Operations**: Database an toàn với backup tự động
- ⚡ **High Performance**: Caching thông minh, UI updates hiệu quả

## 📋 Yêu cầu hệ thống

- **Android 7.0+**
- **Termux app** (từ F-Droid hoặc GitHub)
- **Python 3.8+**
- **Root access** (khuyến nghị)
- **2GB RAM** trở lên

## 🚀 Cài đặt nhanh (1 lệnh)

```bash
curl -sL https://raw.githubusercontent.com/[YOUR-USERNAME]/[REPO-NAME]/main/setup.sh | bash
```

## 📦 Cài đặt thủ công

### Bước 1: Clone repository
```bash
git clone https://github.com/[YOUR-USERNAME]/[REPO-NAME].git
cd [REPO-NAME]
```

### Bước 2: Chạy setup script
```bash
chmod +x setup.sh
./setup.sh
```

### Bước 3: Chạy tool
```bash
# Chế độ thường
./run-znq.sh

# Chế độ root (khuyến nghị)
./run-znq.sh --root
```

## ⚙️ Cài đặt dependencies từ requirements

```bash
# Cài đặt từ requirements.txt
pip install -r requirements.txt

# Hoặc cài đặt thủ công
pkg install python python-pip termux-api tsu
pip install psutil requests rich prettytable colorama
```

## 🎮 Hướng dẫn sử dụng

### Lần đầu chạy
1. Chạy tool: `python znq-rejoin.py`
2. Nhập **Place ID** của game Roblox
3. Chọn package Roblox (mặc định: com.roblox.client)
4. Cấu hình interval (khuyến nghị: 60s)
5. Tool sẽ tự động bắt đầu monitoring

### Dashboard
```
╔══════════════════════════════════════════════════════════════════════════════════╗
║                           ZNQ Enhanced Rejoin Monitor                           ║
║Ngày: 15/12/2024                                            Uptime: 02h15m30s║
╠══════════════════════════════════════════════════════════════════════════════════╣
║         CPU: 15.2% | RAM: 45.8% | Battery: 85% | Running: 1/1         ║
╠══════════════════════════════════════════════════════════════════════════════════╣
║Package               | Status     | Info                    | Time      ║
╟──────────────────────┼────────────┼─────────────────────────┼───────────╢
║com.roblox.client     | Running    | Đang hoạt động (Cycle #42) | 14:30:15  ║
╟Nhấn Ctrl+C để dừng | ZNQ Enhanced                                      ╢
╚══════════════════════════════════════════════════════════════════════════════════╝
```

## 📁 Cấu trúc file

```
znq-rejoin/
├── znq-rejoin.py       # Main application
├── setup.sh            # Auto setup script
├── run-znq.sh          # Launcher script
├── uninstall-znq.sh    # Uninstaller
├── requirements.txt    # Python dependencies
├── README.md           # Documentation
└── roblox_config.json  # Configuration file (auto-generated)
```

## ⚠️ Troubleshooting

### Lỗi thường gặp

**1. Permission Denied**
```bash
chmod +x setup.sh run-znq.sh znq-rejoin.py
termux-setup-storage
```

**2. Python module not found**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**3. Can't detect Roblox process**
```bash
# Chạy với root
tsu -c "python znq-rejoin.py"
```

**4. Database locked**
```bash
# Kill tất cả process Roblox
pkill -f roblox
```

### Performance Issues

**High CPU usage:**
- Tăng interval lên 120s+
- Giảm số package monitoring

**Memory leaks:**
- Restart tool mỗi 24h
- Check background processes: `ps aux | grep python`

## 🔧 Configuration

File config tự động được tạo tại `roblox_config.json`:

```json
{
    "packages": ["com.roblox.client"],
    "place_id": "2753915549", 
    "interval": 60,
    "pulse_delay": 2,
    "rejoin_every": 5,
    "auto_clear_cache": {
        "enabled": false,
        "minutes": 30,
        "packages": []
    },
    "webhook_heartbeat_minutes": 0,
    "discord_webhook": ""
}
```

## 🔄 Updates

### Update tool
```bash
git pull origin main
chmod +x setup.sh
./setup.sh
```

### Update dependencies
```bash
pip install --upgrade -r requirements.txt
```

## 🗑️ Gỡ cài đặt

```bash
./uninstall-znq.sh
```

## 🐛 Bug Report

Nếu gặp lỗi, hãy tạo issue với thông tin:

- **Device**: Model + Android version
- **Termux version**
- **Python version**: `python --version`
- **Error log**: Copy full error message
- **Steps to reproduce**

## 🤝 Đóng góp

1. Fork repository
2. Tạo feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push branch: `git push origin feature/amazing-feature`
5. Tạo Pull Request

## 📄 License

Distributed under MIT License. See `LICENSE` for more information.

## 👏 Credits

- **Original concept**: Based on community rejoin tools
- **Enhanced by**: ZNQ Team
- **Special thanks**: Roblox community, Termux developers

## 📞 Support

- **GitHub Issues**: [Create issue](https://github.com/[YOUR-USERNAME]/[REPO-NAME]/issues)
- **Discord**: [Join server](https://discord.gg/your-server)
- **Email**: support@znq.dev

---

<div align="center">

**⭐ Star this repo if it helped you! ⭐**

Made with ❤️ by ZNQ Team

</div>

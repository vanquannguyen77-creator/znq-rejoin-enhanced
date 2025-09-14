# 📤 Hướng dẫn Upload lên GitHub

## 🚀 **Cách 1: Upload qua GitHub Web Interface (Dễ nhất)**

### Bước 1: Tạo Repository mới
1. Đăng nhập **GitHub.com**
2. Click **"New repository"** hoặc **"+"** → **"New repository"**
3. Đặt tên repo: `znq-rejoin` (hoặc tên bạn muốn)
4. Chọn **"Public"** hoặc **"Private"**
5. ✅ Check **"Add a README file"**
6. Click **"Create repository"**

### Bước 2: Upload files
1. Trong repo vừa tạo, click **"uploading an existing file"**
2. Kéo thả hoặc chọn **tất cả files:**
   - `znq-rejoin.py`
   - `setup.sh` 
   - `run-znq.sh`
   - `requirements.txt`
   - `README.md`
3. Viết commit message: `"Add ZNQ Rejoin Enhanced v1.0"`
4. Click **"Commit changes"**

✅ **Xong! Repo đã sẵn sàng**

---

## ⚡ **Cách 2: Upload qua Git Commands (Nâng cao)**

### Bước 1: Tạo repo trên GitHub (như Cách 1)

### Bước 2: Clone và upload
```bash
# Clone repo về máy
git clone https://github.com/YOUR-USERNAME/REPO-NAME.git
cd REPO-NAME

# Copy tất cả files vào thư mục
cp ../znq-rejoin.py .
cp ../setup.sh .
cp ../run-znq.sh .
cp ../requirements.txt .
cp ../README.md .

# Phân quyền execute
chmod +x setup.sh run-znq.sh znq-rejoin.py

# Add files
git add .

# Commit
git commit -m "Add ZNQ Rejoin Enhanced v1.0

- Complete rejoin automation tool
- Android/Termux optimized
- Enhanced error handling
- Beautiful dashboard UI
- Auto setup script included"

# Push lên GitHub
git push origin main
```

---

## 🛠️ **Cách 3: Upload từ Termux (Cho pro)**

### Bước 1: Cài Git trên Termux
```bash
pkg install git
```

### Bước 2: Cấu hình Git
```bash
git config --global user.name "YOUR-NAME"
git config --global user.email "your-email@gmail.com"
```

### Bước 3: Clone và upload
```bash
# Clone repo
git clone https://github.com/YOUR-USERNAME/REPO-NAME.git
cd REPO-NAME

# Copy files (assuming trong cùng thư mục)
cp ../znq-rejoin.py .
cp ../setup.sh .
cp ../run-znq.sh .
cp ../requirements.txt .
cp ../README.md .

# Phân quyền
chmod +x *.sh *.py

# Git commands
git add .
git commit -m "Add ZNQ Rejoin Enhanced - Complete automation tool"
git push origin main
```

---

## 📋 **Checklist trước khi upload:**

- [ ] `znq-rejoin.py` - Main application
- [ ] `setup.sh` - Auto setup script  
- [ ] `run-znq.sh` - Launcher script
- [ ] `requirements.txt` - Python dependencies
- [ ] `README.md` - Documentation
- [ ] `upload-to-github.md` - This guide (optional)

---

## 🎯 **Sau khi upload xong:**

### Tạo Release
1. Vào repo → **"Releases"** → **"Create new release"**
2. Tag version: `v1.0.0`
3. Release title: `"ZNQ Rejoin Enhanced v1.0 - Stable Release"`
4. Description:
```markdown
🚀 **ZNQ Rejoin Enhanced v1.0**

Complete Roblox auto-rejoin tool optimized for Android/Termux

**New Features:**
- ✅ Enhanced stability and error handling
- ✅ Beautiful dashboard UI with real-time monitoring
- ✅ Smart process detection (Android compatible)
- ✅ Safe database operations with backup
- ✅ Managed threading with graceful shutdown
- ✅ Auto setup script for easy installation

**Installation:**
```bash
curl -sL https://raw.githubusercontent.com/YOUR-USERNAME/REPO-NAME/main/setup.sh | bash
```

**Quick Start:**
```bash
./run-znq.sh --root
```
```

5. Click **"Publish release"**

### Update README links
Sửa các link `[YOUR-USERNAME]` và `[REPO-NAME]` trong README.md thành thông tin thực của bạn.

---

## 🌟 **Lệnh cài đặt 1 click cho users:**

Sau khi upload, users có thể cài đặt bằng:

```bash
# Download và chạy setup
curl -sL https://raw.githubusercontent.com/YOUR-USERNAME/REPO-NAME/main/setup.sh | bash

# Hoặc clone repo
git clone https://github.com/YOUR-USERNAME/REPO-NAME.git
cd REPO-NAME
chmod +x setup.sh
./setup.sh
```

---

## ✨ **Bonus: Tạo GitHub Actions (Tùy chọn)**

Tạo file `.github/workflows/test.yml`:

```yaml
name: Test ZNQ Rejoin

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: '3.8'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    - name: Test syntax
      run: |
        python -m py_compile znq-rejoin.py
        echo "✅ Syntax check passed!"
```

---

**🎉 Hoàn tất! Repo của bạn giờ đã professional và sẵn sàng cho community!**

# 🔐 GitHub Authentication Setup Guide

Để upload code lên GitHub, **BẮT BUỘC** phải authentication. Đây là hướng dẫn chi tiết:

## 🚀 **Cách 1: GitHub CLI (DỄ NHẤT - Khuyên dùng)**

### **Cài đặt GitHub CLI:**
```bash
# Trên Termux Android:
pkg install gh

# Trên Ubuntu/Debian:
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo gpg --dearmor -o /usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update && sudo apt install gh
```

### **Đăng nhập:**
```bash
gh auth login
```

**Chọn:**
- `GitHub.com`
- `HTTPS`
- `Yes` (authenticate Git with GitHub credentials)
- `Login with a web browser`

**Sau đó:** Copy device code → Mở browser → Paste code → Authorize

✅ **Xong! Giờ có thể push code tự động**

---

## 🔑 **Cách 2: Personal Access Token**

### **Bước 1: Tạo Token**
1. Đăng nhập **GitHub.com**
2. Vào **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
3. Click **"Generate new token (classic)"**
4. **Note:** `ZNQ Rejoin Upload`
5. **Expiration:** `90 days` (hoặc `No expiration`)
6. **Scopes:** ✅ Check `repo` (full control)
7. Click **"Generate token"**
8. **⚠️ COPY TOKEN NGAY** (chỉ hiển thị 1 lần!)

### **Bước 2: Sử dụng Token**
```bash
# Configure git
git config --global user.name "Your GitHub Username"
git config --global user.email "your-email@example.com"

# Khi git push, nhập:
# Username: your-github-username
# Password: ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx (your token)
```

### **Bước 3: Store Token (Optional)**
```bash
# Lưu credentials để không phải nhập lại
git config --global credential.helper store

# Hoặc cache trong 1 giờ
git config --global credential.helper 'cache --timeout=3600'
```

---

## 🔐 **Cách 3: SSH Keys (CHO PRO)**

### **Bước 1: Tạo SSH Key**
```bash
# Tạo SSH key
ssh-keygen -t ed25519 -C "your-email@example.com"

# Nhấn Enter cho mọi prompt (dùng default)
```

### **Bước 2: Copy Public Key**
```bash
# Copy public key
cat ~/.ssh/id_ed25519.pub

# Output sẽ như này:
# ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIxxxxx your-email@example.com
```

### **Bước 3: Add Key vào GitHub**
1. Đăng nhập **GitHub.com**
2. **Settings** → **SSH and GPG keys**
3. Click **"New SSH key"**
4. **Title:** `Termux Device` (hoặc tên bạn muốn)
5. **Key:** Paste public key đã copy
6. Click **"Add SSH key"**

### **Bước 4: Test Connection**
```bash
ssh -T git@github.com
# Should output: Hi username! You've successfully authenticated...
```

### **Bước 5: Use SSH URLs**
```bash
# Clone bằng SSH thay vì HTTPS
git clone git@github.com:username/repo.git

# Hoặc change existing repo
git remote set-url origin git@github.com:username/repo.git
```

---

## ✅ **Kiểm tra Authentication**

### **Test GitHub CLI:**
```bash
gh auth status
# Should show: Logged in to github.com as username
```

### **Test Git Push:**
```bash
# Tạo test repo
mkdir test-auth && cd test-auth
git init
echo "# Test" >> README.md
git add . && git commit -m "test"
git remote add origin https://github.com/username/test-repo.git
git push -u origin main
```

### **Test SSH:**
```bash
ssh -T git@github.com
```

---

## 🔧 **Troubleshooting**

### **❌ "Authentication failed"**
- Check username/password chính xác
- Nếu dùng 2FA, phải dùng Personal Access Token thay password
- Token phải có quyền `repo`

### **❌ "Permission denied (publickey)"**
- SSH key chưa add vào GitHub
- SSH agent chưa running: `eval $(ssh-agent -s)`
- Add key: `ssh-add ~/.ssh/id_ed25519`

### **❌ "remote: Repository not found"**
- Repository chưa tồn tại trên GitHub  
- Username/repository name sai
- Không có quyền access repository

### **❌ GitHub CLI không hoạt động**
```bash
# Re-authenticate
gh auth logout
gh auth login

# Check version
gh --version
```

---

## 🎯 **KHUYẾN NGHỊ:**

### **Cho Beginners:**
🟢 **GitHub CLI** - Dễ nhất, tự động handle mọi thứ

### **Cho Developers:**
🟡 **Personal Access Token** - Linh hoạt, work với mọi tool

### **Cho Advanced Users:**
🔵 **SSH Keys** - An toàn nhất, không expire

---

## 🚀 **Sau khi setup authentication:**

```bash
# Chạy auto upload script
chmod +x auto-upload-github.sh
./auto-upload-github.sh
```

**Script sẽ tự động:**
- ✅ Detect authentication method
- ✅ Tạo repository (nếu có GitHub CLI)
- ✅ Configure git
- ✅ Commit và push code
- ✅ Tạo release

---

**🔐 Authentication là bước đầu tiên và quan trọng nhất!**

Chọn 1 trong 3 cách trên, setup xong rồi chạy script upload! 🚀

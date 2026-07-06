# ⚡ Quick Fix Guide - Get Business-Specific Images

## 🎯 Problem
Images are **random** instead of **business-specific**

## ✅ Solution (2 Minutes)

### 1️⃣ Get FREE API Key
**Go to:** https://www.pexels.com/api/  
**Sign up** → **Copy API key**

### 2️⃣ Add to .env File
```bash
# File: seo-automation/backend/.env
# Line: PEXELS_API_KEY=

# Change to:
PEXELS_API_KEY=your_key_here
```

### 3️⃣ Restart Backend
```bash
cd seo-automation/backend
python3 -m uvicorn main:app --reload
```

### 4️⃣ Test
```bash
python3 test_pexels.py
```

**Expected:**
```
✅ Pexels API Key: FOUND
✅ SUCCESS: Got Pexels image!
🎉 All images from Pexels!
```

## 🎉 Done!

Now when you generate content:
- Software Engineer → 💻 Real developer images
- Plumbing → 🔧 Real plumber images
- Yoga → 🧘 Real yoga instructor images

---

**Time:** 2 minutes  
**Cost:** FREE  
**Impact:** Professional business-specific images ✨

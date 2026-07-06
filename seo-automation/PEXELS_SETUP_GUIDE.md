# 🎯 Pexels API Setup Guide - Get Business-Specific Images!

## Why You Need This

**Without Pexels API Key:**
- ❌ Random unrelated images (mountains, beaches, etc.)
- ❌ Software Engineer → Random landscape photo
- ❌ Plumbing → Random nature photo
- ❌ NOT professional or business-specific

**With Pexels API Key:**
- ✅ Real software engineer images for software engineering
- ✅ Real plumber images for plumbing
- ✅ Real yoga instructor images for yoga
- ✅ Professional, business-specific photos

---

## 📝 Step-by-Step Setup (2 Minutes)

### Step 1: Go to Pexels API Website

**Click this link:** https://www.pexels.com/api/

### Step 2: Click "Get Started"

You'll see a big button that says **"Get Started"** - click it!

### Step 3: Sign Up (FREE)

Choose one:
- **Sign up with Email** (enter your email + password)
- **Sign up with Google** (faster - just click and done!)

**Important**: It's completely FREE - no credit card needed!

### Step 4: Verify Email (if using email signup)

- Check your inbox
- Click the verification link
- Come back to Pexels

### Step 5: Get Your API Key

After signing up, you'll see your API key immediately on the page!

It looks like this:
```
563492ad6f91700001000001abc123def456789
```

**Copy this entire key!**

### Step 6: Add to .env File

1. Open this file: `seo-automation/backend/.env`

2. Find line 18 (it says `PEXELS_API_KEY=`)

3. Paste your key after the `=`:
```bash
PEXELS_API_KEY=563492ad6f91700001000001abc123def456789
```

4. **Save the file!**

### Step 7: Backend Auto-Reloads

The backend will automatically restart (wait 2-3 seconds).

You'll see in the backend terminal:
```
WARNING: WatchFiles detected changes in '.env'. Reloading...
```

### Step 8: Test It!

Run the test script:
```bash
cd seo-automation/backend
python3 test_pexels.py
```

You should see:
```
✅ Pexels API Key: FOUND
✅ Software Engineer → Real developer images!
✅ Plumbing → Real plumber images!
```

---

## 🧪 Test Cases

After adding your API key, test these business types:

### Test 1: Software Engineer
```
Business Type: Software Engineer
Locations: San Diego, La Jolla, Chula Vista
Expected: Real images of developers coding on laptops
```

### Test 2: Plumbing
```
Business Type: Plumbing
Locations: San Diego, La Jolla, Chula Vista
Expected: Real images of plumbers working with pipes
```

### Test 3: Yoga Instructor
```
Business Type: Yoga
Locations: San Diego, La Jolla, Chula Vista
Expected: Real images of yoga instructors in studios
```

### Test 4: Restaurant
```
Business Type: Restaurant
Locations: San Diego, La Jolla, Chula Vista
Expected: Real images of chefs in kitchens
```

### Test 5: Marketing
```
Business Type: Marketing
Locations: San Diego, La Jolla, Chula Vista
Expected: Real images of marketing professionals
```

---

## 🔍 How to Verify It's Working

### Check Backend Logs

After generating content, look at your backend terminal:

**✅ SUCCESS (With API Key):**
```
[Image] 🔍 Searching Pexels for: 'software developer coding laptop'
[Image] ✅ Found 15 images, selected #3
[Image] 📸 URL: https://images.pexels.com/photos/...
```

**❌ NO API KEY:**
```
[Image] ⚠️  No Pexels API key - using random fallback images
[Image] 💡 Get FREE Pexels API key at: https://www.pexels.com/api/
```

**❌ INVALID API KEY:**
```
[Image] ❌ Pexels API error: 401
[Image] 🔑 Invalid API key - check your PEXELS_API_KEY in .env
```

### Check Frontend

1. Go to: http://localhost:5173/simple
2. Generate "Software Engineer" content
3. Look at the images:
   - **With API key**: Real developers coding ✅
   - **Without API key**: Random landscapes ❌

---

## 🆘 Troubleshooting

### Problem: "Can't find API key after signing up"

**Solution:**
1. Go to: https://www.pexels.com/api/
2. Log in to your account
3. Look for "Your API Key" section
4. Copy the key

### Problem: "Backend logs show 401 error"

**Solution:**
- Your API key is invalid or incorrect
- Make sure you copied the ENTIRE key
- No spaces before or after the key
- Get a new key from https://www.pexels.com/api/

### Problem: "Still seeing random images"

**Solution:**
1. Check `.env` file - is the key there?
2. Restart backend manually:
   ```bash
   # Stop backend (Ctrl+C)
   cd seo-automation/backend
   python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```
3. Clear browser cache (Ctrl+Shift+R)
4. Generate new content

### Problem: "Backend not reloading after saving .env"

**Solution:**
Manually restart:
```bash
# In backend terminal, press Ctrl+C to stop
# Then start again:
cd seo-automation/backend
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## 📊 Pexels API Limits (FREE Tier)

- **200 requests per hour** (plenty for testing!)
- **20,000 requests per month** (very generous!)
- **No credit card required**
- **Commercial use allowed**
- **High-quality images**

### How Many Pages Can You Generate?

- Each page = 1 API request
- You can generate **200 pages per hour**
- Or **20,000 pages per month**
- More than enough for any business!

---

## ✅ Quick Checklist

- [ ] Go to https://www.pexels.com/api/
- [ ] Click "Get Started"
- [ ] Sign up (FREE)
- [ ] Copy your API key
- [ ] Open `seo-automation/backend/.env`
- [ ] Find `PEXELS_API_KEY=`
- [ ] Paste your key: `PEXELS_API_KEY=your_key_here`
- [ ] Save file
- [ ] Wait 2-3 seconds for backend to reload
- [ ] Run test: `python3 test_pexels.py`
- [ ] Generate content and see real images! 🎉

---

## 🎯 What You'll Get

### Before (No API Key):
```
Software Engineer → 🏔️ Random mountain photo
Plumbing → 🌊 Random beach photo
Yoga → 🌲 Random forest photo
```

### After (With API Key):
```
Software Engineer → 💻 Real developer coding
Plumbing → 🔧 Real plumber with pipes
Yoga → 🧘 Real yoga instructor in studio
```

---

## 🚀 Ready to Start?

**Click here to get your FREE API key:**
👉 **https://www.pexels.com/api/**

**Total time: 2 minutes**
**Total cost: $0 (FREE forever!)**
**Result: Professional business-specific images!** 🎉

---

## 💡 Pro Tips

1. **Save your API key** - Store it somewhere safe
2. **Don't share it** - It's personal to your account
3. **Check usage** - Go to https://www.pexels.com/api/ to see your usage stats
4. **Need more?** - 20,000/month is usually more than enough, but you can contact Pexels for higher limits

---

## ❓ Questions?

**Q: Is it really free?**
A: Yes! Completely free, no credit card needed.

**Q: Will it expire?**
A: No, your API key works forever (unless you delete your account).

**Q: Can I use it commercially?**
A: Yes! Pexels allows commercial use.

**Q: What if I hit the limit?**
A: 20,000/month is very generous. If you need more, contact Pexels.

**Q: Do I need to credit Pexels?**
A: Not required, but appreciated!

---

**Get your FREE API key now and see real business-specific images!** 🚀

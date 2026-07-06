# Pexels API Setup - Get Business-Specific Images! 📸

## Why Pexels?
Pexels provides **FREE, high-quality, business-specific images** that match your content:
- ✅ Plumbing images for plumbing services
- ✅ Electrician images for electrical services
- ✅ HVAC images for HVAC services
- ✅ And 20+ more business types!

## How to Get Your FREE Pexels API Key

### Step 1: Create a Pexels Account
1. Go to: **https://www.pexels.com/**
2. Click **"Join"** in the top right
3. Sign up with your email or Google account (FREE!)

### Step 2: Get Your API Key
1. Once logged in, go to: **https://www.pexels.com/api/**
2. Click **"Get Started"** or **"Your API Key"**
3. You'll see your API key immediately - it looks like:
   ```
   YOUR_API_KEY_HERE_1234567890abcdef
   ```
4. **Copy this key!**

### Step 3: Add API Key to Your .env File
1. Open: `seo-automation/backend/.env`
2. Find the line that says:
   ```
   PEXELS_API_KEY=
   ```
3. Paste your API key after the `=`:
   ```
   PEXELS_API_KEY=YOUR_API_KEY_HERE_1234567890abcdef
   ```
4. **Save the file**

### Step 4: Restart the Backend
The backend needs to reload to pick up the new API key:

**Option A: If backend is running with --reload (it should auto-restart)**
- Just wait 2-3 seconds, it will reload automatically

**Option B: Manual restart**
```bash
# Stop the backend (Ctrl+C in the terminal)
# Then start it again:
cd seo-automation/backend
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Step 5: Test It!
1. Go to: http://localhost:5173/simple
2. Generate content (e.g., "Plumbing" in "San Diego, La Jolla, Chula Vista")
3. **You should now see REAL plumbing images!** 🎉

---

## What You'll Get

### With Pexels API Key (Recommended)
- ✅ **Real business-specific images**
- ✅ Plumber images for plumbing
- ✅ Electrician images for electrical work
- ✅ HVAC technician images for HVAC
- ✅ High-quality professional photos
- ✅ Consistent images (same business + city = same image)

### Without Pexels API Key (Fallback)
- ⚠️ Generic random photos from Picsum
- ⚠️ Not business-specific
- ⚠️ Less professional looking

---

## Supported Business Types

The system has specific image searches for:

1. **Home Services**:
   - Plumbing → Plumber working with pipes
   - Electrician → Electrician with wiring
   - HVAC → Air conditioning technician
   - Roofing → Roofer on construction site
   - Painting → House painter painting
   - Cleaning → Professional cleaning service
   - Pest Control → Exterminator at work
   - Locksmith → Locksmith with keys

2. **Professional Services**:
   - Web Design → Web designer with laptop
   - Marketing → Digital marketing workspace
   - Accounting → Accountant with calculator
   - Legal → Lawyer in office
   - Photography → Professional photographer

3. **Health & Wellness**:
   - Dental → Dentist in clinic
   - Medical → Doctor in medical clinic
   - Fitness → Gym and fitness training
   - Salon → Hair salon and beauty

4. **Business Services**:
   - Restaurant → Restaurant kitchen and food
   - Retail → Retail store shopping
   - Auto Repair → Car mechanic working
   - Carpentry → Carpenter with woodworking tools
   - Flooring → Flooring installation
   - Moving → Moving truck and movers
   - Catering → Catering food service

---

## Pexels API Limits (FREE Tier)

- **200 requests per hour** (more than enough!)
- **20,000 requests per month** (very generous!)
- **Unlimited image downloads**
- **No credit card required**
- **Commercial use allowed**

### How Many Images Can You Generate?
- If you generate 10 pages at once, that's 10 API requests
- You can generate **200 pages per hour** or **20,000 pages per month**
- More than enough for any business! 🚀

---

## Troubleshooting

### Images Still Look Random?
1. **Check if API key is set**: Open `.env` and verify `PEXELS_API_KEY=` has a value
2. **Restart backend**: Stop and start the backend server
3. **Check logs**: Look for `[Image] Pexels API:` messages in backend terminal
4. **Verify API key works**: Go to https://www.pexels.com/api/ and check your key status

### Backend Logs Show "No API key"?
```
[Image] Pexels API: No API key configured, using fallback
```
- This means the `.env` file doesn't have the API key
- Follow Step 3 above to add it

### Backend Logs Show "Pexels API error: 401"?
```
[Image] Pexels API error: 401, using fallback
```
- This means the API key is invalid
- Get a new API key from https://www.pexels.com/api/
- Make sure you copied the entire key (no spaces)

### Backend Logs Show "Found X images"?
```
[Image] Pexels API: Found 15 images for 'plumber working pipes', selected #3
```
- ✅ **This is good!** It means Pexels API is working!
- You should see real plumbing images now

---

## Alternative: Use Without API Key

If you don't want to set up Pexels (not recommended):
- The system will automatically fall back to Picsum Photos
- You'll get generic random images (not business-specific)
- Images will still be consistent per business + city
- But they won't match your business type

---

## Summary

1. **Get FREE Pexels API key**: https://www.pexels.com/api/
2. **Add to .env file**: `PEXELS_API_KEY=your_key_here`
3. **Restart backend**: Wait for auto-reload or restart manually
4. **Generate content**: See real business-specific images! 🎉

**Total time: 2-3 minutes** ⏱️

---

## Questions?

- **Pexels API Docs**: https://www.pexels.com/api/documentation/
- **Pexels Support**: https://help.pexels.com/
- **Check your API usage**: https://www.pexels.com/api/ (shows requests used)

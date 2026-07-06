# 🎯 Pexels API Setup - Complete Guide

## ✅ Test Results Summary

**Date:** April 29, 2026  
**Status:** All tests PASSED ✅ (but using fallback images)

### Test Results:
```
✅ PASSED - Image Generation (5/5)
✅ PASSED - Location Service (2/2)
✅ PASSED - Content Generation (2/2)
✅ PASSED - Image Consistency (3/3)
✅ PASSED - Image Variety (3/3)

🎯 Overall: 5/5 tests passed
```

## ⚠️ Current Situation

**The system is working, BUT:**
- ❌ Images are **RANDOM** (Lorem Picsum fallback)
- ❌ Images are **NOT business-specific**
- ❌ "Software Engineer" shows random landscape photos
- ❌ "Plumbing" shows random abstract photos
- ❌ "Yoga" shows random nature photos

**Why?** Because `PEXELS_API_KEY` is not set in `.env` file.

## 🎯 The Solution: Add Pexels API Key (FREE)

### Step 1: Get FREE Pexels API Key (2 minutes)

1. **Go to:** https://www.pexels.com/api/
2. **Click:** "Get Started" or "Sign Up"
3. **Create account** (email + password)
4. **Verify email** (check inbox)
5. **Go to:** https://www.pexels.com/api/new/
6. **Copy your API key** (looks like: `abc123xyz456...`)

### Step 2: Add API Key to .env File

1. **Open:** `seo-automation/backend/.env`
2. **Find line:** `PEXELS_API_KEY=`
3. **Add your key:** `PEXELS_API_KEY=abc123xyz456...`
4. **Save file**

**Example:**
```bash
# Before:
PEXELS_API_KEY=

# After:
PEXELS_API_KEY=abc123xyz456def789ghi012jkl345mno678pqr901stu234
```

### Step 3: Restart Backend

```bash
cd seo-automation/backend
python3 -m uvicorn main:app --reload
```

### Step 4: Run Tests Again

```bash
cd seo-automation/backend
python3 test_pexels.py
```

**Expected output:**
```
✅ Pexels API Key: FOUND
🔍 Testing: Software Engineer in San Diego
   ✅ SUCCESS: Got Pexels image!
   📸 URL: https://images.pexels.com/photos/...
```

## 🎉 What You'll Get After Adding API Key

### Before (Random Images):
- Software Engineer → Random landscape photo 🏔️
- Plumbing → Random abstract photo 🎨
- Yoga → Random nature photo 🌲

### After (Business-Specific Images):
- Software Engineer → Real developer coding on laptop 💻
- Plumbing → Real plumber working with pipes 🔧
- Yoga → Real yoga instructor in studio 🧘

## 📊 Technical Details

### Current Implementation Status:

✅ **Code is ready:**
- `content_service.py` has Pexels API integration
- 25+ business type mappings configured
- Consistent image selection (same business+city = same image)
- Graceful fallback to Lorem Picsum if no API key

✅ **Tests are ready:**
- `test_pexels.py` - Pexels API verification
- `test_full_system.py` - Comprehensive system tests

❌ **Missing:**
- Pexels API key in `.env` file

### Business Type Mappings:

The system has pre-configured search queries for:
- **Tech:** Software Engineer, Web Design, App Development, IT Support
- **Home Services:** Plumbing, Electrician, HVAC, Roofing, Carpentry
- **Professional:** Marketing, Accounting, Legal, Consulting, Real Estate
- **Health:** Dental, Medical, Fitness, Yoga, Salon
- **Business:** Restaurant, Catering, Retail, Auto Repair, Photography

### How It Works:

1. **User enters:** "Software Engineer" + "San Diego"
2. **System searches Pexels for:** "software developer coding laptop"
3. **Pexels returns:** 15 real photos of developers
4. **System selects:** Consistent image based on hash(business+city)
5. **Result:** Same business+city always gets same professional image

## 🚀 Quick Start (After Adding API Key)

### Test in Terminal:
```bash
cd seo-automation/backend
python3 test_pexels.py
```

### Test in Browser:
1. Go to: http://localhost:5173/simple
2. Enter:
   - Business Type: **Software Engineer**
   - Locations: **San Diego, CA**
   - Number of Pages: **1**
3. Click: **Generate SEO Content**
4. See: **Real developer image** (not random)

## 🔍 Troubleshooting

### Issue: "Invalid API key"
**Solution:** 
- Check for spaces in `.env` file
- Make sure key is on same line: `PEXELS_API_KEY=yourkey`
- No quotes needed

### Issue: "Still showing random images"
**Solution:**
- Restart backend: `Ctrl+C` then `python3 -m uvicorn main:app --reload`
- Clear browser cache: `Ctrl+Shift+R`
- Check `.env` file was saved

### Issue: "Pexels API is down"
**Solution:**
- System automatically falls back to Lorem Picsum
- Check Pexels status: https://status.pexels.com/

## 📝 API Key Limits (FREE Tier)

**Pexels FREE tier includes:**
- ✅ 200 requests per hour
- ✅ Unlimited total requests
- ✅ No credit card required
- ✅ Commercial use allowed
- ✅ No attribution required

**For this app:**
- Each page generation = 1 request
- 200 pages/hour = plenty for testing
- Production: Consider caching images

## 🎯 Next Steps

1. ✅ **Tests completed** - All 5/5 tests passed
2. ⏳ **Get Pexels API key** - https://www.pexels.com/api/
3. ⏳ **Add key to .env** - `PEXELS_API_KEY=your_key`
4. ⏳ **Restart backend** - `python3 -m uvicorn main:app --reload`
5. ⏳ **Run tests again** - `python3 test_pexels.py`
6. ⏳ **Test in browser** - Generate content and see real images!

## 📞 Support

**If you need help:**
1. Check this guide first
2. Run `python3 test_pexels.py` to diagnose
3. Check backend logs for error messages
4. Verify `.env` file has correct format

---

**Last Updated:** April 29, 2026  
**Status:** Ready for Pexels API key ✅  
**Tests:** 5/5 Passed ✅  
**Next:** Add API key to get business-specific images 🎯

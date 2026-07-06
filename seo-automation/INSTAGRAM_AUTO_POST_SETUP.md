# 🤖 Instagram Auto-Posting Setup Guide

## ✅ Feature Implemented!

Your SEO tool now supports **automatic posting to Instagram**! 

When you click the Instagram button, you'll get a choice:
- **Auto-post** (if configured) - Posts directly to Instagram
- **Manual post** (fallback) - Downloads image + copies caption

## 📋 Requirements for Auto-Posting

To enable automatic Instagram posting, you need:

1. ✅ **Instagram Business Account** (not personal account)
2. ✅ **Facebook Page** connected to your Instagram
3. ✅ **Facebook App** with Instagram permissions
4. ✅ **Access Token** with posting permissions

## 🚀 Setup Steps

### Step 1: Convert to Instagram Business Account

1. Open Instagram app on your phone
2. Go to **Settings** → **Account**
3. Tap **Switch to Professional Account**
4. Choose **Business**
5. Connect to your Facebook Page (create one if needed)

### Step 2: Create Facebook App

1. Go to https://developers.facebook.com/
2. Click **My Apps** → **Create App**
3. Choose **Business** type
4. Fill in app details:
   - **App Name**: "SEO Automation Tool"
   - **Contact Email**: zeorbitsd@gmail.com
5. Click **Create App**

### Step 3: Add Instagram Product

1. In your Facebook App dashboard
2. Click **Add Product**
3. Find **Instagram** → Click **Set Up**
4. Follow the setup wizard

### Step 4: Get Access Token

1. In Facebook App dashboard, go to **Tools** → **Graph API Explorer**
2. Select your app from dropdown
3. Click **Generate Access Token**
4. Select permissions:
   - `instagram_basic`
   - `instagram_content_publish`
   - `pages_read_engagement`
5. Click **Generate Token**
6. **Copy the token** (you'll need it!)

### Step 5: Get Instagram Account ID

1. Still in Graph API Explorer
2. In the query field, enter: `me/accounts`
3. Click **Submit**
4. Find your Facebook Page in the response
5. Copy the `id` value
6. Now query: `{page-id}?fields=instagram_business_account`
7. Copy the `instagram_business_account.id` value

### Step 6: Add Credentials to .env File

1. Open `seo-automation/backend/.env`
2. Add these lines:

```bash
# Instagram Auto-Posting
INSTAGRAM_ACCESS_TOKEN=your_access_token_here
INSTAGRAM_ACCOUNT_ID=your_instagram_business_account_id_here
```

3. Save the file
4. Restart the backend server

### Step 7: Test the Setup

1. Go to http://localhost:8000/api/instagram/status
2. You should see:
```json
{
  "configured": true,
  "has_access_token": true,
  "has_account_id": true,
  "message": "Instagram API is configured"
}
```

## 🎯 How to Use Auto-Posting

### In the SEO Tool:

1. Generate SEO content (as usual)
2. Click **"Share on Social Media"** on any page
3. Click **"📸 Post to Instagram"** button
4. Choose **"YES"** for auto-posting
5. Wait 2-3 seconds
6. See success message with Instagram post link!

### What Happens:

```
Click Button
    ↓
Confirm Auto-Post
    ↓
API sends image + caption to Instagram
    ↓
Instagram publishes post
    ↓
Success! Post is live
    ↓
Modal shows Instagram post link
```

## 🔄 Fallback to Manual Posting

If auto-posting is not configured or fails:

1. Tool automatically offers manual posting
2. Caption copies to clipboard
3. Image downloads to your computer
4. You manually post to Instagram (30 seconds)

## 🔒 Security Notes

### Access Token Security:
- ✅ Token stored in `.env` file (not in code)
- ✅ `.env` file is in `.gitignore` (not committed to Git)
- ✅ Token never exposed to frontend
- ✅ All API calls go through your backend

### Token Expiration:
- **Short-lived tokens**: Expire in 1 hour
- **Long-lived tokens**: Expire in 60 days
- **Solution**: Use long-lived tokens or implement token refresh

### To Get Long-Lived Token:

```bash
curl -X GET "https://graph.facebook.com/v18.0/oauth/access_token?grant_type=fb_exchange_token&client_id=YOUR_APP_ID&client_secret=YOUR_APP_SECRET&fb_exchange_token=YOUR_SHORT_LIVED_TOKEN"
```

## 📊 API Endpoints

### Check Configuration Status
```
GET http://localhost:8000/api/instagram/status
```

### Get Account Info
```
GET http://localhost:8000/api/instagram/account
```

### Post to Instagram
```
POST http://localhost:8000/api/instagram/post
Body: {
  "image_url": "https://...",
  "caption": "Your caption here"
}
```

## 🐛 Troubleshooting

### Error: "Instagram credentials not configured"
- **Solution**: Add `INSTAGRAM_ACCESS_TOKEN` and `INSTAGRAM_ACCOUNT_ID` to `.env`

### Error: "Invalid access token"
- **Solution**: Token expired. Generate a new long-lived token

### Error: "Image URL not accessible"
- **Solution**: Image must be publicly accessible. Unsplash images work fine!

### Error: "Permission denied"
- **Solution**: Make sure you selected `instagram_content_publish` permission

### Error: "Account not found"
- **Solution**: Double-check your `INSTAGRAM_ACCOUNT_ID` is correct

## 🎨 What Gets Posted

### Image:
- Business-specific image from Unsplash
- 1200x600px (optimized for Instagram)
- High quality, professional

### Caption Format:
```
[Business Title]

📍 [City], [State]

🔗 Link in bio

#BusinessType #CityName #LocalBusiness #SEO
```

### Example:
```
Best Plumbing in San Diego, CA | Affordable, Proven Results

📍 San Diego, California

🔗 Link in bio

#Plumbing #SanDiego #LocalBusiness #SEO
```

## 🌟 Benefits of Auto-Posting

✅ **Save Time**: Post in 2 seconds instead of 30 seconds
✅ **Consistency**: Never forget to post
✅ **Bulk Posting**: Generate 10 pages → Post all 10 to Instagram automatically
✅ **Scheduling**: Can be extended to schedule posts for later
✅ **Analytics**: Track which posts perform best

## 📱 Current Status

- ✅ Backend API implemented
- ✅ Frontend button with auto/manual choice
- ✅ Fallback to manual posting if not configured
- ✅ Error handling and user feedback
- ⏳ **Waiting for you to add credentials to `.env`**

## 🔧 Quick Setup Checklist

- [ ] Convert Instagram to Business account
- [ ] Create Facebook Page
- [ ] Create Facebook App
- [ ] Add Instagram product to app
- [ ] Generate access token with permissions
- [ ] Get Instagram Business Account ID
- [ ] Add credentials to `.env` file
- [ ] Restart backend server
- [ ] Test at http://localhost:8000/api/instagram/status
- [ ] Try auto-posting from the tool!

## 💡 Pro Tips

1. **Use Long-Lived Tokens**: They last 60 days instead of 1 hour
2. **Test First**: Try posting manually before bulk posting
3. **Check Image URLs**: Make sure images are publicly accessible
4. **Monitor Rate Limits**: Instagram has posting limits (25 posts/day for new accounts)
5. **Keep Token Secret**: Never share your access token

## 🎯 Next Steps

1. Follow the setup steps above
2. Add credentials to `.env`
3. Restart backend: `Ctrl+C` then `python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000`
4. Test the auto-posting feature!

---

**Need Help?**
- Facebook Developers: https://developers.facebook.com/docs/instagram-api
- Instagram Graph API: https://developers.facebook.com/docs/instagram-api/guides/content-publishing
- Your backend API docs: http://localhost:8000/docs

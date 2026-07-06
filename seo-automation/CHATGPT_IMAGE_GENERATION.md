# ChatGPT-Powered Image Search 🤖

## What Changed

Instead of using predefined image searches, the system now uses **ChatGPT (GPT-3.5-turbo)** to generate specific image search queries that match your content better!

## How It Works

### Old Way (Predefined)
```
Business Type: "Software Engineer"
Search Query: "software engineer coding laptop developer" (hardcoded)
Problem: Same search for all software engineers
```

### New Way (ChatGPT-Powered)
```
Business Type: "Software Engineer"
Location: "San Diego"

ChatGPT analyzes and generates:
→ "developer coding laptop office"

Business Type: "Yoga Instructor"
Location: "La Jolla"

ChatGPT analyzes and generates:
→ "yoga teacher class studio meditation"

Business Type: "Dog Walker"
Location: "Chula Vista"

ChatGPT analyzes and generates:
→ "dog walker park pets leash"
```

## Benefits

✅ **Better Matching**: Images match the actual business type better
✅ **Dynamic**: Works for ANY business type, not just predefined ones
✅ **Contextual**: Takes into account the specific business and location
✅ **Consistent**: Same business type gets similar (but not identical) searches
✅ **Smart**: ChatGPT understands nuances (e.g., "Life Coach" vs "Business Coach")

## Examples

| Business Type | ChatGPT Generates | Pexels Finds |
|--------------|-------------------|--------------|
| Software Engineer | "developer coding laptop office" | Real developers at work |
| Yoga Instructor | "yoga teacher class studio" | Real yoga instructors |
| Dog Walker | "dog walker park pets" | Real dog walkers |
| Life Coach | "life coach consultation meeting" | Real life coaches |
| Tattoo Artist | "tattoo artist tattooing studio" | Real tattoo artists |
| Personal Chef | "chef cooking kitchen professional" | Real chefs cooking |

## Setup Requirements

### 1. OpenAI API Key (For ChatGPT)

**Get FREE OpenAI API Key**:
1. Go to: https://platform.openai.com/api-keys
2. Sign up (FREE tier available)
3. Create API key
4. Copy the key

**Add to .env**:
```bash
# Open: seo-automation/backend/.env
# Find:
OPENAI_API_KEY=

# Change to:
OPENAI_API_KEY=sk-proj-...your_key_here...
```

### 2. Pexels API Key (For Images)

**Get FREE Pexels API Key**:
1. Go to: https://www.pexels.com/api/
2. Sign up (FREE)
3. Copy your API key

**Add to .env**:
```bash
# Find:
PEXELS_API_KEY=

# Change to:
PEXELS_API_KEY=your_pexels_key_here
```

### 3. Save and Reload

Save the `.env` file and the backend will auto-reload (wait 2-3 seconds).

## How It Works Technically

### Step 1: ChatGPT Generates Search Query
```python
# User enters: "Software Engineer" in "San Diego"

# ChatGPT prompt:
"Generate a short, specific image search query (3-5 words) for:
Business Type: Software Engineer
Location: San Diego

The query should describe what a professional in this field looks like at work."

# ChatGPT responds:
"developer coding laptop office"
```

### Step 2: Pexels Searches for Images
```python
# Search Pexels with ChatGPT's query
search_query = "developer coding laptop office"
results = pexels_api.search(search_query, per_page=15)

# Returns 15 relevant images of developers coding
```

### Step 3: Consistent Selection
```python
# Use hash to consistently select same image for same business+city
seed = hash("software engineer-san diego") % 15
selected_image = results[seed]

# Same business+city always gets same image
```

## Fallback System

The system has multiple fallback levels:

### Level 1: ChatGPT + Pexels (Best)
- Uses ChatGPT to generate search query
- Uses Pexels to find images
- **Result**: Perfect match, business-specific images

### Level 2: Simple + Pexels (Good)
- No OpenAI key, uses simple query: "{business_type} professional service work"
- Uses Pexels to find images
- **Result**: Good match, professional images

### Level 3: Picsum Photos (Fallback)
- No Pexels key, uses Picsum Photos
- **Result**: Random images, not business-specific

## Cost

### OpenAI API (ChatGPT)
- **Model**: GPT-3.5-turbo (cheapest)
- **Cost**: $0.0005 per 1K tokens (~$0.00001 per image query)
- **Example**: 1000 pages = $0.01 (1 cent!)
- **FREE Tier**: $5 credit for new accounts

### Pexels API
- **Cost**: FREE
- **Limits**: 200 requests/hour, 20,000/month
- **No credit card required**

### Total Cost
- **With FREE tiers**: $0 (completely free!)
- **After FREE tier**: ~$0.01 per 1000 pages (negligible)

## Backend Logs

### ✅ Success (With Both API Keys)
```
[Image] ChatGPT generated search query: 'developer coding laptop office'
[Image] Searching Pexels for: 'developer coding laptop office'
[Image] Pexels API: Found 15 images for 'developer coding laptop office', selected #3
[Image] Set image URL for Software Engineer in San Diego: https://images.pexels.com/photos/...
```

### ⚠️ No OpenAI Key (Still Works)
```
[Image] ChatGPT query generation failed: No API key
[Image] Searching Pexels for: 'software engineer professional service work'
[Image] Pexels API: Found 15 images for 'software engineer professional service work', selected #3
[Image] Set image URL for Software Engineer in San Diego: https://images.pexels.com/photos/...
```

### ❌ No Pexels Key (Fallback)
```
[Image] Set image URL for Software Engineer in San Diego: https://picsum.photos/seed/...
```

## Testing

### Test 1: With Both API Keys
```bash
# 1. Add both keys to .env:
OPENAI_API_KEY=sk-proj-...
PEXELS_API_KEY=...

# 2. Generate content:
Business Type: "Yoga Instructor"
Locations: "San Diego"

# 3. Check logs:
[Image] ChatGPT generated search query: 'yoga teacher class studio'
[Image] Pexels API: Found 15 images...

# 4. Result: Perfect yoga instructor images! ✅
```

### Test 2: Without OpenAI Key
```bash
# 1. Only Pexels key in .env:
OPENAI_API_KEY=
PEXELS_API_KEY=...

# 2. Generate content:
Business Type: "Yoga Instructor"

# 3. Check logs:
[Image] Searching Pexels for: 'yoga instructor professional service work'

# 4. Result: Good yoga images (not perfect, but good) ✅
```

### Test 3: No API Keys
```bash
# 1. No keys in .env:
OPENAI_API_KEY=
PEXELS_API_KEY=

# 2. Generate content:
Business Type: "Yoga Instructor"

# 3. Result: Random images (Picsum fallback) ⚠️
```

## Advantages Over Predefined List

### Old System (Predefined)
- ❌ Only works for 40 business types
- ❌ Same search for all similar businesses
- ❌ Can't handle variations (e.g., "Life Coach" vs "Business Coach")
- ❌ Requires manual updates for new business types

### New System (ChatGPT)
- ✅ Works for ANY business type
- ✅ Contextual searches based on business specifics
- ✅ Handles variations intelligently
- ✅ Automatically adapts to new business types
- ✅ Better image matching

## Summary

### What You Get

**With OpenAI + Pexels API Keys** (Recommended):
- 🎯 **Perfect Match**: ChatGPT generates specific search queries
- 🖼️ **Business-Specific Images**: Pexels finds exact matches
- 🚀 **Works for ANY Business Type**: No predefined list needed
- 💰 **Almost Free**: ~$0.01 per 1000 pages

**With Only Pexels API Key**:
- ✅ **Good Match**: Simple search queries
- 🖼️ **Professional Images**: Pexels finds related images
- 🚀 **Works for ANY Business Type**: Fallback queries
- 💰 **Completely Free**: No OpenAI costs

**With No API Keys**:
- ⚠️ **Random Images**: Picsum Photos fallback
- 📸 **Generic Photos**: Not business-specific
- 🆓 **Free**: But not ideal

### Recommendation

**Best Setup**:
1. Get FREE OpenAI API key ($5 credit for new accounts)
2. Get FREE Pexels API key (no credit card)
3. Add both to `.env`
4. Enjoy perfect image matching! 🎉

**Total Time**: 5 minutes
**Total Cost**: $0 (with free tiers)
**Result**: Perfect business-specific images for ANY business type!

---

## Quick Start

```bash
# 1. Get FREE API keys:
OpenAI: https://platform.openai.com/api-keys
Pexels: https://www.pexels.com/api/

# 2. Add to .env:
OPENAI_API_KEY=sk-proj-...
PEXELS_API_KEY=...

# 3. Save file (backend auto-reloads)

# 4. Generate content:
http://localhost:5173/simple

# 5. See perfect images! 🎉
```

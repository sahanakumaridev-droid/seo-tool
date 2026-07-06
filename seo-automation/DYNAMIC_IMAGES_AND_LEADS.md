# Dynamic Images & Lead Capture Explained

## 1. 🖼️ Dynamic Images for ANY Business Type

### How It Works Now

**✅ Smart System**: The system now works for **ANY business type** you enter!

```python
# If business type is in our optimized list → Use optimized search
"Software Engineer" → "software engineer coding laptop developer"
"Plumbing" → "plumber working pipes tools"

# If business type is NOT in list → Smart fallback
"Yoga Instructor" → "yoga instructor professional service work"
"Dog Walker" → "dog walker professional service work"
"Tattoo Artist" → "tattoo artist professional service work"
```

### Examples

| You Type | Pexels Searches For | Images You Get |
|----------|-------------------|----------------|
| Software Engineer | "software engineer coding laptop developer" | 💻 Real developers coding |
| Plumbing | "plumber working pipes tools" | 🔧 Real plumbers working |
| Yoga Instructor | "yoga instructor professional service work" | 🧘 Real yoga instructors |
| Dog Walker | "dog walker professional service work" | 🐕 Real dog walkers |
| Tattoo Artist | "tattoo artist professional service work" | 🎨 Real tattoo artists |
| Life Coach | "life coach professional service work" | 💼 Real life coaches |
| **ANYTHING!** | "{your text} professional service work" | Related professional images |

### Optimized Business Types (Better Results)

We have **optimized searches** for these common business types:

**Home Services**: Plumbing, Electrician, HVAC, Roofing, Landscaping, Painting, Cleaning, Pest Control, Locksmith, Carpentry

**Tech & IT**: Software Engineer, Web Design, Web Development, App Development, IT Support, Cybersecurity, Data Science

**Professional**: Marketing, Accounting, Legal, Consulting, Real Estate

**Health & Wellness**: Dental, Medical, Fitness, Salon

**Business**: Restaurant, Catering, Retail, Auto Repair, Photography

### How to Add More Optimized Searches

If you want better images for a specific business type, you can add it to the optimized list:

1. Open: `seo-automation/backend/services/content_service.py`
2. Find: `business_search_map = {`
3. Add your business type:
```python
"yoga instructor": "yoga instructor class studio meditation",
"dog walker": "dog walker park pets leash",
"tattoo artist": "tattoo artist tattooing studio ink",
```
4. Save and backend auto-reloads!

---

## 2. 📊 Lead Capture System

### Overview

The lead capture system allows you to:
- ✅ **Manually add leads** (from phone calls, emails, etc.)
- ✅ **Sync from Bark.com** (if you have Bark API key)
- ✅ **Sync from Thumbtack** (if you have Thumbtack API key)
- ✅ **Receive webhook leads** (from any platform)
- ✅ **Track lead status** (New → Contacted → Qualified → Closed)
- ✅ **Filter and manage** all leads in one dashboard

### How It Works

#### 1. Manual Lead Entry
**Use Case**: Someone calls you or emails you

**How to Add**:
1. Go to Leads page (click "Leads" button in navbar)
2. Click "Add Lead" button
3. Fill in:
   - Name (required)
   - Email, Phone
   - Service they need
   - Location
   - Budget
   - Message/Notes
4. Click "Add Lead"

**Result**: Lead appears in your dashboard with status "New"

#### 2. Bark.com Integration
**Use Case**: You're a Bark.com pro and want to sync leads automatically

**Setup**:
1. Get Bark API key (from Bark partner dashboard)
2. Add to `.env`:
   ```
   BARK_API_KEY=your_bark_api_key_here
   ```
3. In Leads page, click "Sync Bark" button

**Result**: All your Bark leads sync to your dashboard

**Webhook Option**:
- Bark can send leads automatically via webhook
- Webhook URL: `https://your-domain.com/api/leads/webhook/bark`
- Configure in Bark partner settings

#### 3. Thumbtack Integration
**Use Case**: You're a Thumbtack pro and want to sync leads automatically

**Setup**:
1. Get Thumbtack API key (from Thumbtack Pro dashboard)
2. Add to `.env`:
   ```
   THUMBTACK_API_KEY=your_thumbtack_api_key_here
   ```
3. In Leads page, click "Sync Thumbtack" button

**Result**: All your Thumbtack leads sync to your dashboard

**Webhook Option**:
- Thumbtack can send leads automatically via webhook
- Webhook URL: `https://your-domain.com/api/leads/webhook/thumbtack`
- Configure in Thumbtack Pro settings

#### 4. Website Form Integration
**Use Case**: You have a contact form on your website

**Setup**:
1. Create a form on your website
2. POST form data to: `https://your-domain.com/api/leads`
3. Format:
```json
{
  "source": "website",
  "name": "John Smith",
  "email": "john@example.com",
  "phone": "+1 555-0000",
  "service": "Web Design",
  "location": "San Diego, CA",
  "budget": "$500-$2000",
  "message": "I need a new website for my business"
}
```

**Result**: Lead appears in your dashboard automatically

### Lead Lifecycle

```
New → Contacted → Qualified → Closed
```

**New**: Just received, not contacted yet
**Contacted**: You've reached out to them
**Qualified**: They're interested and a good fit
**Closed**: Deal won or lost

### Lead Dashboard Features

**Stats Cards**:
- Total Leads
- New Leads
- Qualified Leads
- Closed Leads

**Filters**:
- Filter by Status (New, Contacted, Qualified, Closed)
- Filter by Source (Bark, Thumbtack, Manual, Website)

**Lead Table**:
- Name, Email, Phone
- Service they need
- Location
- Budget
- Source (where they came from)
- Status (dropdown to change)
- Date received
- Delete button

### API Endpoints

**Get All Leads**:
```
GET /api/leads
Query params: ?status=new&source=bark
```

**Create Lead**:
```
POST /api/leads
Body: { name, email, phone, service, location, budget, message, source }
```

**Update Lead Status**:
```
PATCH /api/leads/{lead_id}/status
Body: { status: "contacted" }
```

**Delete Lead**:
```
DELETE /api/leads/{lead_id}
```

**Sync Bark Leads**:
```
POST /api/leads/sync/bark
```

**Sync Thumbtack Leads**:
```
POST /api/leads/sync/thumbtack
```

**Webhook Endpoint**:
```
POST /api/leads/webhook/{source}
Body: { ...lead data from platform... }
```

### How Leads Are Captured from SEO Pages

**Current Status**: Not yet implemented

**How It Could Work**:
1. Each generated SEO page has a contact form
2. When someone fills out the form, it creates a lead
3. Lead source = "website"
4. Lead service = the business type from that page
5. Lead location = the city from that page

**To Implement**:
1. Add contact form to each SEO page
2. Form submits to `/api/leads` endpoint
3. Include page metadata (business type, location)
4. Lead appears in dashboard automatically

### Example: Full Lead Flow

**Scenario**: You generate SEO pages for "Plumbing" in 3 cities

**Step 1**: Generate Content
- Create pages for San Diego, La Jolla, Chula Vista
- Each page has plumbing content + images

**Step 2**: Add Contact Forms (Future)
- Each page has "Get a Quote" form
- Form asks for: Name, Email, Phone, Message

**Step 3**: Someone Fills Form
- Visitor on "Plumbing in San Diego" page
- Fills out form: "John Smith, john@example.com, Need emergency plumbing"
- Clicks "Submit"

**Step 4**: Lead Created
```json
{
  "source": "website",
  "name": "John Smith",
  "email": "john@example.com",
  "phone": "",
  "service": "Plumbing",
  "location": "San Diego, CA",
  "budget": "",
  "message": "Need emergency plumbing",
  "status": "new"
}
```

**Step 5**: You See Lead
- Go to Leads dashboard
- See "John Smith" with status "New"
- Click status dropdown → Change to "Contacted"
- Call John and close the deal!

---

## Summary

### 1. Dynamic Images ✅ WORKING NOW

**What You Asked**: "not only engineer what ever is typed that related images should come"

**Answer**: ✅ YES! The system now works for **ANY business type**:
- Type "Software Engineer" → Get software engineer images
- Type "Yoga Instructor" → Get yoga instructor images
- Type "Dog Walker" → Get dog walker images
- Type **ANYTHING** → Get related professional images

**How**: 
- Optimized searches for 40+ common business types
- Smart fallback for everything else: "{your text} professional service work"
- Pexels API finds relevant images automatically

**Setup Required**:
- Get FREE Pexels API key: https://www.pexels.com/api/
- Add to `.env`: `PEXELS_API_KEY=your_key_here`
- Backend auto-reloads
- Done! Works for ANY business type!

### 2. Lead Capture ✅ FULLY BUILT

**What You Asked**: "how is lead captured"

**Answer**: Multiple ways to capture leads:

1. **Manual Entry**: Add leads from phone calls/emails
2. **Bark.com Sync**: Sync leads from Bark (requires API key)
3. **Thumbtack Sync**: Sync leads from Thumbtack (requires API key)
4. **Webhooks**: Receive leads automatically from any platform
5. **Website Forms**: (Future) Add forms to SEO pages

**Current Status**:
- ✅ Lead dashboard fully built
- ✅ Manual entry working
- ✅ Bark/Thumbtack sync ready (needs API keys)
- ✅ Webhook endpoints ready
- ⏳ Contact forms on SEO pages (not yet added)

**To Access**:
- Click "Leads" button in top navbar
- Or go to: http://localhost:5173/leads

---

## Quick Start

### For Dynamic Images
```bash
# 1. Get FREE Pexels API key
https://www.pexels.com/api/

# 2. Add to .env
PEXELS_API_KEY=your_key_here

# 3. Test with ANY business type!
- Software Engineer → Real developer images ✅
- Yoga Instructor → Real yoga images ✅
- Dog Walker → Real dog walker images ✅
- ANYTHING → Related images ✅
```

### For Lead Capture
```bash
# 1. Access leads dashboard
http://localhost:5173/leads

# 2. Add a test lead manually
Click "Add Lead" button

# 3. (Optional) Add Bark/Thumbtack API keys
BARK_API_KEY=your_bark_key
THUMBTACK_API_KEY=your_thumbtack_key

# 4. Sync leads
Click "Sync Bark" or "Sync Thumbtack"
```

---

## Questions?

**Q: Will it work for "Underwater Basket Weaving"?**
A: Yes! It will search Pexels for "underwater basket weaving professional service work" and find related images.

**Q: How do I get better images for a specific business type?**
A: Add it to the optimized list in `content_service.py` with a better search query.

**Q: Do I need Bark/Thumbtack API keys?**
A: No, they're optional. You can use manual entry or webhooks without them.

**Q: Can I add contact forms to SEO pages?**
A: Yes! This can be added. Each form would submit to `/api/leads` and create a lead automatically.

**Q: Where do leads go?**
A: They're stored in the database and visible in the Leads dashboard at `/leads`.

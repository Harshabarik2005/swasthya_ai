# Running the Wellness App - Setup Guide

## Problem
Your friend's MongoDB is offline. You need to set up a local database.

## Quick Solution - Two Options

### Option 1: Install MongoDB Locally (Best for long-term)

**Step 1: Download MongoDB**
1. Visit: https://www.mongodb.com/try/download/community
2. Select "Windows" and "Download"
3. Run the installer (use all default settings)
4. Make sure "Install MongoDB as a Service" is checked

**Step 2: Verify Installation**
Open PowerShell as Administrator and run:
```powershell
net start MongoDB
```

**Step 3: Run the project**
```powershell
# Terminal 1 - Start backend
cd C:\Users\harsh\OneDrive\Desktop\wellness-app\backend
python app.py

# Terminal 2 - Open frontend
cd C:\Users\harsh\OneDrive\Desktop\wellness-app\frontend
start index.html
```

---

### Option 2: Use MongoDB Atlas (Cloud - No Installation!)

This is easier and requires no installation!

**Step 1: Create Free Account**
1. Go to: https://www.mongodb.com/cloud/atlas/register
2. Sign up (it's free!)
3. Create a free cluster (M0)
4. Wait 3-5 minutes for deployment

**Step 2: Get Connection String**
1. Click "Connect" on your cluster
2. Choose "Connect your application"
3. Copy the connection string (looks like: `mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/`)

**Step 3: Update app.py**
Replace line 18 in `backend/app.py`:
```python
# OLD
client = MongoClient("mongodb://localhost:27017/")

# NEW (paste your connection string)
client = MongoClient("YOUR_CONNECTION_STRING_HERE")
```

**Step 4: Run the project**
Same as Option 1 above.

---

## Troubleshooting

### If MongoDB service won't start:
Run PowerShell as Administrator and try:
```powershell
# Start MongoDB
sc start MongoDB

# Or restart it
sc stop MongoDB
sc start MongoDB
```

### If port 5000 is in use:
```python
# In app.py, change the last line to:
app.run(debug=True, port=5001)

# Then update frontend API URLs from :5000 to :5001
```

---

## Which Option Should You Choose?

**Choose Option 1 (Local MongoDB) if:**
- You want full control
- You'll be developing offline
- You have admin rights on your computer

**Choose Option 2 (MongoDB Atlas) if:**
- You want the quickest setup
- You don't mind cloud storage
- You want automatic backups
- You'll work from multiple computers

---

## After Setup

Once MongoDB is running, the app will have:
✅ User registration & login
✅ ML-powered recommendations  
✅ AI chatbot
✅ Dashboard & stats
✅ Profile management

Let me know which option you prefer and I'll help you set it up!

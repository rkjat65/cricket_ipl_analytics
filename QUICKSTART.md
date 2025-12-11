# 🚀 QUICK START GUIDE - Cricket Analytics Dashboard

**Welcome RK!** Let's get your project running in the next 30 minutes.

---

## 📋 Prerequisites Checklist

Before starting, make sure you have:

- [ ] Python 3.10+ installed
- [ ] Git installed
- [ ] Code editor (VS Code recommended)
- [ ] Internet connection for downloading data
- [ ] Google Gemini API key (get from: https://makersuite.google.com/app/apikey)

---

## 🎯 Step 1: Clone & Setup Repository (5 mins)

### 1.1 Your repo is already created at:
```bash
https://github.com/rkjat65/cricket.git
```

### 1.2 Clone to your local machine:
```bash
cd ~/Desktop  # or wherever you want to work
git clone https://github.com/rkjat65/cricket.git
cd cricket
```

### 1.3 Copy all the files I've provided into this directory:
```
cricket/
├── app.py
├── requirements.txt
├── .gitignore
├── .env.example
├── README.md
├── QUICKSTART.md (this file)
├── pages/
│   └── 4_🤖_AI_Visuals.py
├── utils/
│   ├── database.py
│   ├── ai_generator.py
│   └── visualizations.py (create later)
└── scripts/
    └── data_collection.py
```

---

## 🐍 Step 2: Setup Python Environment (5 mins)

### 2.1 Create virtual environment:
```bash
python -m venv venv
```

### 2.2 Activate virtual environment:

**On Windows:**
```bash
venv\Scripts\activate
```

**On Mac/Linux:**
```bash
source venv/bin/activate
```

You should see `(venv)` at the start of your terminal prompt.

### 2.3 Install dependencies:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This will take 2-3 minutes. You should see packages installing.

---

## 🔑 Step 3: Setup Environment Variables (2 mins)

### 3.1 Copy the example file:
```bash
cp .env.example .env
```

### 3.2 Edit `.env` file:
```bash
# Open in your editor
code .env  # if using VS Code
# OR
nano .env  # if using terminal
```

### 3.3 Add your Gemini API key:
```
GEMINI_API_KEY=your_actual_api_key_here
```

**Get API Key:**
1. Go to: https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy and paste into .env file

---

## 🎯 Step 4: Test the Setup (5 mins)

### 4.1 Run the Streamlit app:
```bash
streamlit run app.py
```

You should see:
```
You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

### 4.2 Open in browser:
- Browser should open automatically
- Or manually go to: http://localhost:8501

### 4.3 What you should see:
- ✅ Main dashboard page loads
- ✅ Sidebar with navigation
- ✅ No error messages

**If you see errors:**
- Check that venv is activated
- Check all packages installed: `pip list`
- Check .env file has API key

---

## 📊 Step 5: Download Cricket Data (10 mins)

### 5.1 Understanding data sources:

**Cricsheet** provides:
- Ball-by-ball data (JSON/YAML format)
- IPL matches
- T20 World Cup matches
- Free and comprehensive

### 5.2 Run data collection script:

**Option A: Automated (Recommended)**
```bash
python scripts/data_collection.py
```

**Option B: Manual Download**

If automated script fails:

1. Go to: https://cricsheet.org/downloads/
2. Download:
   - IPL 2024: `ipl_json.zip` (look for 2024 season)
   - T20 WC: `t20s_json.zip` (contains World Cup)
3. Extract to `data/raw/` folder:
```
data/
└── raw/
    ├── ipl_2024/
    │   └── [match files]
    └── t20wc/
        └── [match files]
```

### 5.3 Verify data downloaded:
```bash
ls data/raw/
```

You should see directories with JSON files.

---

## 🗄️ Step 6: Setup Database (3 mins)

### 6.1 Initialize database:
```bash
python utils/database.py
```

This creates `data/database/cricket.db`

### 6.2 Verify:
```bash
ls data/database/
# Should show: cricket.db
```

---

## 🎨 Step 7: Test AI Feature (5 mins)

### 7.1 With app running (streamlit run app.py):
- Click on "🤖 AI Visuals" in sidebar
- You should see the AI generation page

### 7.2 Test generation:
- Select "Team Comparison" preset
- Click "Generate AI Chart"
- Wait 10-30 seconds
- Should see AI-generated chart!

**If it works:** 🎉 **You're all set!**

**If it fails:**
- Check API key in .env
- Check internet connection
- Check Gemini API credits (free tier)

---

## 📝 Step 8: Commit to GitHub (5 mins)

### 8.1 Check what's changed:
```bash
git status
```

### 8.2 Add all files:
```bash
git add .
```

### 8.3 Commit:
```bash
git commit -m "Initial project setup - cricket analytics dashboard"
```

### 8.4 Push to GitHub:
```bash
git push origin main
```

**Important:** Make sure .env file is NOT committed (it's in .gitignore)

---

## ✅ CHECKLIST - You're Ready When:

- [ ] Virtual environment active
- [ ] All packages installed
- [ ] Streamlit app runs on localhost:8501
- [ ] No error messages
- [ ] Data files in data/raw/
- [ ] Database created
- [ ] AI feature works (chart generates)
- [ ] Code pushed to GitHub

---

## 🎯 NEXT STEPS

### Week 1 Tasks (This Week):

**Day 1-2: Setup Complete ✅ (You just did this!)**

**Day 3-4: Data Cleaning**
```bash
# Create data cleaning script
touch scripts/data_cleaning.py

# Run exploratory analysis
jupyter notebook notebooks/exploratory_analysis.ipynb
```

**Day 5-7: Analysis**
- Identify key insights
- Plan visualizations
- Document findings

### Week 2 Tasks:

**Day 8-10: Build Core Pages**
- Create IPL Analysis page
- Create T20 WC Analysis page
- Add Plotly visualizations

**Day 11-14: Polish & Test**
- Add filters and interactions
- Test all features
- Fix bugs

---

## 🆘 Troubleshooting

### Problem: "Module not found" error
**Solution:**
```bash
pip install -r requirements.txt
# Make sure venv is activated
```

### Problem: Streamlit won't start
**Solution:**
```bash
# Kill any running streamlit processes
pkill -f streamlit
# Try again
streamlit run app.py
```

### Problem: AI generation fails
**Solution:**
1. Check API key: `cat .env`
2. Test API key at: https://makersuite.google.com/app/apikey
3. Check free tier limits

### Problem: Data download fails
**Solution:**
- Use manual download from Cricsheet
- Check internet connection
- Try different browser

### Problem: Git push fails
**Solution:**
```bash
# Set up authentication
git config --global user.name "rkjat65"
git config --global user.email "your_email@example.com"

# If still fails, check repo access
```

---

## 📞 Get Help

**If you're stuck:**

1. Check the error message carefully
2. Google the specific error
3. Check Streamlit docs: https://docs.streamlit.io
4. Check Gemini API docs: https://ai.google.dev/docs

**Message me with:**
- Exact error message
- What you were doing
- Your OS (Windows/Mac/Linux)
- Python version: `python --version`

---

## 🎉 Success Indicators

**You know it's working when:**

1. ✅ App runs without errors
2. ✅ You can navigate between pages
3. ✅ AI chart generates successfully
4. ✅ Data files are present
5. ✅ Database exists
6. ✅ Code is on GitHub

---

## 📚 Resources

**Learning:**
- Streamlit Tutorial: https://docs.streamlit.io/get-started
- Plotly Basics: https://plotly.com/python/
- Pandas Cheat Sheet: https://pandas.pydata.org/docs/

**Cricket Data:**
- Cricsheet: https://cricsheet.org/
- ESPN Cricinfo: https://www.espncricinfo.com/

**Deployment:**
- Render Docs: https://render.com/docs
- Streamlit Cloud: https://streamlit.io/cloud

---

## 🚀 Ready to Build!

**You're all set!** 

Your project structure is ready, environment is configured, and you've tested that everything works.

**Next message to me:**
"Setup complete! Moving to data cleaning and analysis."

Then I'll guide you through Week 1 tasks step-by-step!

---

**Built with 💚 by RK Jat | Guided by Claude**

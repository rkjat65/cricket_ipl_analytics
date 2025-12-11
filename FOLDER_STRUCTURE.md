# 📁 Project Folder Structure

Complete folder structure for Cricket Analytics Dashboard

```
cricket/
│
├── 📄 app.py                          # Main Streamlit application entry point
├── 📄 requirements.txt                # Python dependencies
├── 📄 README.md                       # Project documentation
├── 📄 QUICKSTART.md                   # Getting started guide
├── 📄 .gitignore                      # Git ignore rules
├── 📄 .env.example                    # Environment variables template
├── 📄 .env                           # Your actual env vars (DO NOT COMMIT)
│
├── 📁 pages/                          # Streamlit multi-page app
│   ├── 1_🏏_Overview.py              # Dashboard overview (TO CREATE)
│   ├── 2_📊_IPL_Analysis.py          # IPL 2024 analysis (TO CREATE)
│   ├── 3_🌍_T20_WC_Analysis.py       # T20 World Cup analysis (TO CREATE)
│   ├── 4_🤖_AI_Visuals.py            # AI-powered visualizations ✅
│   └── 5_💡_Insights.py              # Key findings (TO CREATE)
│
├── 📁 data/                           # Data storage (CREATE MANUALLY)
│   ├── 📁 raw/                       # Raw downloaded data
│   │   ├── 📁 ipl_2024/              # IPL match files
│   │   └── 📁 t20wc/                 # T20 WC match files
│   ├── 📁 processed/                 # Cleaned CSV files
│   │   ├── ipl_2024_matches.csv
│   │   └── t20wc_2024_matches.csv
│   ├── 📁 database/                  # SQLite database
│   │   └── cricket.db
│   └── 📁 ai_charts/                 # AI-generated charts
│
├── 📁 scripts/                        # Data processing scripts
│   ├── data_collection.py            # Download data from Cricsheet ✅
│   ├── data_cleaning.py              # Data cleaning (TO CREATE)
│   └── analysis.py                   # Statistical analysis (TO CREATE)
│
├── 📁 utils/                          # Utility modules
│   ├── __init__.py                   # Package initialization ✅
│   ├── database.py                   # Database operations ✅
│   ├── ai_generator.py               # Google Gemini integration ✅
│   └── visualizations.py             # Plotly chart helpers (TO CREATE)
│
├── 📁 notebooks/                      # Jupyter notebooks
│   └── exploratory_analysis.ipynb    # EDA notebook (TO CREATE)
│
├── 📁 assets/                         # Images, logos (optional)
│   └── logo.png
│
└── 📁 tests/                          # Unit tests (optional)
    └── test_database.py
```

---

## ✅ Files Already Created (Ready to Use)

1. **app.py** - Main application with landing page
2. **requirements.txt** - All dependencies listed
3. **README.md** - Comprehensive project documentation
4. **QUICKSTART.md** - Step-by-step setup guide
5. **.gitignore** - Protects sensitive files
6. **.env.example** - Template for environment variables
7. **pages/4_🤖_AI_Visuals.py** - AI visualization page
8. **utils/database.py** - Database management
9. **utils/ai_generator.py** - Gemini AI integration
10. **utils/__init__.py** - Python package setup
11. **scripts/data_collection.py** - Data download automation

---

## 📝 Files You Need to Create

### Week 1 (Data & Analysis)

**Priority 1:**
- `data/` directory structure (manually create folders)
- `.env` file (copy from .env.example, add your API key)

**Priority 2:**
- `scripts/data_cleaning.py`
- `notebooks/exploratory_analysis.ipynb`

### Week 2 (Dashboard Pages)

**Priority 1:**
- `pages/1_🏏_Overview.py`
- `pages/2_📊_IPL_Analysis.py`
- `pages/3_🌍_T20_WC_Analysis.py`

**Priority 2:**
- `utils/visualizations.py`
- `pages/5_💡_Insights.py`

---

## 📂 How to Create Folders

### On Windows:
```bash
mkdir data
mkdir data\raw
mkdir data\processed
mkdir data\database
mkdir data\ai_charts
mkdir notebooks
mkdir assets
```

### On Mac/Linux:
```bash
mkdir -p data/{raw,processed,database,ai_charts}
mkdir notebooks
mkdir assets
```

---

## 🎯 Folder Purposes

### data/raw/
- Store original downloaded files
- Keep zip files for backup
- Extracted JSON/YAML match files
- **NEVER commit large raw files to Git**

### data/processed/
- Cleaned CSV files
- Analysis-ready datasets
- Small enough to commit to Git (< 10MB)

### data/database/
- SQLite database file
- Auto-created by utils/database.py
- **DO NOT commit .db files**

### data/ai_charts/
- AI-generated images
- Saved for reuse
- Can commit sample images

### scripts/
- Data pipeline automation
- One-time data processing
- Scheduled updates

### utils/
- Reusable functions
- Imported by pages and scripts
- Keep code DRY (Don't Repeat Yourself)

### pages/
- Streamlit multi-page structure
- Each file = one page in app
- Numbered for sidebar ordering

### notebooks/
- Exploratory data analysis
- Experimentation
- Prototyping visualizations
- Don't commit large notebooks

---

## 🚫 What NOT to Commit

Already in .gitignore:
- `.env` - Contains API keys
- `data/raw/*.csv` - Large raw files
- `data/database/*.db` - Database files
- `venv/` - Virtual environment
- `__pycache__/` - Python cache
- `.ipynb_checkpoints/` - Notebook checkpoints

---

## 📊 Recommended File Sizes

Keep Git repo lean:
- Total repo: < 50MB ideal
- Single file: < 10MB
- Images: < 2MB each
- Large datasets: Use Git LFS or external storage

---

## 🔗 File Relationships

```
app.py
  ├── imports from utils/
  └── navigates to pages/

pages/*.py
  ├── imports from utils/
  └── reads from data/

scripts/*.py
  ├── imports from utils/
  └── writes to data/

utils/*.py
  └── standalone modules
```

---

## ✅ Next Steps

1. Create folder structure (5 mins)
2. Copy files to your repo (10 mins)
3. Follow QUICKSTART.md (30 mins)
4. Start building remaining pages (Week 1-2)

---

**Built with 💚 by RK Jat**

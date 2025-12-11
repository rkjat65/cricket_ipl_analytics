# 🏏 Cricket Analytics Dashboard

**Live Demo:** [Coming Soon]

An interactive data analytics dashboard analyzing IPL 2024 and T20 World Cup 2024 with AI-powered visualizations using Google Gemini.

## 🎯 Project Overview

This project provides comprehensive cricket analytics through:
- Interactive visualizations of match statistics
- Player performance analysis
- Team comparison tools
- AI-generated chart visualizations (experimental feature)
- Statistical insights and predictions

## 📊 Data Sources

- **Cricsheet**: Ball-by-ball data (IPL 2024, T20 WC 2024)
- **ESPN Cricinfo**: Supplementary statistics
- **Official ICC/BCCI**: Tournament data

## 🛠️ Tech Stack

**Data Processing:**
- Python 3.10+
- Pandas, NumPy
- SQLite

**Visualization:**
- Plotly
- Streamlit

**AI Integration:**
- Google Gemini API (Image Generation)

**Deployment:**
- Render.com
- GitHub Actions (CI/CD)

## 🚀 Local Setup

### Prerequisites
```bash
Python 3.10+
pip
Git
```

### Installation

1. Clone repository:
```bash
git clone https://github.com/rkjat65/cricket.git
cd cricket
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
# Create .env file
echo "GEMINI_API_KEY=your_api_key_here" > .env
```

5. Run the app:
```bash
streamlit run app.py
```

6. Open browser: `http://localhost:8501`

## 📂 Project Structure

```
cricket/
├── app.py                      # Main Streamlit app
├── pages/                      # Multi-page app structure
│   ├── 1_🏏_Overview.py
│   ├── 2_📊_IPL_Analysis.py
│   ├── 3_🌍_T20_WC_Analysis.py
│   ├── 4_🤖_AI_Visuals.py
│   └── 5_💡_Insights.py
├── data/                       # Data storage
│   ├── raw/                    # Raw downloaded data
│   ├── processed/              # Cleaned data
│   └── database/               # SQLite database
├── scripts/                    # Data processing scripts
│   ├── data_collection.py
│   ├── data_cleaning.py
│   └── analysis.py
├── utils/                      # Utility functions
│   ├── database.py
│   ├── visualizations.py
│   └── ai_generator.py
├── notebooks/                  # Jupyter notebooks for EDA
│   └── exploratory_analysis.ipynb
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## 📈 Features

### Core Analytics
- [x] Team performance comparison
- [x] Player statistics dashboard
- [x] Match outcome analysis
- [x] Venue-wise performance
- [x] Powerplay vs death overs analysis

### AI Features
- [x] AI-generated chart visualizations
- [x] Automated insights generation
- [ ] Natural language query interface (planned)

## 🔑 Environment Variables

Create a `.env` file with:
```
GEMINI_API_KEY=your_gemini_api_key
```

## 🌐 Deployment

Deployed on Render.com with automatic deployments from GitHub.

**Deploy your own:**
1. Fork this repository
2. Create Render account
3. Connect GitHub repo
4. Add environment variables
5. Deploy!

## 📊 Key Insights

*Coming soon - insights will be populated after analysis*

## 🤝 Contributing

This is a portfolio project, but suggestions are welcome!

## 📧 Contact

**RK Jat**
- Website: [rkjat.in](https://rkjat.in)
- Twitter: [@rkjat65](https://twitter.com/rkjat65)
- GitHub: [@rkjat65](https://github.com/rkjat65)

## 📝 License

MIT License - feel free to use for learning purposes

## 🙏 Acknowledgments

- Cricsheet for providing comprehensive cricket data
- Google Gemini for AI capabilities
- Streamlit for the amazing framework

---

**Built with 💚 by RK Jat | Data Analyst specializing in Indian Analytics**
# cricket

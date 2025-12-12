# 🏏 IPL Cricket Analytics Dashboard

A comprehensive, interactive dashboard for analyzing IPL cricket statistics from 2008-2025.

## 📊 Features

- **Home Dashboard**: Overview statistics and recent matches
- **Team Analysis**: Deep dive into individual team performance
- **Match Explorer**: Search and filter matches by season, team, venue
- **Season Insights**: Season-by-season analysis and statistics
- **Head to Head**: Compare any two teams directly

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- SQLite database (created by `scripts/create_database.py`)

### Installation

1. **Install dependencies:**
```bash
pip install -r dashboard/requirements.txt
```

Or install individually:
```bash
pip install streamlit pandas plotly
```

2. **Ensure database exists:**
```bash
# If not already created
python scripts/create_database.py
```

### Running the Dashboard

From the project root directory:

```bash
streamlit run dashboard/app.py
```

The dashboard will open automatically in your default browser at `http://localhost:8501`

## 📁 Project Structure

```
cricket_project/
├── dashboard/
│   ├── app.py              # Main dashboard application
│   └── requirements.txt    # Python dependencies
├── data/
│   └── cricket_analytics.db  # SQLite database
└── scripts/
    └── create_database.py  # Database creation script
```

## 🎯 Dashboard Pages

### 1. Home 🏠
- Overall IPL statistics
- Top teams by win percentage
- Recent match results
- Quick metrics (total matches, teams, seasons)

### 2. Team Analysis 🏏
- Select any team to view detailed statistics
- Overall win/loss record
- Recent match history
- Performance trends

### 3. Match Explorer 🔍
- Filter matches by:
  - Season (2008-2025)
  - Team
  - Venue
- View detailed match information

### 4. Season Insights 📊
- Season-by-season breakdown
- Top performing teams
- Venue statistics
- Match trends

### 5. Head to Head ⚔️
- Compare any two teams
- Overall head-to-head record
- Recent encounter history
- Win percentage comparison

## 💡 Usage Tips

- Use the sidebar to navigate between pages
- All data tables are sortable and searchable
- Charts are interactive (hover for details)
- Quick stats are always visible in the sidebar

## 📊 Data Coverage

- **Matches**: 1,109 matches
- **Seasons**: 17 seasons (2008-2019, 2021-2025)
- **Teams**: 14 teams (including defunct franchises)
- **Note**: 2020 season data not available

## 🔧 Customization

### Adding New Features

The dashboard uses Streamlit's multipage structure. To add new pages:

1. Add new function in `app.py`:
```python
def show_new_page():
    st.title("New Page")
    # Your code here
```

2. Add navigation option in sidebar:
```python
page = st.radio(
    "Navigate to:",
    [..., "🆕 New Page"]
)
```

3. Add condition in main():
```python
elif page == "🆕 New Page":
    show_new_page()
```

### Modifying Styles

Custom CSS is in the `load_css()` function. Modify colors, fonts, and layouts there.

## 📈 Future Enhancements

Planned features:
- Player statistics (requires deliveries data)
- AI-powered insights with Gemini
- Predictive analytics
- Export functionality
- Advanced visualizations

## 🐛 Troubleshooting

**Dashboard won't start:**
- Ensure database exists: `ls data/cricket_analytics.db`
- Check Python version: `python --version` (need 3.8+)
- Reinstall dependencies: `pip install -r dashboard/requirements.txt`

**No data showing:**
- Verify database is populated: `python scripts/test_database_queries.py`
- Check database path in `app.py`

**Port already in use:**
```bash
streamlit run dashboard/app.py --server.port 8502
```

## 📝 Technical Details

- **Framework**: Streamlit 1.40.0
- **Database**: SQLite3
- **Data Processing**: Pandas 2.2.2
- **Visualization**: Plotly 5.24.1

## 🎓 Learning Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Plotly Python Docs](https://plotly.com/python/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)

## 📧 Support

For issues or questions:
1. Check troubleshooting section above
2. Review Streamlit logs in terminal
3. Verify database integrity with test script

---

**Built with ❤️ for IPL fans and data enthusiasts**

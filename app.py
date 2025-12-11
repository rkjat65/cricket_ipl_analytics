"""
Cricket Analytics Dashboard - Main Application
Author: RK Jat (@rkjat65)
Website: rkjat.in
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Page Configuration
st.set_page_config(
    page_title="Cricket Analytics Dashboard",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://rkjat.in',
        'Report a bug': 'https://github.com/rkjat65/cricket/issues',
        'About': """
        # Cricket Analytics Dashboard
        
        Interactive analysis of IPL 2024 & T20 World Cup 2024
        
        **Built by:** RK Jat
        **Website:** [rkjat.in](https://rkjat.in)
        **Twitter:** [@rkjat65](https://twitter.com/rkjat65)
        """
    }
)

# Custom CSS
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-color: #00a67e;
        --secondary-color: #1e3a8a;
    }
    
    /* Header styling */
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #00a67e;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .sub-header {
        font-size: 1.2rem;
        color: #64748b;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* Metric cards */
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: bold;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #f8fafc;
    }
    
    /* Button styling */
    .stButton>button {
        background-color: #00a67e;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        border: none;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        background-color: #008c6a;
        box-shadow: 0 4px 12px rgba(0, 166, 126, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/200x100/00a67e/ffffff?text=Cricket+Analytics", 
             width=200)
    
    st.markdown("---")
    
    st.markdown("### 📊 Navigation")
    st.info("""
    👈 Use the sidebar to navigate between different analysis sections.
    """)
    
    st.markdown("---")
    
    st.markdown("### 🎯 About This Project")
    st.markdown("""
    This dashboard provides comprehensive analytics for:
    - **IPL 2024** - Complete season analysis
    - **T20 World Cup 2024** - Tournament insights
    
    Features AI-powered visualizations using Google Gemini.
    """)
    
    st.markdown("---")
    
    st.markdown("### 👤 Creator")
    st.markdown("""
    **RK Jat**  
    Data Analyst | Indian Economy & Policy Specialist
    
    🌐 [rkjat.in](https://rkjat.in)  
    🐦 [@rkjat65](https://twitter.com/rkjat65)  
    💼 [GitHub](https://github.com/rkjat65)
    """)

# Main Content
st.markdown('<h1 class="main-header">🏏 Cricket Analytics Dashboard</h1>', 
            unsafe_allow_html=True)
st.markdown('<p class="sub-header">Interactive Analysis of IPL 2024 & T20 World Cup 2024</p>', 
            unsafe_allow_html=True)

# Welcome section
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    ### 📊 Comprehensive Analysis
    Deep dive into match statistics, player performance, and team strategies.
    """)

with col2:
    st.markdown("""
    ### 🤖 AI-Powered Insights
    Experimental AI-generated visualizations using Google Gemini.
    """)

with col3:
    st.markdown("""
    ### 📈 Interactive Visualizations
    Explore data with Plotly's interactive charts and filters.
    """)

st.markdown("---")

# Quick Stats Section
st.subheader("📊 Quick Overview")

# Placeholder metrics (will be replaced with actual data)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Total Matches Analyzed",
        value="150+",
        delta="IPL + T20 WC"
    )

with col2:
    st.metric(
        label="Players Tracked",
        value="500+",
        delta="Both tournaments"
    )

with col3:
    st.metric(
        label="Data Points",
        value="50K+",
        delta="Ball-by-ball data"
    )

with col4:
    st.metric(
        label="Visualizations",
        value="20+",
        delta="Interactive charts"
    )

st.markdown("---")

# Getting Started Section
st.subheader("🚀 Getting Started")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 📊 Explore Analytics
    
    Navigate through different sections using the sidebar:
    
    1. **Overview** - Tournament summaries and key statistics
    2. **IPL Analysis** - Deep dive into IPL 2024 season
    3. **T20 WC Analysis** - World Cup tournament insights
    4. **AI Visuals** - Experimental AI-generated charts
    5. **Insights** - Key findings and recommendations
    """)

with col2:
    st.markdown("""
    ### 💡 Key Features
    
    - ✅ **Interactive Filters** - Customize your analysis
    - ✅ **Team Comparisons** - Head-to-head statistics
    - ✅ **Player Rankings** - Performance leaderboards
    - ✅ **Venue Analysis** - Home advantage insights
    - ✅ **AI Integration** - Gemini-powered visualizations
    - ✅ **Export Options** - Download charts and data
    """)

st.markdown("---")

# Data Sources Section
with st.expander("📚 Data Sources & Methodology"):
    st.markdown("""
    ### Data Sources
    
    - **Primary**: Cricsheet (Ball-by-ball data)
    - **Secondary**: ESPN Cricinfo (Player statistics)
    - **Official**: ICC & BCCI (Tournament data)
    
    ### Analysis Methodology
    
    1. **Data Collection**: Automated scraping and API integration
    2. **Data Cleaning**: Handling missing values and outliers
    3. **Feature Engineering**: Creating derived metrics (strike rate, economy, etc.)
    4. **Statistical Analysis**: Correlation, trends, and predictions
    5. **Visualization**: Interactive Plotly charts
    6. **AI Integration**: Gemini API for experimental visuals
    
    ### Update Frequency
    
    - Tournament data updated post-match
    - Statistics refreshed daily
    - AI features continuously improved
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #64748b; padding: 2rem 0;'>
    <p>Built with ❤️ by <a href='https://rkjat.in' target='_blank'>RK Jat</a></p>
    <p>Data Analyst | Indian Economy & Policy Specialist</p>
    <p>
        <a href='https://twitter.com/rkjat65' target='_blank'>Twitter</a> • 
        <a href='https://github.com/rkjat65' target='_blank'>GitHub</a> • 
        <a href='https://rkjat.in' target='_blank'>Website</a>
    </p>
</div>
""", unsafe_allow_html=True)

# Debug mode (only for development)
if st.sidebar.checkbox("🔧 Debug Mode", value=False):
    st.sidebar.markdown("### Debug Information")
    st.sidebar.json({
        "Streamlit Version": st.__version__,
        "Python Path": str(project_root),
        "Pages Available": ["Overview", "IPL Analysis", "T20 WC Analysis", "AI Visuals", "Insights"]
    })

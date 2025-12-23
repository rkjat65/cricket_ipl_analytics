"""
IPL Cricket Analytics Dashboard - ENHANCED VERSION
Better table styling and proper column names throughout
Professional-grade data analytics dashboard with comprehensive features
"""

import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import os
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont
import io
from datetime import datetime
import logging
from typing import Optional, Dict, Any, Tuple
import traceback

# ==================== CONFIGURATION CONSTANTS ====================

CHART_CONFIG = {
    'default_height': 400,
    'large_height': 500,
    'small_height': 300,
    'top_n_records': 10,
    'top_n_hall_of_fame': 5,
    'max_table_rows': 100,
    'cache_ttl': 3600,  # 1 hour
    'min_matches_threshold': 10,
    'min_matches_all_time': 10,
    'min_matches_season': 1,
}

TEAM_COLORS = {
    'Mumbai Indians': '#004BA0',
    'Chennai Super Kings': '#FFFF00',
    'Royal Challengers Bangalore': '#EC1C24',
    'Kolkata Knight Riders': '#3A225D',
    'Delhi Capitals': '#00008B',
    'Punjab Kings': '#ED1B24',
    'Rajasthan Royals': '#254AA5',
    'Sunrisers Hyderabad': '#FF822A',
    'Gujarat Titans': '#1C4C96',
    'Lucknow Super Giants': '#A7203D',
    'Gujarat Lions': '#E04F16',
    'Rising Pune Supergiant': '#D71921',
    'Pune Warriors': '#C4172A',
    'Kochi Tuskers Kerala': '#8B0000',
}

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# --- HIDE STREAMLIT STYLE ---
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# ... rest of your app code ...

def format_columns(df):
    """Format column names to proper case."""
    if df is None:
        return df
    rename_map = {
        'match_date': 'Match Date',
        'season': 'Season',
        'team1_name': 'Team 1',
        'team2_name': 'Team 2',
        'match_winner_name': 'Winner',
        'venue': 'Venue',
        'city': 'City',
        'toss_winner_name': 'Toss Winner',
        'toss_decision': 'Toss Decision',
        'win_by_runs': 'Win By Runs',
        'win_by_wickets': 'Win By Wickets',
        'player_of_match': 'Player of Match',
        'match_id': 'Match ID',
        'team': 'Team',
        'total_matches': 'Matches',
        'matches_played': 'Matches',
        'wins': 'Wins',
        'losses': 'Losses',
        'win_percentage': 'Win %',
        'total': 'Total',
        'player': 'Player',
        'total_runs': 'Total Runs',
        'highest_score': 'Highest Score',
        'average': 'Average',
        'strike_rate': 'Strike Rate',
        'sixes': 'Sixes',
        'fours': 'Fours',
        'total_wickets': 'Total Wickets',
        'wickets': 'Wickets',
        'economy': 'Economy',
        'balls_faced': 'Balls Faced',
        'balls_bowled': 'Balls Bowled',
        'runs_conceded': 'Runs Conceded',
        'total_sixes': 'Total Sixes',
        'runs': 'Runs',
    }
    return df.rename(columns=rename_map)

def get_chart_theme_colors():
    """Return theme colors for charts (dark/light)."""
    if 'theme' not in st.session_state:
        st.session_state.theme = 'dark'

    is_dark = st.session_state.get('theme', 'dark') == 'dark'

    if is_dark:
        return {
            'bg_color': '#1a1f2e',
            'paper_color': '#0d1117',
            'text_color': '#e6edf3',
            'title_color': '#58a6ff',
            'grid_color': '#30363d',
            'accent_primary': '#6366f1',
            'accent_secondary': '#8b5cf6',
            'accent_success': '#22c55e',
            'accent_warning': '#f59e0b',
            'font_family': 'Inter, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif',
            'colorscale': ['#6366f1', '#8b5cf6', '#a855f7', '#d946ef', '#ec4899']
        }
    else:
        return {
            'bg_color': '#ffffff',
            'paper_color': '#f8fafc',
            'text_color': '#1e293b',
            'title_color': '#4f46e5',
            'grid_color': '#e2e8f0',
            'accent_primary': '#4f46e5',
            'accent_secondary': '#7c3aed',
            'accent_success': '#16a34a',
            'accent_warning': '#d97706',
            'font_family': 'Inter, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif',
            'colorscale': ['#4f46e5', '#7c3aed', '#9333ea', '#c026d3', '#db2777']
        }

def apply_chart_theme(fig, title=None, height=500, show_legend=True):
    """Apply consistent theme-aware styling to all charts - Professional design"""
    theme = get_chart_theme_colors()
    is_dark = st.session_state.get('theme', 'dark') == 'dark'

    # Professional layout configuration
    layout_config = {
        'plot_bgcolor': theme['bg_color'],
        'paper_bgcolor': theme['paper_color'],
        'font': {
            'family': theme['font_family'],
            'size': 13,
            'color': theme['text_color']
        },
        'title': {
            'font': {
                'size': 20,
                'color': theme['title_color'],
                'family': theme['font_family'],
                'weight': 600
            },
            'x': 0.5,
            'xanchor': 'center',
            'y': 0.95,
            'yanchor': 'top'
        },
        'xaxis': {
            'gridcolor': theme['grid_color'],
            'gridwidth': 1,
            'color': theme['text_color'],
            'title_font': {'color': theme['text_color'], 'size': 14},
            'tickfont': {'color': theme['text_color'], 'size': 12},
            'linecolor': theme['grid_color'],
            'showgrid': True,
            'zeroline': False
        },
        'yaxis': {
            'gridcolor': theme['grid_color'],
            'gridwidth': 1,
            'color': theme['text_color'],
            'title_font': {'color': theme['text_color'], 'size': 14},
            'tickfont': {'color': theme['text_color'], 'size': 12},
            'linecolor': theme['grid_color'],
            'showgrid': True,
            'zeroline': False
        },
        'height': height,
        'showlegend': show_legend,
        'legend': {
            'font': {'color': theme['text_color'], 'size': 12},
            'bgcolor': 'rgba(0,0,0,0.02)' if not is_dark else 'rgba(255,255,255,0.02)',
            'bordercolor': theme['grid_color'],
            'borderwidth': 1
        },
        'margin': {'l': 60, 'r': 100, 't': 60, 'b': 50},  # Extra right margin for colorbar
        'hoverlabel': {
            'bgcolor': theme['paper_color'],
            'bordercolor': theme['accent_primary'],
            'font': {'color': theme['text_color'], 'family': theme['font_family'], 'size': 13}
        },
        'hovermode': 'closest'
    }

    if title:
        layout_config['title']['text'] = title

    fig.update_layout(**layout_config)

    # Update trace colors for consistency
    for trace in fig.data:
        # Update bar chart text colors
        if hasattr(trace, 'textfont'):
            trace.textfont.color = theme['text_color']
        # Update pie chart text
        if trace.type == 'pie':
            trace.textfont = dict(color=theme['text_color'], size=13)
            trace.outsidetextfont = dict(color=theme['text_color'], size=12)

    # Update annotations if they exist (for pie charts, donut center text)
    if fig.layout.annotations:
        for annotation in fig.layout.annotations:
            annotation.font.color = theme['text_color']

    # Update colorbar if exists
    for trace in fig.data:
        if hasattr(trace, 'marker') and hasattr(trace.marker, 'colorbar'):
            if trace.marker.colorbar:
                trace.marker.colorbar.tickfont = dict(color=theme['text_color'])
                trace.marker.colorbar.title.font = dict(color=theme['text_color'])

    return fig

# Load environment
load_dotenv()

# Try to import Gemini
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'

# Page configuration
st.set_page_config(
    page_title="IPL Cricket Analytics",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Create directory for generated images
GENERATED_IMAGES_DIR = Path("generated_images")
GENERATED_IMAGES_DIR.mkdir(exist_ok=True)

# ==================== DATABASE FUNCTIONS ====================

@st.cache_resource
def get_database_connection():
    """Get database connection"""
    db_path = Path("data/cricket_analytics.db")
    if not db_path.exists():
        st.error("❌ Database not found! Run `python scripts/create_database.py` first.")
        st.stop()
    return sqlite3.connect(db_path, check_same_thread=False)

@st.cache_data(ttl=CHART_CONFIG['cache_ttl'], show_spinner=False)
def load_teams():
    """Load teams data - cached for performance"""
    conn = get_database_connection()
    return pd.read_sql_query("SELECT * FROM teams ORDER BY team_name", conn)

@st.cache_data(ttl=CHART_CONFIG['cache_ttl'], show_spinner=False)
def load_matches():
    """Load all matches - cached for performance"""
    conn = get_database_connection()
    return pd.read_sql_query("SELECT * FROM matches ORDER BY match_date DESC", conn)

@st.cache_data(ttl=CHART_CONFIG['cache_ttl'], show_spinner=False)
def get_team_stats():
    """Get overall team statistics"""
    conn = get_database_connection()
    return pd.read_sql_query("""
        WITH team_matches AS (
            SELECT team1_name as team FROM matches
            UNION ALL SELECT team2_name as team FROM matches
        ),
        team_wins AS (
            SELECT match_winner_name as team FROM matches WHERE match_winner_name IS NOT NULL
        )
        SELECT 
            tm.team,
            COUNT(*) as matches_played,
            COALESCE(tw.wins, 0) as wins,
            COUNT(*) - COALESCE(tw.wins, 0) as losses,
            ROUND(100.0 * COALESCE(tw.wins, 0) / COUNT(*), 1) as win_percentage
        FROM team_matches tm
        LEFT JOIN (SELECT team, COUNT(*) as wins FROM team_wins GROUP BY team) tw 
        ON tm.team = tw.team
        WHERE tm.team IS NOT NULL
        GROUP BY tm.team
        ORDER BY win_percentage DESC
    """, conn)

# ==================== DATA QUALITY & VALIDATION ====================

@st.cache_data(ttl=CHART_CONFIG['cache_ttl'], show_spinner=False)
def get_data_quality_report() -> Dict[str, Any]:
    """Generate comprehensive data quality metrics"""
    try:
        conn = get_database_connection()
        matches = load_matches()
        
        # Check deliveries data
        try:
            deliveries_match_ids = pd.read_sql_query(
                "SELECT DISTINCT match_id FROM deliveries", conn
            )['match_id'].tolist()
            matches_with_deliveries = len(matches[matches['match_id'].isin(deliveries_match_ids)])
        except:
            matches_with_deliveries = 0
            deliveries_match_ids = []
        
        return {
            'total_matches': len(matches),
            'matches_with_deliveries': matches_with_deliveries,
            'delivery_coverage': round(100.0 * matches_with_deliveries / len(matches), 1) if len(matches) > 0 else 0,
            'null_venues': int(matches['venue'].isna().sum()),
            'null_winners': int(matches['match_winner_name'].isna().sum()),
            'null_toss_winners': int(matches['toss_winner_name'].isna().sum()),
            'date_range': (matches['match_date'].min(), matches['match_date'].max()) if not matches.empty else (None, None),
            'seasons': matches['season'].nunique() if not matches.empty else 0,
            'teams': matches['team1_name'].nunique() if not matches.empty else 0,
            'venues': matches['venue'].nunique() if not matches.empty else 0,
            'last_updated': datetime.now(),
            'data_quality_score': calculate_data_quality_score(matches, matches_with_deliveries)
        }
    except Exception as e:
        logger.error(f"Error generating data quality report: {e}")
        return {
            'total_matches': 0,
            'matches_with_deliveries': 0,
            'delivery_coverage': 0,
            'data_quality_score': 0,
            'error': str(e)
        }

def calculate_data_quality_score(matches: pd.DataFrame, matches_with_deliveries: int) -> float:
    """Calculate overall data quality score (0-100)"""
    if matches.empty:
        return 0.0
    
    total = len(matches)
    score = 100.0
    
    # Deduct points for missing data
    null_venues_pct = matches['venue'].isna().sum() / total * 100
    null_winners_pct = matches['match_winner_name'].isna().sum() / total * 100
    delivery_coverage = matches_with_deliveries / total * 100 if total > 0 else 0
    
    score -= null_venues_pct * 0.5  # Venue missing is minor
    score -= null_winners_pct * 2.0  # Winner missing is more important
    score -= (100 - delivery_coverage) * 0.3  # Delivery data is important but not critical
    
    return max(0.0, min(100.0, score))

def safe_query_execution(query: str, conn, error_message: str = "Unable to fetch data", 
                        return_empty_df: bool = True) -> pd.DataFrame:
    """Execute query with proper error handling and user-friendly messages"""
    try:
        result = pd.read_sql_query(query, conn)
        if result.empty and return_empty_df:
            return pd.DataFrame()
        return result
    except sqlite3.OperationalError as e:
        logger.error(f"Database operational error: {e}")
        st.error(f"❌ Database Error: {error_message}")
        st.info("💡 This might be a query syntax issue. Try refreshing the page or contact support.")
        if return_empty_df:
            return pd.DataFrame()
        raise
    except sqlite3.IntegrityError as e:
        logger.error(f"Database integrity error: {e}")
        st.error(f"❌ Data Integrity Error: {error_message}")
        st.info("💡 There might be an issue with the database structure.")
        if return_empty_df:
            return pd.DataFrame()
        raise
    except Exception as e:
        logger.error(f"Unexpected query error: {e}\nQuery: {query[:200]}")
        st.error(f"❌ Unexpected Error: {error_message}")
        st.info("💡 Try refreshing the page. If the issue persists, check the logs.")
        if return_empty_df:
            return pd.DataFrame()
        raise

# ==================== EXPORT FUNCTIONALITY ====================

def export_dataframe_to_csv(df: pd.DataFrame, filename: str = "ipl_data") -> bytes:
    """Export dataframe to CSV bytes"""
    return df.to_csv(index=False).encode('utf-8')

def export_dataframe_to_excel(df: pd.DataFrame, filename: str = "ipl_data") -> bytes:
    """Export dataframe to Excel bytes"""
    try:
        from io import BytesIO
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Data')
        output.seek(0)
        return output.getvalue()
    except ImportError:
        st.warning("⚠️ openpyxl not installed. Install with: pip install openpyxl")
        return None

def add_export_buttons(df: pd.DataFrame, key_prefix: str = "export"):
    """Add export buttons for dataframe"""
    if df.empty:
        return
    
    col1, col2 = st.columns(2)
    with col1:
        csv_data = export_dataframe_to_csv(df)
        st.download_button(
            "📥 Export as CSV",
            csv_data,
            f"{key_prefix}_data.csv",
            "text/csv",
            key=f"{key_prefix}_csv"
        )
    with col2:
        excel_data = export_dataframe_to_excel(df)
        if excel_data:
            st.download_button(
                "📥 Export as Excel",
                excel_data,
                f"{key_prefix}_data.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key=f"{key_prefix}_excel"
            )

# ==================== ADVANCED METRICS ====================

@st.cache_data(ttl=CHART_CONFIG['cache_ttl'])
def calculate_net_run_rate(team_name: str, season: Optional[int] = None) -> float:
    """Calculate Net Run Rate (NRR) for a team"""
    try:
        conn = get_database_connection()
        season_filter = f"AND season = {season}" if season else ""
        
        query = f"""
        WITH team_matches AS (
            SELECT match_id, team1_name, team2_name, match_winner_name
            FROM matches
            WHERE (team1_name = '{team_name}' OR team2_name = '{team_name}')
            {season_filter}
        ),
        team_runs AS (
            SELECT 
                d.match_id,
                CASE 
                    WHEN m.team1_name = '{team_name}' AND d.innings = 1 THEN SUM(d.total_runs)
                    WHEN m.team2_name = '{team_name}' AND d.innings = 2 THEN SUM(d.total_runs)
                    ELSE 0
                END as runs_scored,
                CASE 
                    WHEN m.team1_name = '{team_name}' AND d.innings = 2 THEN SUM(d.total_runs)
                    WHEN m.team2_name = '{team_name}' AND d.innings = 1 THEN SUM(d.total_runs)
                    ELSE 0
                END as runs_conceded
            FROM deliveries d
            JOIN team_matches m ON d.match_id = m.match_id
            GROUP BY d.match_id, d.innings
        )
        SELECT 
            SUM(runs_scored) as total_runs_scored,
            SUM(runs_conceded) as total_runs_conceded,
            COUNT(DISTINCT match_id) as matches_played
        FROM team_runs
        """
        result = safe_query_execution(query, conn, "Unable to calculate NRR")
        if result.empty or result.iloc[0]['matches_played'] == 0:
            return 0.0
        
        runs_scored = result.iloc[0]['total_runs_scored'] or 0
        runs_conceded = result.iloc[0]['total_runs_conceded'] or 0
        matches = result.iloc[0]['matches_played']
        
        if matches == 0:
            return 0.0
        
        # NRR = (Total Runs Scored / Total Overs Faced) - (Total Runs Conceded / Total Overs Bowled)
        # Simplified: (Runs Scored - Runs Conceded) / Matches (approximation)
        nrr = (runs_scored - runs_conceded) / matches / 20.0  # Divide by 20 for overs approximation
        return round(nrr, 3)
    except Exception as e:
        logger.error(f"Error calculating NRR: {e}")
        return 0.0

@st.cache_data(ttl=CHART_CONFIG['cache_ttl'], show_spinner=False)
def get_powerplay_stats(team_name: str, season: Optional[int] = None) -> Dict[str, Any]:
    """Get powerplay (overs 1-6) statistics"""
    try:
        conn = get_database_connection()
        season_filter = f"AND m.season = {season}" if season else ""
        
        query = f"""
        SELECT 
            AVG(CASE WHEN d.over_number <= 6 THEN d.total_runs ELSE 0 END) as avg_powerplay_runs,
            AVG(CASE WHEN d.over_number > 15 THEN d.total_runs ELSE 0 END) as avg_death_runs,
            SUM(CASE WHEN d.over_number <= 6 AND d.is_wicket = 1 THEN 1 ELSE 0 END) as powerplay_wickets,
            SUM(CASE WHEN d.over_number > 15 AND d.is_wicket = 1 THEN 1 ELSE 0 END) as death_wickets
        FROM deliveries d
        JOIN matches m ON d.match_id = m.match_id
        WHERE (m.team1_name = '{team_name}' OR m.team2_name = '{team_name}')
        {season_filter}
        """
        result = safe_query_execution(query, conn, "Unable to fetch powerplay stats")
        if result.empty:
            return {'avg_powerplay_runs': 0, 'avg_death_runs': 0, 'powerplay_wickets': 0, 'death_wickets': 0}
        return result.iloc[0].to_dict()
    except Exception as e:
        logger.error(f"Error calculating powerplay stats: {e}")
        return {'avg_powerplay_runs': 0, 'avg_death_runs': 0, 'powerplay_wickets': 0, 'death_wickets': 0}

@st.cache_data(ttl=CHART_CONFIG['cache_ttl'], show_spinner=False)
def get_chase_vs_defend_stats(team_name: str) -> Dict[str, Any]:
    """Get chase vs defend success rates"""
    try:
        conn = get_database_connection()
        query = f"""
        WITH team_matches AS (
            SELECT match_id, team1_name, team2_name, toss_winner_name, toss_decision, match_winner_name
            FROM matches
            WHERE team1_name = '{team_name}' OR team2_name = '{team_name}'
        )
        SELECT 
            SUM(CASE 
                WHEN (team1_name = '{team_name}' AND toss_decision = 'bat' AND match_winner_name = '{team_name}') OR
                     (team2_name = '{team_name}' AND toss_decision = 'field' AND match_winner_name = '{team_name}')
                THEN 1 ELSE 0 END) as defend_wins,
            SUM(CASE 
                WHEN (team1_name = '{team_name}' AND toss_decision = 'bat') OR
                     (team2_name = '{team_name}' AND toss_decision = 'field')
                THEN 1 ELSE 0 END) as defend_matches,
            SUM(CASE 
                WHEN (team1_name = '{team_name}' AND toss_decision = 'field' AND match_winner_name = '{team_name}') OR
                     (team2_name = '{team_name}' AND toss_decision = 'bat' AND match_winner_name = '{team_name}')
                THEN 1 ELSE 0 END) as chase_wins,
            SUM(CASE 
                WHEN (team1_name = '{team_name}' AND toss_decision = 'field') OR
                     (team2_name = '{team_name}' AND toss_decision = 'bat')
                THEN 1 ELSE 0 END) as chase_matches
        FROM team_matches
        """
        result = safe_query_execution(query, conn, "Unable to fetch chase/defend stats")
        if result.empty:
            return {'defend_win_rate': 0, 'chase_win_rate': 0}
        
        row = result.iloc[0]
        defend_wins = row['defend_wins'] or 0
        defend_matches = row['defend_matches'] or 1
        chase_wins = row['chase_wins'] or 0
        chase_matches = row['chase_matches'] or 1
        
        return {
            'defend_win_rate': round(100.0 * defend_wins / defend_matches, 1) if defend_matches > 0 else 0,
            'chase_win_rate': round(100.0 * chase_wins / chase_matches, 1) if chase_matches > 0 else 0,
            'defend_wins': int(defend_wins),
            'defend_matches': int(defend_matches),
            'chase_wins': int(chase_wins),
            'chase_matches': int(chase_matches)
        }
    except Exception as e:
        logger.error(f"Error calculating chase/defend stats: {e}")
        return {'defend_win_rate': 0, 'chase_win_rate': 0}

# ==================== IMAGE HELPER FUNCTIONS ====================

def plotly_to_image_bytes(fig, width=1200, height=675):
    """Convert Plotly figure to image bytes"""
    try:
        import plotly.io as pio
        # Try to set kaleido as engine (needed for image export)
        try:
            pio.kaleido.scope.mathjax = None
        except:
            pass
        return pio.to_image(fig, format='png', width=width, height=height, engine='kaleido')
    except ImportError as e:
        st.error("❌ Install kaleido: `pip install kaleido`")
        st.info("Kaleido is required to export Plotly charts as images")
        return None
    except Exception as e:
        st.warning(f"Could not convert chart to image: {e}")
        st.info("💡 The chart is still visible above. To enable downloads, install: `pip install kaleido`")
        return None

def add_watermark_to_image(image_bytes, text="@rkjat65"):
    """Add watermark to image"""
    try:
        img = Image.open(io.BytesIO(image_bytes))
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        overlay = Image.new('RGBA', img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(overlay)
        
        try:
            font = ImageFont.truetype("arial.ttf", 18)
        except:
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
            except:
                font = ImageFont.load_default()
        
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        margin = 20
        x = img.width - text_width - margin
        y = img.height - text_height - margin
        
        draw.text((x + 2, y + 2), text, fill=(0, 0, 0, 128), font=font)
        draw.text((x, y), text, fill=(255, 255, 255, 200), font=font)
        
        watermarked = Image.alpha_composite(img, overlay).convert('RGB')
        
        output = io.BytesIO()
        watermarked.save(output, format='PNG', quality=95)
        output.seek(0)
        return output.getvalue()
    except Exception as e:
        st.warning(f"Watermark warning: {e}")
        return image_bytes

def save_image_to_folder(image_bytes, prefix="ai_generated"):
    """Save image locally"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp}.png"
        filepath = GENERATED_IMAGES_DIR / filename
        with open(filepath, 'wb') as f:
            f.write(image_bytes)
        return str(filepath)
    except Exception as e:
        st.warning(f"Could not save: {e}")
        return None

def prepare_data_context(dataframe, max_rows=20):
    """Prepare data for AI prompt"""
    if dataframe is None or len(dataframe) == 0:
        return ""
    df_subset = dataframe.head(max_rows)
    return f"""
Dataset Information:
- Total Rows: {len(dataframe)}
- Columns: {', '.join(dataframe.columns.tolist())}

Data (first {min(len(dataframe), max_rows)} rows):
{df_subset.to_string(index=False)}
"""

def get_chart_info(fig):
    """Extract chart information"""
    try:
        chart_type = fig.data[0].type if len(fig.data) > 0 else "unknown"
        layout = fig.layout
        return f"""
Chart Type: {chart_type}
Title: {layout.title.text if layout.title else "No title"}
"""
    except:
        return "Chart info not available"

# ==================== PLOTLY CHART GENERATOR ====================

def detect_best_chart_type(dataframe):
    """Detect best chart type from data"""
    if len(dataframe.columns) < 2:
        return "table"
    numeric_cols = dataframe.select_dtypes(include=['number']).columns.tolist()
    text_cols = dataframe.select_dtypes(include=['object']).columns.tolist()
    if len(numeric_cols) >= 1 and len(text_cols) >= 1:
        return "bar"
    elif len(numeric_cols) >= 2:
        return "scatter"
    return "table"

def generate_plotly_chart(dataframe, chart_type=None, title="IPL Data Visualization"):
    """Generate Plotly chart from data"""
    if dataframe is None or len(dataframe) == 0:
        return None
    
    if chart_type is None:
        chart_type = detect_best_chart_type(dataframe)
    
    numeric_cols = dataframe.select_dtypes(include=['number']).columns.tolist()
    text_cols = dataframe.select_dtypes(include=['object']).columns.tolist()
    
    try:
        if chart_type == "bar":
            fig = px.bar(dataframe,
                y=text_cols[0] if text_cols else dataframe.columns[0],
                x=numeric_cols[0] if numeric_cols else dataframe.columns[1],
                title=title, orientation='h',
                color=numeric_cols[0] if numeric_cols else None,
                color_continuous_scale='Viridis')
        elif chart_type == "pie":
            fig = px.pie(dataframe,
                names=text_cols[0] if text_cols else dataframe.columns[0],
                values=numeric_cols[0] if numeric_cols else dataframe.columns[1],
                title=title)
        elif chart_type == "line":
            fig = px.line(dataframe,
                x=dataframe.columns[0],
                y=numeric_cols[0] if numeric_cols else dataframe.columns[1],
                title=title, markers=True)
        else:
            fig = px.bar(dataframe,
                x=dataframe.columns[0],
                y=numeric_cols[0] if numeric_cols else dataframe.columns[1],
                title=title)

        # Apply theme-aware styling
        fig = apply_chart_theme(fig, title=title, height=500, show_legend=False)
        return fig
    except Exception as e:
        st.error(f"Error generating chart: {e}")
        return None

def get_chart_type_options(dataframe):
    """Get available chart types for data"""
    options = []
    numeric_cols = dataframe.select_dtypes(include=['number']).columns.tolist()
    text_cols = dataframe.select_dtypes(include=['object']).columns.tolist()
    
    if len(text_cols) >= 1 and len(numeric_cols) >= 1:
        options.extend([("bar", "📊 Bar Chart"), ("pie", "🥧 Pie Chart")])
    if len(numeric_cols) >= 1:
        options.append(("line", "📈 Line Chart"))
    if len(numeric_cols) >= 2:
        options.append(("scatter", "🔵 Scatter Plot"))
    if not options:
        options.append(("bar", "📊 Bar Chart"))
    return options

# ==================== ADVANCED VISUALIZATIONS ====================

def create_heatmap(data: pd.DataFrame, x_col: str, y_col: str, values_col: str, 
                   title: str = "Heatmap", height: int = None) -> go.Figure:
    """Create a heatmap visualization with improved layout"""
    if height is None:
        height = CHART_CONFIG['default_height']
    
    pivot_data = data.pivot_table(values=values_col, index=y_col, columns=x_col, aggfunc='mean', fill_value=0)
    
    # Truncate long venue names for better display
    if x_col == 'Venue':
        pivot_data.columns = [col[:25] + '...' if len(str(col)) > 25 else str(col) for col in pivot_data.columns]
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot_data.values,
        x=pivot_data.columns,
        y=pivot_data.index,
        colorscale='RdYlGn',  # Better color scheme: Red-Yellow-Green
        text=pivot_data.values,
        texttemplate='%{text:.1f}%',
        textfont={"size": 11, "color": "white"},
        colorbar=dict(
            title=dict(text=values_col, font=dict(size=12)),
            len=0.6,
            y=0.5
        ),
        hovertemplate='<b>%{y}</b> at <b>%{x}</b><br>Win %: %{z:.1f}%<extra></extra>'
    ))
    
    theme = get_chart_theme_colors()
    fig.update_layout(
        title=dict(text=title, font=dict(size=16)),
        xaxis=dict(
            title=x_col,
            tickangle=-45,
            tickfont=dict(size=10)
        ),
        yaxis=dict(
            title=y_col,
            tickfont=dict(size=11)
        ),
        height=height + 100,  # Extra height for rotated labels
        margin=dict(l=100, r=100, t=80, b=150)  # More margin for labels
    )
    
    return apply_chart_theme(fig, title=title, height=height + 100, show_legend=True)

def create_radar_chart(categories: list, values: list, title: str = "Radar Chart", 
                       height: int = None) -> go.Figure:
    """Create a radar/spider chart for multi-dimensional comparison"""
    if height is None:
        height = CHART_CONFIG['default_height']
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Performance'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max(values) * 1.2 if values else 100]
            )),
        showlegend=True,
        title=title,
        height=height
    )
    
    return apply_chart_theme(fig, title=title, height=height, show_legend=True)

def create_box_plot(data: pd.DataFrame, x_col: str, y_col: str, 
                    title: str = "Distribution Analysis", height: int = None) -> go.Figure:
    """Create a box plot for distribution analysis"""
    if height is None:
        height = CHART_CONFIG['default_height']
    
    fig = go.Figure()
    
    for category in data[x_col].unique():
        category_data = data[data[x_col] == category][y_col]
        fig.add_trace(go.Box(
            y=category_data,
            name=str(category),
            boxmean='sd'
        ))
    
    fig.update_layout(
        title=title,
        xaxis_title=x_col,
        yaxis_title=y_col,
        height=height
    )
    
    return apply_chart_theme(fig, title=title, height=height, show_legend=False)

def create_correlation_matrix(data: pd.DataFrame, title: str = "Correlation Matrix", 
                               height: int = None) -> go.Figure:
    """Create a correlation matrix heatmap"""
    if height is None:
        height = CHART_CONFIG['default_height']
    
    numeric_data = data.select_dtypes(include=['number'])
    if numeric_data.empty:
        return None
    
    corr_matrix = numeric_data.corr()
    
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        colorscale='RdBu',
        zmid=0,
        text=corr_matrix.values,
        texttemplate='%{text:.2f}',
        textfont={"size": 10},
        colorbar=dict(title="Correlation")
    ))
    
    fig.update_layout(
        title=title,
        height=height
    )
    
    return apply_chart_theme(fig, title=title, height=height, show_legend=True)

# ==================== UI HELPERS ====================

def add_tooltip(text: str, tooltip_text: str) -> str:
    """Add HTML tooltip to text"""
    return f"""
    <span title="{tooltip_text}" style="cursor: help; border-bottom: 1px dotted; position: relative;">
        {text} <span style="font-size: 0.8em; color: #666;">ℹ️</span>
    </span>
    """

def show_metric_with_tooltip(label: str, value: Any, tooltip: str = "", 
                             delta: Optional[str] = None, help_text: str = ""):
    """Display metric with optional tooltip and delta"""
    if tooltip or help_text:
        tooltip_text = tooltip or help_text
        label_with_tooltip = add_tooltip(label, tooltip_text)
        st.markdown(f"<div style='margin-bottom: 0.5rem;'>{label_with_tooltip}</div>", unsafe_allow_html=True)
        st.metric("", value, delta=delta)
    else:
        st.metric(label, value, delta=delta)

def export_chart_as_image(fig, filename: str = "chart") -> bytes:
    """Export Plotly chart as PNG image"""
    try:
        import plotly.io as pio
        try:
            pio.kaleido.scope.mathjax = None
        except:
            pass
        return pio.to_image(fig, format='png', width=1200, height=675, engine='kaleido')
    except ImportError:
        return None
    except Exception as e:
        logger.warning(f"Could not export chart: {e}")
        return None

def add_chart_export_button(fig, chart_title: str, key_prefix: str = "chart"):
    """Add export button below a chart - compact single line layout"""
    if fig is None:
        return
    
    # Use a more compact layout with smaller buttons
    col1, col2 = st.columns([1, 1])
    with col1:
        # Export as PNG
        img_bytes = export_chart_as_image(fig, chart_title)
        if img_bytes:
            st.download_button(
                "📥 PNG",
                img_bytes,
                f"{chart_title.replace(' ', '_')}.png",
                "image/png",
                key=f"{key_prefix}_png",
                use_container_width=True
            )
    with col2:
        # Export as HTML
        html_str = fig.to_html(include_plotlyjs='cdn')
        st.download_button(
            "📥 HTML",
            html_str.encode('utf-8'),
            f"{chart_title.replace(' ', '_')}.html",
            "text/html",
            key=f"{key_prefix}_html",
            use_container_width=True
        )

# ==================== GEMINI AI FUNCTIONS ====================

def initialize_gemini():
    """Initialize Gemini API"""
    if not GEMINI_API_KEY:
        return False
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        return True
    except:
        return False

def generate_sql_from_question(question):
    """Generate SQL from natural language with smart preprocessing"""
    try:
        # Check for common patterns and provide better SQL directly
        question_lower = question.lower()
        
        # Pattern: "Compare Team A vs Team B"
        if 'compare' in question_lower and ' vs ' in question_lower:
            # Extract team names
            parts = question_lower.split(' vs ')
            if len(parts) == 2:
                team1 = parts[0].replace('compare', '').strip()
                team2 = parts[1].strip()
                
                # Map common abbreviations to full names
                team_map = {
                    'mi': 'Mumbai Indians',
                    'mumbai': 'Mumbai Indians',
                    'mumbai indians': 'Mumbai Indians',
                    'csk': 'Chennai Super Kings',
                    'chennai': 'Chennai Super Kings',
                    'chennai super kings': 'Chennai Super Kings',
                    'rcb': 'Royal Challengers Bangalore',
                    'bangalore': 'Royal Challengers Bangalore',
                    'kkr': 'Kolkata Knight Riders',
                    'kolkata': 'Kolkata Knight Riders',
                    'dc': 'Delhi Capitals',
                    'delhi': 'Delhi Capitals',
                    'pbks': 'Punjab Kings',
                    'punjab': 'Punjab Kings',
                    'rr': 'Rajasthan Royals',
                    'rajasthan': 'Rajasthan Royals',
                    'srh': 'Sunrisers Hyderabad',
                    'hyderabad': 'Sunrisers Hyderabad',
                    'gt': 'Gujarat Titans',
                    'gujarat': 'Gujarat Titans',
                    'lsg': 'Lucknow Super Giants',
                    'lucknow': 'Lucknow Super Giants'
                }
                
                team1_full = team_map.get(team1, team1.title())
                team2_full = team_map.get(team2, team2.title())
                
                # Return proper comparison SQL
                return f"""
SELECT 
    '{team1_full}' as team,
    COUNT(*) as total_matches,
    SUM(CASE WHEN match_winner_name = '{team1_full}' THEN 1 ELSE 0 END) as wins,
    ROUND(100.0 * SUM(CASE WHEN match_winner_name = '{team1_full}' THEN 1 ELSE 0 END) / COUNT(*), 1) as win_percentage
FROM matches
WHERE team1_name = '{team1_full}' OR team2_name = '{team1_full}'
UNION ALL
SELECT 
    '{team2_full}' as team,
    COUNT(*) as total_matches,
    SUM(CASE WHEN match_winner_name = '{team2_full}' THEN 1 ELSE 0 END) as wins,
    ROUND(100.0 * SUM(CASE WHEN match_winner_name = '{team2_full}' THEN 1 ELSE 0 END) / COUNT(*), 1) as win_percentage
FROM matches
WHERE team1_name = '{team2_full}' OR team2_name = '{team2_full}'
                """.strip()
        
        # Pattern: "Head to head Team A vs Team B"
        if ('head' in question_lower or 'h2h' in question_lower) and ' vs ' in question_lower:
            parts = question_lower.replace('head to head', '').replace('h2h', '').split(' vs ')
            if len(parts) == 2:
                team1 = parts[0].strip()
                team2 = parts[1].strip()
                
                team_map = {
                    'mi': 'Mumbai Indians', 'mumbai': 'Mumbai Indians', 'mumbai indians': 'Mumbai Indians',
                    'csk': 'Chennai Super Kings', 'chennai': 'Chennai Super Kings', 'chennai super kings': 'Chennai Super Kings',
                    'rcb': 'Royal Challengers Bangalore', 'kkr': 'Kolkata Knight Riders',
                    'dc': 'Delhi Capitals', 'pbks': 'Punjab Kings', 'rr': 'Rajasthan Royals',
                    'srh': 'Sunrisers Hyderabad', 'gt': 'Gujarat Titans', 'lsg': 'Lucknow Super Giants'
                }
                
                team1_full = team_map.get(team1, team1.title())
                team2_full = team_map.get(team2, team2.title())
                
                return f"""
SELECT 
    '{team1_full}' as team,
    SUM(CASE WHEN match_winner_name = '{team1_full}' THEN 1 ELSE 0 END) as wins
FROM matches
WHERE (team1_name = '{team1_full}' AND team2_name = '{team2_full}')
   OR (team1_name = '{team2_full}' AND team2_name = '{team1_full}')
UNION ALL
SELECT 
    '{team2_full}' as team,
    SUM(CASE WHEN match_winner_name = '{team2_full}' THEN 1 ELSE 0 END) as wins
FROM matches
WHERE (team1_name = '{team1_full}' AND team2_name = '{team2_full}')
   OR (team1_name = '{team2_full}' AND team2_name = '{team1_full}')
                """.strip()
        
        # Otherwise use Gemini for SQL generation
        model = genai.GenerativeModel('gemini-3-pro-preview')  # Use latest text model for SQL
        schema = """Database Schema:

Table: teams (team_id, team_name, short_name, is_active)
Table: matches (match_id, season, match_date, venue, city, team1_name, team2_name, 
               toss_winner_name, toss_decision, match_winner_name, win_by_runs, 
               win_by_wickets, player_of_match, result)
Table: deliveries (match_id, innings, batter, non_striker, bowler, over_number, ball_number,
                   batter_runs, extras, total_runs, is_wicket, player_out, wicket_kind)

CRITICAL RULES FOR PLAYER QUERIES:
- Player names are stored as TEXT in 'batter' and 'bowler' columns (e.g., 'V Kohli', 'RG Sharma')
- NEVER query player_id or team_batting_id - query the actual NAME columns (batter, bowler)
- For run scorers: SELECT batter as player, SUM(batter_runs) as runs FROM deliveries
- For wicket takers: SELECT bowler as player, SUM(is_wicket) as wickets FROM deliveries
- ALWAYS use column aliases to make output readable (e.g., 'total_runs' not 'sum')

Team name rules:
- Full names: 'Mumbai Indians', 'Chennai Super Kings', 'Royal Challengers Bangalore'
- NEVER use team IDs in SELECT - always use team_name

Data: 1,169 matches, 18 seasons (2008-2025), 16 teams, 200k+ deliveries"""
        
        prompt = f"""You are an expert SQL developer for an IPL cricket database.

{schema}

User Question: {question}

CRITICAL: 
- For player statistics, query 'batter' and 'bowler' TEXT columns (NOT IDs)
- For team statistics, query 'team_name' TEXT columns (NOT IDs)
- Return ONLY valid SQL - no markdown, no explanations
- Use readable column aliases (player, total_runs, total_wickets)
- Add LIMIT 20 for large result sets

Examples of CORRECT queries:
✅ SELECT batter as player, SUM(batter_runs) as total_runs FROM deliveries GROUP BY batter ORDER BY total_runs DESC LIMIT 10
✅ SELECT bowler as player, SUM(is_wicket) as total_wickets FROM deliveries GROUP BY bowler ORDER BY total_wickets DESC LIMIT 10
✅ SELECT team_name as team, COUNT(*) as matches FROM matches WHERE team1_name = 'Team' OR team2_name = 'Team'

Examples of WRONG queries:
❌ SELECT team_batting_id, player_id FROM deliveries (NEVER query IDs)
❌ SELECT COUNT(*) FROM deliveries (missing GROUP BY and readable columns)

Generate the SQL now:"""
        
        response = model.generate_content(prompt)
        sql = response.text.strip()
        
        # Remove ALL markdown artifacts
        sql = sql.replace('```sql', '')
        sql = sql.replace('```sqlite', '')
        sql = sql.replace('```SQL', '')
        sql = sql.replace('```', '')
        sql = sql.replace('`', '')
        
        # Remove common prefixes
        sql = sql.replace('sqlite', '', 1)
        sql = sql.replace('ite', '', 1)
        sql = sql.replace('SQLite', '', 1)
        
        # Clean up whitespace
        sql = sql.strip()
        
        # Ensure it starts with SELECT, WITH, INSERT, UPDATE, or DELETE
        if not any(sql.upper().startswith(kw) for kw in ['SELECT', 'WITH', 'INSERT', 'UPDATE', 'DELETE']):
            for keyword in ['SELECT', 'WITH', 'INSERT', 'UPDATE', 'DELETE']:
                if keyword in sql.upper():
                    idx = sql.upper().index(keyword)
                    sql = sql[idx:]
                    break
        
        return sql
    except Exception as e:
        return f"Error: {e}"

def generate_insight_from_data(question, data):
    """Generate insights from data"""
    try:
        model = genai.GenerativeModel('gemini-3-pro-preview')  # Use text model for analysis
        prompt = f"""You are a cricket analyst.

User asked: {question}
Data: {data.head(10).to_string() if len(data) > 0 else "No results"}

Provide a 2-3 sentence analysis with the answer and one interesting insight."""
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Analysis unavailable: {e}"

def load_database_data_options():
    """Pre-configured data queries"""
    return {
        "Team Statistics": {
            "query": """
                SELECT t.team_name, COUNT(m.match_id) as total_matches,
                    SUM(CASE WHEN m.match_winner_name = t.team_name THEN 1 ELSE 0 END) as wins,
                    ROUND(100.0 * SUM(CASE WHEN m.match_winner_name = t.team_name THEN 1 ELSE 0 END) / COUNT(m.match_id), 1) as win_percentage
                FROM teams t
                LEFT JOIN matches m ON t.team_name = m.team1_name OR t.team_name = m.team2_name
                WHERE t.is_active = 1
                GROUP BY t.team_name
                ORDER BY win_percentage DESC
            """,
            "description": "Overall statistics for all active teams"
        },
        "Toss Impact": {
            "query": """
                SELECT toss_decision, COUNT(*) as total,
                    SUM(CASE WHEN toss_winner_id = match_winner_id THEN 1 ELSE 0 END) as wins,
                    ROUND(100.0 * SUM(CASE WHEN toss_winner_id = match_winner_id THEN 1 ELSE 0 END) / COUNT(*), 1) as win_pct
                FROM matches
                WHERE toss_decision IS NOT NULL
                GROUP BY toss_decision
            """,
            "description": "Win rates: bat vs field first"
        },
        "Top Venues": {
            "query": """
                SELECT venue, city, COUNT(*) as matches
                FROM matches WHERE venue IS NOT NULL
                GROUP BY venue, city ORDER BY matches DESC LIMIT 10
            """,
            "description": "Top 10 stadiums by matches"
        },
        "Recent Seasons": {
            "query": """
                SELECT season, COUNT(*) as matches, 
                    COUNT(DISTINCT venue) as venues,
                    COUNT(DISTINCT team1_name) as teams
                FROM matches WHERE season >= 2020
                GROUP BY season ORDER BY season DESC
            """,
            "description": "Recent IPL seasons (2020+)"
        }
    }

# ==================== PROFESSIONAL CSS ====================

def load_css():
    """Load professional CSS - Clean Modern Theme"""

    is_dark = st.session_state.get('theme', 'dark') == 'dark'

    if is_dark:
        colors = {
            'bg_main': '#0d1117',
            'bg_secondary': '#161b22',
            'bg_card': '#21262d',
            'bg_sidebar': '#010409',
            'text_primary': '#e6edf3',
            'text_secondary': '#8b949e',
            'text_muted': '#6e7681',
            'border': '#30363d',
            'border_light': '#21262d',
            'accent': '#58a6ff',
            'accent_secondary': '#a371f7',
            'accent_success': '#3fb950',
            'accent_warning': '#d29922',
            'accent_hover': '#79c0ff',
            'table_header': '#161b22',
            'table_row_alt': '#0d1117',
            'table_hover': '#1f2937',
            'chart_bg': '#0d1117',
            'shadow': 'rgba(0, 0, 0, 0.4)'
        }
    else:
        colors = {
            'bg_main': '#ffffff',
            'bg_secondary': '#f6f8fa',
            'bg_card': '#ffffff',
            'bg_sidebar': '#0d1117',
            'text_primary': '#1f2328',
            'text_secondary': '#656d76',
            'text_muted': '#8b949e',
            'border': '#d0d7de',
            'border_light': '#e1e4e8',
            'accent': '#0969da',
            'accent_secondary': '#8250df',
            'accent_success': '#1a7f37',
            'accent_warning': '#9a6700',
            'accent_hover': '#0550ae',
            'table_header': '#f6f8fa',
            'table_row_alt': '#f6f8fa',
            'table_hover': '#f3f4f6',
            'chart_bg': '#ffffff',
            'shadow': 'rgba(0, 0, 0, 0.08)'
        }

    st.markdown(f"""
        <style>
        /* ==================== CSS VARIABLES ==================== */
        :root {{
            --bg-main: {colors['bg_main']};
            --bg-card: {colors['bg_card']};
            --text-primary: {colors['text_primary']};
            --text-secondary: {colors['text_secondary']};
            --accent: {colors['accent']};
            --border: {colors['border']};
        }}

        /* ==================== GLOBAL STYLES ==================== */
        .stApp {{
            background-color: {colors['bg_main']} !important;
        }}

        /* NOTE: Streamlit main menu, header and toolbar are kept visible.
           Removed rules that hid Streamlit branding and toolbar so users
           can access the hamburger menu, deploy and settings. */

        /* ==================== SIDEBAR ==================== */
        section[data-testid="stSidebar"] {{
            background-color: {colors['bg_sidebar']} !important;
            border-right: 1px solid {colors['border']} !important;
        }}

        section[data-testid="stSidebar"] > div {{
            background-color: {colors['bg_sidebar']} !important;
            padding-top: 1.5rem !important;
        }}

        /* Sidebar text */
        section[data-testid="stSidebar"] * {{
            color: #e6edf3 !important;
        }}

        section[data-testid="stSidebar"] .stMarkdown p,
        section[data-testid="stSidebar"] .stMarkdown span {{
            color: rgba(230, 237, 243, 0.8) !important;
        }}

        /* Sidebar navigation radio */
        section[data-testid="stSidebar"] [data-testid="stRadio"] > div {{
            gap: 0.25rem !important;
        }}

        section[data-testid="stSidebar"] [data-testid="stRadio"] label {{
            background: transparent !important;
            padding: 0.6rem 0.75rem !important;
            margin: 0.15rem 0 !important;
            border-radius: 6px !important;
            transition: all 0.15s ease !important;
            cursor: pointer !important;
        }}

        section[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {{
            background: rgba(255, 255, 255, 0.08) !important;
        }}

        section[data-testid="stSidebar"] [data-testid="stRadio"] label[data-checked="true"] {{
            background: {colors['accent']} !important;
        }}

        /* Sidebar metrics */
        section[data-testid="stSidebar"] [data-testid="stMetric"] {{
            background: rgba(255, 255, 255, 0.03) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 8px !important;
            padding: 0.75rem !important;
        }}

        section[data-testid="stSidebar"] [data-testid="stMetricValue"] {{
            color: {colors['accent']} !important;
        }}

        /* Sidebar buttons */
        section[data-testid="stSidebar"] button {{
            background: rgba(255, 255, 255, 0.08) !important;
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
            color: white !important;
        }}

        section[data-testid="stSidebar"] button:hover {{
            background: rgba(255, 255, 255, 0.15) !important;
            border-color: rgba(255, 255, 255, 0.25) !important;
        }}

        /* ==================== MAIN CONTENT ==================== */
        .main .block-container {{
            padding: 2rem 3rem !important;
            max-width: 1400px !important;
        }}

        /* ==================== TYPOGRAPHY ==================== */
        .main h1 {{
            color: {colors['text_primary']} !important;
            font-size: 2rem !important;
            font-weight: 700 !important;
            margin-bottom: 1.5rem !important;
        }}

        .main h2 {{
            color: {colors['accent']} !important;
            font-size: 1.5rem !important;
            font-weight: 600 !important;
            margin-top: 2rem !important;
            margin-bottom: 1rem !important;
        }}

        .main h3 {{
            color: {colors['text_primary']} !important;
            font-size: 1.2rem !important;
            font-weight: 600 !important;
        }}

        .main p, .main span, .main label, .main div {{
            color: {colors['text_primary']} !important;
        }}

        /* ==================== METRICS ==================== */
        [data-testid="stMetric"] {{
            background: {colors['bg_card']} !important;
            border: 1px solid {colors['border']} !important;
            border-radius: 12px !important;
            padding: 1.25rem !important;
        }}

        [data-testid="stMetricLabel"] {{
            color: {colors['text_secondary']} !important;
            font-size: 0.85rem !important;
            font-weight: 500 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.03em !important;
        }}

        [data-testid="stMetricValue"] {{
            color: {colors['accent']} !important;
            font-size: 2rem !important;
            font-weight: 700 !important;
        }}

        /* ==================== BUTTONS ==================== */
        .stButton > button {{
            background: {colors['accent']} !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 0.5rem 1.25rem !important;
            font-weight: 600 !important;
            transition: all 0.15s ease !important;
        }}

        .stButton > button:hover {{
            background: {colors['accent_hover']} !important;
            transform: translateY(-1px) !important;
        }}

        .stButton > button:active {{
            transform: translateY(0) !important;
        }}

        /* ==================== CHARTS ==================== */
        .stPlotlyChart {{
            background: {colors['bg_card']} !important;
            border: 1px solid {colors['border']} !important;
            border-radius: 12px !important;
            padding: 1rem !important;
        }}

        /* ==================== DATA TABLES ==================== */
        [data-testid="stDataFrame"] {{
            background: {colors['bg_card']} !important;
            border: 1px solid {colors['border']} !important;
            border-radius: 12px !important;
            overflow: hidden !important;
        }}

        [data-testid="stDataFrame"] > div {{
            border-radius: 12px !important;
        }}

        /* ==================== SELECT BOXES ==================== */
        .stSelectbox > div > div {{
            background: {colors['bg_card']} !important;
            border: 1px solid {colors['border']} !important;
            border-radius: 8px !important;
            color: {colors['text_primary']} !important;
        }}

        .stSelectbox > div > div:hover {{
            border-color: {colors['accent']} !important;
        }}

        /* ==================== EXPANDERS ==================== */
        .streamlit-expanderHeader {{
            background: {colors['bg_card']} !important;
            border: 1px solid {colors['border']} !important;
            border-radius: 8px !important;
            color: {colors['text_primary']} !important;
        }}

        /* ==================== CUSTOM METRIC CARDS ==================== */
        .metric-card {{
            background: {colors['bg_card']};
            border: 1px solid {colors['border']};
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
        }}

        .metric-value {{
            font-size: 2.25rem;
            font-weight: 700;
            color: {colors['accent']};
            margin-bottom: 0.25rem;
        }}

        .metric-label {{
            font-size: 0.85rem;
            color: {colors['text_secondary']};
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        /* ==================== ALERTS ==================== */
        .stAlert {{
            border-radius: 8px !important;
        }}

        /* ==================== DIVIDERS ==================== */
        hr {{
            border-color: {colors['border']} !important;
            opacity: 0.5 !important;
        }}

        /* ==================== SCROLLBAR ==================== */
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}

        ::-webkit-scrollbar-track {{
            background: {colors['bg_secondary']};
        }}

        ::-webkit-scrollbar-thumb {{
            background: {colors['border']};
            border-radius: 4px;
        }}

        ::-webkit-scrollbar-thumb:hover {{
            background: {colors['text_muted']};
        }}

        /* ==================== BRANDING ==================== */
        .stApp::after {{
            content: "@rkjat65";
            position: fixed;
            bottom: 12px;
            right: 16px;
            font-size: 0.75rem;
            color: {colors['text_muted']};
            font-weight: 600;
            opacity: 0.4;
            letter-spacing: 0.1em;
            z-index: 1000;
        }}

        /* ==================== RESPONSIVE DESIGN ==================== */
        /* Tablet and smaller laptops */
        @media (max-width: 1200px) {{
            .main .block-container {{
                padding: 1.5rem 1.5rem !important;
                max-width: 100% !important;
            }}

            [data-testid="stMetricValue"] {{
                font-size: 1.5rem !important;
            }}

            .metric-value {{
                font-size: 1.75rem;
            }}
        }}

        /* Mobile and small tablets */
        @media (max-width: 768px) {{
            .main .block-container {{
                padding: 1rem 0.75rem !important;
            }}

            .main h1 {{
                font-size: 1.5rem !important;
            }}

            .main h2 {{
                font-size: 1.25rem !important;
            }}

            [data-testid="stMetric"] {{
                padding: 0.75rem !important;
            }}

            [data-testid="stMetricValue"] {{
                font-size: 1.25rem !important;
            }}

            [data-testid="stMetricLabel"] {{
                font-size: 0.7rem !important;
            }}

            .metric-card {{
                padding: 1rem;
            }}

            .metric-value {{
                font-size: 1.5rem;
            }}

            .metric-label {{
                font-size: 0.75rem;
            }}

            /* Stack columns on mobile */
            [data-testid="column"] {{
                width: 100% !important;
                flex: 1 1 100% !important;
            }}
        }}

        /* ==================== SIDEBAR COLLAPSE BUTTON ==================== */
        button[kind="header"] {{
            color: {colors['text_primary']} !important;
        }}

        [data-testid="collapsedControl"] {{
            color: {colors['text_primary']} !important;
            background: {colors['bg_card']} !important;
        }}

        /* ==================== IMPROVED TEXT CONTRAST ==================== */
        /* Ensure all text is readable */
        .stMarkdown, .stMarkdown p, .stMarkdown span {{
            color: {colors['text_primary']} !important;
        }}

        /* Chart title readability */
        .js-plotly-plot .plotly .gtitle {{
            fill: {colors['text_primary']} !important;
        }}

        /* Table text */
        .stDataFrame td, .stDataFrame th {{
            color: {colors['text_primary']} !important;
        }}

        /* Input fields */
        .stTextInput input, .stNumberInput input {{
            color: {colors['text_primary']} !important;
            background: {colors['bg_card']} !important;
            border: 1px solid {colors['border']} !important;
        }}

        /* Radio button text */
        .stRadio label span {{
            color: {colors['text_primary']} !important;
        }}

        /* Checkbox text */
        .stCheckbox label span {{
            color: {colors['text_primary']} !important;
        }}

        /* Tab text */
        .stTabs [data-baseweb="tab"] {{
            color: {colors['text_secondary']} !important;
        }}

        .stTabs [aria-selected="true"] {{
            color: {colors['accent']} !important;
        }}

        /* Plotly modebar visibility */
        .modebar {{
            background: transparent !important;
        }}

        .modebar-btn {{
            fill: {colors['text_secondary']} !important;
        }}

        .modebar-btn:hover {{
            fill: {colors['accent']} !important;
        }}
        
        /* Scroll to top on page navigation */
        html {{
            scroll-behavior: smooth;
        }}
        </style>
        
        <script>
        // Scroll to top when page changes
        if (window.parent !== window) {{
            window.parent.scrollTo(0, 0);
        }} else {{
            window.scrollTo(0, 0);
        }}
        </script>
    """, unsafe_allow_html=True)

# ==================== CHART FUNCTIONS ====================

def create_win_trend_chart(matches_df):
    """Win trend over seasons"""
    wins_by_season = matches_df.groupby(['season', 'match_winner_name']).size().reset_index(name='wins')
    top_teams = ['Mumbai Indians', 'Chennai Super Kings', 'Kolkata Knight Riders',
                 'Royal Challengers Bangalore', 'Delhi Capitals', 'Sunrisers Hyderabad']
    wins_filtered = wins_by_season[wins_by_season['match_winner_name'].isin(top_teams)]

    fig = px.line(wins_filtered, x='season', y='wins', color='match_winner_name',
                  title='🏆 Team Performance Trends Over Seasons', markers=True)

    fig = apply_chart_theme(fig, height=500, show_legend=True)
    fig.update_layout(
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig

def create_toss_impact_chart(matches_df):
    """Toss impact visualization"""
    toss_data = matches_df[matches_df['toss_decision'].notna()].copy()
    toss_data['won_after_toss'] = (toss_data['toss_winner_id'] == toss_data['match_winner_id'])
    impact = toss_data.groupby('toss_decision')['won_after_toss'].agg(['sum', 'count']).reset_index()
    impact['win_percentage'] = (impact['sum'] / impact['count'] * 100).round(1)

    theme = get_chart_theme_colors()
    fig = go.Figure(data=[go.Bar(x=impact['toss_decision'], y=impact['win_percentage'],
                                 text=impact['win_percentage'].astype(str) + '%',
                                 textposition='auto',
                                 textfont=dict(color=theme['text_color'], size=14),
                                 marker=dict(color=[theme['accent_primary'], theme['accent_secondary']],
                                           line=dict(color=theme['bg_color'], width=2)))])
    fig = apply_chart_theme(fig, title='Toss Impact: Bat First vs Field First', height=400, show_legend=False)
    return fig

def create_team_comparison_chart(team_stats_df):
    """Team comparison bar chart"""
    top_10 = team_stats_df.head(10)
    theme = get_chart_theme_colors()

    fig = go.Figure(data=[go.Bar(y=top_10['team'], x=top_10['win_percentage'], orientation='h',
                                 text=top_10['win_percentage'].astype(str) + '%',
                                 textposition='auto',
                                 textfont=dict(color=theme['text_color'], size=13),
                                 marker=dict(color=top_10['win_percentage'], colorscale='Viridis',
                                           showscale=True, colorbar=dict(
                                               title=dict(text="Win %", font=dict(color=theme['text_color'])),
                                               tickfont=dict(color=theme['text_color'])
                                           )))])
    fig = apply_chart_theme(fig, title='📊 Top 10 Teams by Win Percentage', height=500, show_legend=False)
    return fig

def create_venue_chart(matches_df):
    """Top venues chart"""
    venue_counts = matches_df['venue'].value_counts().head(10).reset_index()
    venue_counts.columns = ['venue', 'matches']
    fig = px.bar(venue_counts, x='matches', y='venue', orientation='h',
                 title='🏟️ Top 10 Venues by Matches Hosted',
                 color='matches', color_continuous_scale='Blues')
    fig = apply_chart_theme(fig, height=450, show_legend=False)
    return fig

def create_season_matches_chart(matches_df):
    """Matches per season chart"""
    theme = get_chart_theme_colors()
    season_counts = matches_df.groupby('season').size().reset_index(name='matches')
    fig = px.area(season_counts, x='season', y='matches',
                  title='Matches Played Per Season',
                  color_discrete_sequence=[theme['accent_primary']])
    fig = apply_chart_theme(fig, height=400, show_legend=False)
    return fig

def create_team_season_performance(team_name, matches_df):
    """Team performance over seasons"""
    team_matches = matches_df[
        (matches_df['team1_name'] == team_name) | (matches_df['team2_name'] == team_name)
    ].copy()
    team_matches['is_win'] = team_matches['match_winner_name'] == team_name
    season_perf = team_matches.groupby('season').agg({
        'match_id': 'count', 'is_win': 'sum'
    }).reset_index()
    season_perf.columns = ['season', 'matches', 'wins']
    season_perf['losses'] = season_perf['matches'] - season_perf['wins']

    theme = get_chart_theme_colors()
    fig = go.Figure()
    fig.add_trace(go.Bar(x=season_perf['season'], y=season_perf['wins'], name='Wins',
                        marker_color=theme['accent_success'], text=season_perf['wins'],
                        textposition='auto', textfont=dict(color=theme['text_color'])))
    fig.add_trace(go.Bar(x=season_perf['season'], y=season_perf['losses'], name='Losses',
                        marker_color=theme['accent_secondary'], text=season_perf['losses'],
                        textposition='auto', textfont=dict(color=theme['text_color'])))
    fig = apply_chart_theme(fig, title=f'{team_name} - Season Performance',
                           height=400, show_legend=True)
    fig.update_layout(barmode='stack',
                     legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    return fig

def create_win_loss_pie(team_name, matches_df):
    """Win/loss pie chart"""
    team_matches = matches_df[
        (matches_df['team1_name'] == team_name) | (matches_df['team2_name'] == team_name)
    ].copy()
    wins = (team_matches['match_winner_name'] == team_name).sum()
    losses = len(team_matches) - wins

    theme = get_chart_theme_colors()
    fig = go.Figure(data=[go.Pie(labels=['Wins', 'Losses'], values=[wins, losses], hole=0.4,
                                 marker=dict(colors=[theme['accent_success'], theme['accent_secondary']]),
                                 textinfo='label+percent',
                                 textfont=dict(size=14, color=theme['text_color']))])
    fig = apply_chart_theme(fig, title=f'{team_name} - Win/Loss Record', height=400, show_legend=False)
    return fig

def create_h2h_donut(team1, team2, matches_df):
    """H2H donut chart"""
    h2h_matches = matches_df[
        ((matches_df['team1_name'] == team1) & (matches_df['team2_name'] == team2)) |
        ((matches_df['team1_name'] == team2) & (matches_df['team2_name'] == team1))
    ]
    team1_wins = (h2h_matches['match_winner_name'] == team1).sum()
    team2_wins = (h2h_matches['match_winner_name'] == team2).sum()

    theme = get_chart_theme_colors()
    fig = go.Figure(data=[go.Pie(labels=[team1, team2], values=[team1_wins, team2_wins],
                                 hole=0.5, marker=dict(colors=[theme['accent_primary'], theme['accent_secondary']]),
                                 textinfo='label+value',
                                 textfont=dict(size=14, color=theme['text_color']))])
    fig = apply_chart_theme(fig, title='Head to Head Record', height=400, show_legend=False)
    fig.update_layout(
        annotations=[dict(text=f'{team1_wins + team2_wins}<br>Matches',
                         x=0.5, y=0.5, font_size=20, showarrow=False,
                         font=dict(color=theme['text_color']))]
    )
    return fig

# ==================== MAIN APP ====================

def main():
    """Main dashboard"""
    load_css()

    # Sidebar
    with st.sidebar:
        st.markdown("""
            <div style="text-align: center; padding: 1.5rem 0 1rem 0;">
                <h2 style="color: white; margin: 0; font-size: 1.5rem;">IPL Analytics</h2>
                <p style="color: rgba(255,255,255,0.8); font-size: 0.9rem; margin-top: 0.5rem;">Powered by AI</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        page = st.radio("Navigate to:",
            ["Home", "AI Dashboard", "Team Analysis", "Season Insights", "Player Records"],
            label_visibility="visible")
        
        # Track page changes and scroll to top
        if 'current_page' not in st.session_state:
            st.session_state.current_page = page
        
        if st.session_state.current_page != page:
            st.session_state.current_page = page
            # Scroll to top when page changes
            st.markdown("""
                <script>
                    window.parent.scrollTo(0, 0);
                </script>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.caption("Data: IPL 2008-2025")
        st.caption("Created by @rkjat65")

        st.markdown("---")
        st.markdown("#### Theme")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🌙 Dark", width='stretch',
                type="primary" if st.session_state.get('theme', 'dark') == 'dark' else "secondary"):
                st.session_state.theme = 'dark'
                st.rerun()
        with col2:
            if st.button("☀️ Light", width='stretch',
                type="primary" if st.session_state.get('theme', 'dark') == 'light' else "secondary"):
                st.session_state.theme = 'light'
                st.rerun()
    
    # Scroll to top at start of each page
    st.markdown("""
        <script>
            setTimeout(function() {
                window.parent.scrollTo(0, 0);
            }, 100);
        </script>
    """, unsafe_allow_html=True)
    
    # Route to pages
    if page == "Home":
        show_home_page()
    elif page == "AI Dashboard":
        show_ai_dashboard()
    elif page == "Team Analysis":
        show_team_analysis()
    elif page == "Season Insights":
        show_season_insights()
    elif page == "Player Records":
        show_player_records()

# ==================== PAGE FUNCTIONS ====================

def show_home_page():
    """Home page - COMPLETELY REDESIGNED with data quality checks"""
    theme = get_chart_theme_colors()
    st.markdown(f"""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h1 style="font-size: 2.5rem; margin-bottom: 0.5rem; color: {theme['title_color']};">IPL Cricket Analytics Dashboard</h1>
            <p style="font-size: 1.2rem; color: {theme['text_color']}; opacity: 0.8;">Comprehensive Data Analysis & AI-Powered Insights</p>
        </div>
    """, unsafe_allow_html=True)
    
    try:
        matches = load_matches()
        teams = load_teams()
        team_stats = get_team_stats()
        conn = get_database_connection()
        
        if matches.empty:
            st.warning("⚠️ No data loaded")
            return
        
        # ============ DATA QUALITY BANNER ============
        with st.expander("📊 Data Quality Report", expanded=False):
            quality_report = get_data_quality_report()
            if 'error' not in quality_report:
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    show_metric_with_tooltip(
                        "Data Quality Score", 
                        f"{quality_report['data_quality_score']:.1f}/100",
                        help_text="Overall data completeness score based on missing values and coverage"
                    )
                with col2:
                    show_metric_with_tooltip(
                        "Total Matches",
                        f"{quality_report['total_matches']:,}",
                        help_text="Total number of matches in the database"
                    )
                with col3:
                    show_metric_with_tooltip(
                        "Delivery Coverage",
                        f"{quality_report['delivery_coverage']:.1f}%",
                        help_text="Percentage of matches with ball-by-ball delivery data"
                    )
                with col4:
                    if quality_report['date_range'][0]:
                        date_range = f"{quality_report['date_range'][0]} to {quality_report['date_range'][1]}"
                        show_metric_with_tooltip(
                            "Date Range",
                            date_range[:20] + "..." if len(date_range) > 20 else date_range,
                            help_text="Earliest to latest match dates in the dataset"
                        )
                
                # Quality indicators
                quality_score = quality_report['data_quality_score']
                if quality_score >= 90:
                    st.success("✅ Excellent data quality")
                elif quality_score >= 75:
                    st.info("ℹ️ Good data quality")
                elif quality_score >= 60:
                    st.warning("⚠️ Moderate data quality - some missing data")
                else:
                    st.error("❌ Poor data quality - significant missing data")
                
                # Additional metrics
                if quality_report['null_venues'] > 0:
                    st.caption(f"⚠️ {quality_report['null_venues']} matches missing venue data")
                if quality_report['null_winners'] > 0:
                    st.caption(f"⚠️ {quality_report['null_winners']} matches missing winner data")
        
        # ============ SECTION 1: KEY METRICS ============
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            tooltip_text = "Total number of IPL matches in the database across all seasons"
            label_html = add_tooltip("Total Matches", tooltip_text)
            st.markdown(f"""<div class="metric-card">
                <div class="metric-label">{label_html}</div>
                <div class="metric-value">{len(matches):,}</div>
            </div>""", unsafe_allow_html=True)
        with col2:
            tooltip_text = "Number of unique IPL teams that have participated"
            label_html = add_tooltip("IPL Teams", tooltip_text)
            st.markdown(f"""<div class="metric-card">
                <div class="metric-label">{label_html}</div>
                <div class="metric-value">{len(teams)}</div>
            </div>""", unsafe_allow_html=True)
        with col3:
            tooltip_text = "Number of IPL seasons covered in the dataset"
            label_html = add_tooltip("Seasons", tooltip_text)
            st.markdown(f"""<div class="metric-card">
                <div class="metric-label">{label_html}</div>
                <div class="metric-value">{matches['season'].nunique()}</div>
            </div>""", unsafe_allow_html=True)
        with col4:
            tooltip_text = "Number of unique venues where matches have been played"
            label_html = add_tooltip("Venues", tooltip_text)
            st.markdown(f"""<div class="metric-card">
                <div class="metric-label">{label_html}</div>
                <div class="metric-value">{matches['venue'].nunique()}</div>
            </div>""", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # ============ SECTION 2: VISUAL INSIGHTS ============
        st.markdown("## 📈 Visual Insights")
        
        # # Row 1: Team Trends + Toss Impact
        # col1, col2 = st.columns(2)
        
        # with col1:
        #     # TOP 5 TEAMS PERFORMANCE TREND (Less cluttered)
        #     wins_by_season = matches.groupby(['season', 'match_winner_name']).size().reset_index(name='wins')
            
        #     # Get top 5 teams by total wins
        #     top_teams = matches['match_winner_name'].value_counts().head(5).index.tolist()
        #     wins_filtered = wins_by_season[wins_by_season['match_winner_name'].isin(top_teams)]
            
        #     fig = px.line(wins_filtered, x='season', y='wins', color='match_winner_name',
        #                   title='🏆 Top 5 Teams Performance Trends',
        #                   markers=True, line_shape='spline')
        #     fig.update_layout(
        #         height=400, 
        #         hovermode='x unified',
        #         legend=dict(
        #             title="Team",
        #             orientation="v",
        #             yanchor="top",
        #             y=0.99,
        #             xanchor="right",
        #             x=0.99,
        #             bgcolor="rgba(0,0,0,0.5)"
        #         ),
        #         plot_bgcolor='rgba(0,0,0,0)', 
        #         paper_bgcolor='rgba(0,0,0,0)',
        #         xaxis_title="Season",
        #         yaxis_title="Wins"
        #     )
        #     st.plotly_chart(fig, width='stretch')
        
        # with col2:
        #     # 3D PIE CHART FOR TOSS IMPACT (Coin-like)
        #     toss_data = matches[matches['toss_decision'].notna()].copy()
        #     toss_data['won_after_toss'] = (toss_data['toss_winner_id'] == toss_data['match_winner_id'])
            
        #     # Calculate stats
        #     bat_first = toss_data[toss_data['toss_decision'] == 'bat']
        #     field_first = toss_data[toss_data['toss_decision'] == 'field']
            
        #     bat_win_pct = (bat_first['won_after_toss'].sum() / len(bat_first) * 100) if len(bat_first) > 0 else 0
        #     field_win_pct = (field_first['won_after_toss'].sum() / len(field_first) * 100) if len(field_first) > 0 else 0
            
        #     # Create 3D pie chart
        #     labels = ['Bat First', 'Field First']
        #     values = [bat_win_pct, field_win_pct]
        #     colors = ['#667eea', '#764ba2']
            
        #     fig = go.Figure(data=[go.Pie(
        #         labels=labels,
        #         values=values,
        #         hole=0.3,
        #         marker=dict(
        #             colors=colors,
        #             line=dict(color='white', width=3)
        #         ),
        #         textinfo='label+percent',
        #         textfont_size=14,
        #         pull=[0.05, 0.05],  # Slightly pull out for 3D effect
        #         rotation=45
        #     )])
            
        #     fig.update_layout(
        #         title='🪙 Toss Impact: Win After Winning Toss',
        #         height=400,
        #         plot_bgcolor='rgba(0,0,0,0)',
        #         paper_bgcolor='rgba(0,0,0,0)',
        #         showlegend=True,
        #         legend=dict(
        #             orientation="h",
        #             yanchor="bottom",
        #             y=-0.15,
        #             xanchor="center",
        #             x=0.5
        #         ),
        #         annotations=[dict(
        #             text=f'{bat_win_pct:.1f}% vs {field_win_pct:.1f}%',
        #             x=0.5, y=0.5,
        #             font_size=16,
        #             showarrow=False,
        #             font=dict(color='#667eea')
        #         )]
        #     )
        #     st.plotly_chart(fig, width='stretch')
        
        # Row 2: Top 10 Teams + Win Methods
        col1, col2 = st.columns(2)
        
        with col1:
            # TOP 10 TEAMS - SORTED HIGH TO LOW
            top_10 = team_stats.sort_values('win_percentage', ascending=False).head(10)
            theme = get_chart_theme_colors()

            fig = go.Figure(data=[go.Bar(
                y=top_10['team'],
                x=top_10['win_percentage'],
                orientation='h',
                text=top_10['win_percentage'].round(1).astype(str) + '%',
                textposition='auto',
                textfont=dict(color=theme['text_color'], size=13),
                marker=dict(
                    color=top_10['win_percentage'],
                    colorscale='Viridis',
                    showscale=True,
                    colorbar=dict(
                        title=dict(text="Win %", font=dict(color=theme['text_color'])),
                        x=1.15,
                        tickfont=dict(color=theme['text_color'])
                    )
                ),
                hovertemplate='<b>%{y}</b><br>Win %: %{x:.1f}%<br>Matches: %{customdata[0]}<br>Wins: %{customdata[1]}<extra></extra>',
                customdata=top_10[['matches_played', 'wins']].values
            )])

            fig = apply_chart_theme(fig, title='📊 Top 10 Teams by Win Percentage',
                                   height=CHART_CONFIG['large_height'], show_legend=False)
            fig.update_layout(
                xaxis_title="Win Percentage (%)",
                yaxis_title="",
                yaxis=dict(autorange="reversed")  # High to low
            )
            st.plotly_chart(fig, width='stretch')
            add_chart_export_button(fig, "Top_10_Teams_Win_Percentage", "top_teams")
        
        with col2:
            # WIN METHODS DISTRIBUTION
            win_by_runs = matches[matches['win_by_runs'] > 0]['win_by_runs'].count()
            win_by_wickets = matches[matches['win_by_wickets'] > 0]['win_by_wickets'].count()
            theme = get_chart_theme_colors()

            fig = go.Figure(data=[go.Pie(
                labels=['Won by Runs', 'Won by Wickets'],
                values=[win_by_runs, win_by_wickets],
                hole=0.4,
                marker=dict(colors=[theme['accent_primary'], theme['accent_secondary']]),
                textinfo='label+percent+value',
                textfont=dict(size=13, color=theme['text_color'])
            )])

            fig = apply_chart_theme(fig, title='Match Winning Methods',
                                   height=450, show_legend=False)
            fig.update_layout(
                annotations=[dict(
                    text=f'{win_by_runs + win_by_wickets}<br>Matches',
                    x=0.5, y=0.5,
                    font_size=18,
                    showarrow=False,
                    font=dict(color=theme['text_color'])
                )]
            )
            st.plotly_chart(fig, width='stretch')
            add_chart_export_button(fig, "Match_Winning_Methods", "win_methods")
        
        # ============ SECTION 3: PLAYER SPOTLIGHT ============
        st.markdown("## 🌟 Player Spotlight")
        
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM deliveries")
            deliveries_count = cursor.fetchone()[0]
            
            if deliveries_count > 0:
                col1, col2 = st.columns(2)
                
                with col1:
                    # TOP 10 RUN SCORERS - cached
                    @st.cache_data(ttl=CHART_CONFIG['cache_ttl'], show_spinner=False)
                    def get_top_scorers_cached(conn):
                        return pd.read_sql_query("""
                            SELECT batter as player, 
                                   SUM(batter_runs) as total_runs,
                                   COUNT(DISTINCT match_id) as matches,
                                   ROUND(SUM(batter_runs) * 1.0 / COUNT(DISTINCT match_id), 1) as avg_per_match
                            FROM deliveries
                            WHERE batter IS NOT NULL
                            GROUP BY batter
                            ORDER BY total_runs DESC
                            LIMIT 10
                        """, conn)
                    top_scorers = get_top_scorers_cached(conn)
                    
                    theme = get_chart_theme_colors()
                    fig = go.Figure(data=[go.Bar(
                        y=top_scorers['player'],
                        x=top_scorers['total_runs'],
                        orientation='h',
                        text=top_scorers['total_runs'],
                        textposition='auto',
                        textfont=dict(color=theme['text_color'], size=12),
                        marker=dict(
                            color=top_scorers['total_runs'],
                            colorscale='Oranges',
                            showscale=False
                        ),
                        hovertemplate='<b>%{y}</b><br>Runs: %{x}<br>Matches: %{customdata[0]}<br>Avg: %{customdata[1]}/match<extra></extra>',
                        customdata=top_scorers[['matches', 'avg_per_match']].values
                    )])

                    fig = apply_chart_theme(fig, title='🏏 Top 10 Run Scorers (All-Time)',
                                           height=CHART_CONFIG['large_height'], show_legend=False)
                    fig.update_layout(
                        xaxis_title="Total Runs",
                        yaxis=dict(autorange="reversed")
                    )
                    st.plotly_chart(fig, width='stretch')
                    add_chart_export_button(fig, "Top_10_Run_Scorers", "top_scorers")
                
                with col2:
                    # TOP 10 WICKET TAKERS - cached
                    @st.cache_data(ttl=CHART_CONFIG['cache_ttl'], show_spinner=False)
                    def get_top_bowlers_cached(conn):
                        return pd.read_sql_query("""
                            SELECT bowler as player,
                                   SUM(CASE WHEN is_wicket = 1 AND wicket_kind NOT IN ('run out', 'retired hurt', 'obstructing the field') THEN 1 ELSE 0 END) as total_wickets,
                                   COUNT(DISTINCT match_id) as matches,
                                   ROUND(SUM(CASE WHEN is_wicket = 1 AND wicket_kind NOT IN ('run out', 'retired hurt', 'obstructing the field') THEN 1 ELSE 0 END) * 1.0 / COUNT(DISTINCT match_id), 2) as avg_per_match
                            FROM deliveries
                            WHERE bowler IS NOT NULL
                            GROUP BY bowler
                            ORDER BY total_wickets DESC
                            LIMIT 10
                        """, conn)
                    top_bowlers = get_top_bowlers_cached(conn)
                    
                    theme = get_chart_theme_colors()
                    fig = go.Figure(data=[go.Bar(
                        y=top_bowlers['player'],
                        x=top_bowlers['total_wickets'],
                        orientation='h',
                        text=top_bowlers['total_wickets'],
                        textposition='auto',
                        textfont=dict(color=theme['text_color'], size=12),
                        marker=dict(
                            color=top_bowlers['total_wickets'],
                            colorscale='Reds',
                            showscale=False
                        ),
                        hovertemplate='<b>%{y}</b><br>Wickets: %{x}<br>Matches: %{customdata[0]}<br>Avg: %{customdata[1]}/match<extra></extra>',
                        customdata=top_bowlers[['matches', 'avg_per_match']].values
                    )])

                    fig = apply_chart_theme(fig, title='🎯 Top 10 Wicket Takers (All-Time)',
                                           height=CHART_CONFIG['large_height'], show_legend=False)
                    fig.update_layout(
                        xaxis_title="Total Wickets",
                        yaxis=dict(autorange="reversed")
                    )
                    st.plotly_chart(fig, width='stretch')
                    add_chart_export_button(fig, "Top_10_Wicket_Takers", "top_bowlers")
            else:
                st.info("💡 Player statistics available after loading ball-by-ball data")
                
        except Exception as e:
            st.info("💡 Player statistics will appear once ball-by-ball data is loaded")
        
        # ============ SECTION 3.5: TEAM STATISTICS TABLE ============
        st.markdown("## 📋 Complete Team Statistics")
        formatted_team_stats = format_columns(team_stats.copy())
        st.dataframe(formatted_team_stats, width='stretch', hide_index=True, height=400)
        add_export_buttons(formatted_team_stats, key_prefix="team_stats_all")
        
        # Last Updated timestamp
        quality_report = get_data_quality_report()
        if 'last_updated' in quality_report:
            st.caption(f"📅 Last Updated: {quality_report['last_updated'].strftime('%Y-%m-%d %H:%M:%S')}")
        
        # ============ SECTION 4: SEASON ANALYSIS ============
        st.markdown("## 📊 Season Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # AVERAGE RUNS PER SEASON (Scoring trends)
            try:
                scoring_trends = pd.read_sql_query("""
                    SELECT m.season,
                           AVG(d.total_runs) as avg_runs_per_ball,
                           COUNT(DISTINCT m.match_id) as matches
                    FROM matches m
                    JOIN deliveries d ON m.match_id = d.match_id
                    GROUP BY m.season
                    ORDER BY m.season
                """, conn)
                
                if len(scoring_trends) > 0:
                    # Calculate runs per match
                    scoring_trends['runs_per_match'] = scoring_trends['avg_runs_per_ball'] * 240  # Approx 240 balls/match
                    theme = get_chart_theme_colors()

                    fig = px.line(scoring_trends,
                                  x='season',
                                  y='runs_per_match',
                                  title='Scoring Evolution Over Seasons',
                                  markers=True,
                                  line_shape='spline')

                    fig.update_traces(
                        line=dict(color=theme['accent_primary'], width=3),
                        marker=dict(size=8, color=theme['accent_secondary'])
                    )

                    fig = apply_chart_theme(fig, height=400, show_legend=False)
                    fig.update_layout(
                        xaxis_title="Season",
                        yaxis_title="Avg Runs per Match",
                        hovermode='x'
                    )
                    st.plotly_chart(fig, width='stretch')
                else:
                    raise Exception("No data")
            except:
                # Fallback: Matches per season (simple version)
                season_counts = matches.groupby('season').size().reset_index(name='matches')
                fig = px.bar(season_counts, x='season', y='matches',
                            title='📊 Matches Played Per Season',
                            color='matches',
                            color_continuous_scale='Blues')
                fig = apply_chart_theme(fig, height=400, show_legend=False)
                st.plotly_chart(fig, width='stretch')
        
        with col2:
            # TOP VENUES BY MATCHES
            venue_counts = matches['venue'].value_counts().head(10).reset_index()
            venue_counts.columns = ['venue', 'matches']
            
            fig = px.bar(venue_counts,
                         x='matches',
                         y='venue',
                         orientation='h',
                         title='🏟️ Top 10 Venues by Matches Hosted',
                         color='matches',
                         color_continuous_scale='Blues')

            fig = apply_chart_theme(fig, height=CHART_CONFIG['default_height'], show_legend=False)
            fig.update_layout(yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig, width='stretch')
            add_chart_export_button(fig, "Top_10_Venues", "venues")
        
            
    except Exception as e:
        error_msg = f"❌ Error loading dashboard: {str(e)}"
        st.error(error_msg)
        logger.error(f"Home page error: {e}\n{traceback.format_exc()}")
        st.info("💡 Try refreshing the page. If the issue persists, check that the database is properly configured.")

def show_team_analysis():
    """Team analysis page with formatted tables"""
    st.title("🏏 Team Analysis")
    
    try:
        teams = load_teams()
        matches = load_matches()
        
        if teams.empty or matches.empty:
            st.warning("⚠️ No data")
            return
        
        active = teams[teams['is_active'] == 1]['team_name'].tolist()
        selected = st.selectbox("Select Team", active)
        
        if selected:
            st.markdown(f"## {selected}")
            conn = get_database_connection()
            
            stats = pd.read_sql_query(f"""
                WITH team_matches AS (
                    SELECT * FROM matches 
                    WHERE team1_name = '{selected}' OR team2_name = '{selected}'
                )
                SELECT 
                    COUNT(*) as total_matches,
                    SUM(CASE WHEN match_winner_name = '{selected}' THEN 1 ELSE 0 END) as wins,
                    ROUND(100.0 * SUM(CASE WHEN match_winner_name = '{selected}' THEN 1 ELSE 0 END) / COUNT(*), 1) as win_pct
                FROM team_matches
            """, conn)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                show_metric_with_tooltip(
                    "Matches",
                    int(stats['total_matches'].iloc[0]),
                    help_text="Total number of matches played by this team"
                )
            with col2:
                show_metric_with_tooltip(
                    "Wins",
                    int(stats['wins'].iloc[0]),
                    help_text="Total number of matches won by this team"
                )
            with col3:
                show_metric_with_tooltip(
                    "Win %",
                    f"{stats['win_pct'].iloc[0]}%",
                    help_text="Percentage of matches won (Wins / Total Matches × 100)"
                )
            with col4:
                # Calculate NRR
                nrr = calculate_net_run_rate(selected)
                show_metric_with_tooltip(
                    "Net Run Rate",
                    f"{nrr:+.3f}",
                    help_text="Net Run Rate: Average run difference per match. Positive NRR indicates better scoring rate."
                )
            
            # Advanced Metrics Section
            st.markdown("### 📊 Advanced Performance Metrics")
            chase_defend = get_chase_vs_defend_stats(selected)
            powerplay_stats = get_powerplay_stats(selected)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                show_metric_with_tooltip(
                    "Chase Win Rate",
                    f"{chase_defend['chase_win_rate']:.1f}%",
                    delta=f"{chase_defend['chase_wins']}/{chase_defend['chase_matches']} matches",
                    help_text="Win percentage when chasing a target (batting second)"
                )
            with col2:
                show_metric_with_tooltip(
                    "Defend Win Rate",
                    f"{chase_defend['defend_win_rate']:.1f}%",
                    delta=f"{chase_defend['defend_wins']}/{chase_defend['defend_matches']} matches",
                    help_text="Win percentage when defending a total (batting first)"
                )
            with col3:
                avg_pp_runs = powerplay_stats.get('avg_powerplay_runs', 0)
                show_metric_with_tooltip(
                    "Avg Powerplay Runs",
                    f"{avg_pp_runs:.1f}",
                    help_text="Average runs scored per over in powerplay (overs 1-6)"
                )
            with col4:
                avg_death_runs = powerplay_stats.get('avg_death_runs', 0)
                show_metric_with_tooltip(
                    "Avg Death Overs Runs",
                    f"{avg_death_runs:.1f}",
                    help_text="Average runs scored per over in death overs (overs 16-20)"
                )
            
            col1, col2 = st.columns(2)
            with col1:
                perf_fig = create_team_season_performance(selected, matches)
                st.plotly_chart(perf_fig)
                add_chart_export_button(perf_fig, f"{selected}_Season_Performance", f"{selected}_perf")
            with col2:
                pie_fig = create_win_loss_pie(selected, matches)
                st.plotly_chart(pie_fig)
                add_chart_export_button(pie_fig, f"{selected}_Win_Loss", f"{selected}_pie")
            
            # New: Wins by Venue for Selected Team
            st.markdown("### 🏟️ Success by Venue")
            venue_stats = matches[matches['match_winner_name'] == selected]['venue'].value_counts().head(10).reset_index()
            venue_stats.columns = ['venue', 'wins']
            
            # Add export button
            if not venue_stats.empty:
                add_export_buttons(venue_stats, key_prefix=f"venue_stats_{selected}")
            
            fig = px.bar(venue_stats, x='wins', y='venue', orientation='h',
                        title=f'Success for {selected} at Different Venues',
                        color='wins', color_continuous_scale='Blues')
            fig = apply_chart_theme(fig, height=CHART_CONFIG['default_height'], show_legend=False)
            fig.update_layout(yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig, width='stretch')
            add_chart_export_button(fig, f"{selected}_Venue_Success", f"{selected}_venue")
            
            # ============ HEAD TO HEAD COMPARISON ============
            st.markdown("---")
            st.markdown("## ⚔️ Head to Head Comparison")
            
            # Get other teams for comparison
            other_teams = [t for t in active if t != selected]
            if other_teams:
                compare_team = st.selectbox("Compare with", other_teams, key=f"compare_{selected}")
                
                if compare_team:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # H2H Statistics
                        h2h = safe_query_execution(f"""
                            SELECT COUNT(*) as total,
                                SUM(CASE WHEN match_winner_name = '{selected}' THEN 1 ELSE 0 END) as team1_wins,
                                SUM(CASE WHEN match_winner_name = '{compare_team}' THEN 1 ELSE 0 END) as team2_wins
                            FROM matches
                            WHERE (team1_name = '{selected}' AND team2_name = '{compare_team}')
                               OR (team1_name = '{compare_team}' AND team2_name = '{selected}')
                        """, conn, "Unable to fetch H2H data")
                        
                        if not h2h.empty:
                            total = int(h2h['total'].iloc[0])
                            team1_wins = int(h2h['team1_wins'].iloc[0])
                            team2_wins = int(h2h['team2_wins'].iloc[0])
                            
                            col1_metric, col2_metric, col3_metric = st.columns(3)
                            with col1_metric:
                                st.metric(f"{selected}", team1_wins, 
                                         delta=f"{round(100*team1_wins/total, 1)}%" if total > 0 else "0%")
                            with col2_metric:
                                st.metric("Total Matches", total)
                            with col3_metric:
                                st.metric(f"{compare_team}", team2_wins,
                                         delta=f"{round(100*team2_wins/total, 1)}%" if total > 0 else "0%")
                            
                            # H2H Donut Chart
                            h2h_fig = create_h2h_donut(selected, compare_team, matches)
                            st.plotly_chart(h2h_fig, width='stretch')
                            add_chart_export_button(h2h_fig, f"{selected}_vs_{compare_team}_H2H", f"h2h_{selected}_{compare_team}")
                    
                    with col2:
                        # Recent Encounters
                        st.markdown("### 📅 Recent Encounters")
                        recent_matches = matches[
                            ((matches['team1_name'] == selected) & (matches['team2_name'] == compare_team)) |
                            ((matches['team1_name'] == compare_team) & (matches['team2_name'] == selected))
                        ].head(10).sort_values('match_date', ascending=False)
                        
                        if not recent_matches.empty:
                            recent_display = recent_matches[['match_date', 'season', 'venue', 'match_winner_name']].copy()
                            recent_display['Result'] = recent_display.apply(
                                lambda row: f"{selected} won" if row['match_winner_name'] == selected 
                                           else f"{compare_team} won" if row['match_winner_name'] == compare_team 
                                           else "No result",
                                axis=1
                            )
                            # Format columns first, then select
                            recent_display = format_columns(recent_display)
                            # Select only the columns we want to display
                            display_cols = ['Match Date', 'Season', 'Venue', 'Result']
                            available_cols = [col for col in display_cols if col in recent_display.columns]
                            if available_cols:
                                recent_display = recent_display[available_cols]
                            st.dataframe(recent_display, width='stretch', hide_index=True, height=300)
                            
                            # Win trend over seasons
                            h2h_by_season = recent_matches.groupby('season').agg({
                                'match_id': 'count',
                                'match_winner_name': lambda x: (x == selected).sum()
                            }).reset_index()
                            h2h_by_season.columns = ['Season', 'Matches', 'Wins']
                            h2h_by_season['Win %'] = (h2h_by_season['Wins'] / h2h_by_season['Matches'] * 100).round(1)
                            
                            trend_fig = px.line(h2h_by_season, x='Season', y='Win %', 
                                              title=f'{selected} Win % vs {compare_team} Over Seasons',
                                              markers=True)
                            trend_fig = apply_chart_theme(trend_fig, height=CHART_CONFIG['small_height'], show_legend=False)
                            st.plotly_chart(trend_fig, width='stretch')
                            add_chart_export_button(trend_fig, f"{selected}_vs_{compare_team}_Trend", f"h2h_trend_{selected}")
                        else:
                            st.info("No recent matches found")
            
            # Add correlation matrix for team performance metrics
            st.markdown("---")
            st.markdown("### 📈 Performance Metrics Correlation")
            try:
                # Get team performance data across seasons
                team_season_data = []
                for season in matches['season'].unique():
                    season_matches = matches[matches['season'] == season]
                    team_season_matches = season_matches[
                        (season_matches['team1_name'] == selected) | 
                        (season_matches['team2_name'] == selected)
                    ]
                    if len(team_season_matches) > 0:
                        wins = (team_season_matches['match_winner_name'] == selected).sum()
                        team_season_data.append({
                            'Season': season,
                            'Matches': len(team_season_matches),
                            'Wins': wins,
                            'Win %': (wins / len(team_season_matches)) * 100
                        })
                
                if len(team_season_data) > 3:
                    corr_df = pd.DataFrame(team_season_data)
                    corr_fig = create_correlation_matrix(
                        corr_df[['Matches', 'Wins', 'Win %']],
                        title=f'{selected} - Performance Metrics Correlation',
                        height=CHART_CONFIG['small_height']
                    )
                    if corr_fig:
                        st.plotly_chart(corr_fig, width='stretch')
                        add_chart_export_button(corr_fig, f"{selected}_Correlation", f"{selected}_corr")
            except Exception as e:
                logger.warning(f"Error creating correlation matrix: {e}")
                
    except Exception as e:
        st.error(f"❌ Error: {e}")

# def show_match_explorer():
#     """Match explorer with formatted tables and pagination"""
#     st.title("🔍 Match Explorer")
    
#     try:
#         matches = load_matches()
#         if matches.empty:
#             st.warning("⚠️ No data")
#             return
        
#         col1, col2, col3 = st.columns(3)
        
#         with col1:
#             seasons = ['All'] + sorted(matches['season'].unique().tolist(), reverse=True)
#             season = st.selectbox("Season", seasons)
#         with col2:
#             teams = ['All'] + sorted(matches['team1_name'].dropna().unique().tolist())
#             team = st.selectbox("Team", teams)
#         with col3:
#             venues = ['All'] + sorted(matches['venue'].dropna().unique().tolist())
#             venue = st.selectbox("Venue", venues)
        
#         filtered = matches.copy()
#         if season != 'All':
#             filtered = filtered[filtered['season'] == season]
#         if team != 'All':
#             filtered = filtered[(filtered['team1_name'] == team) | (filtered['team2_name'] == team)]
#         if venue != 'All':
#             filtered = filtered[filtered['venue'] == venue]
        
#         st.markdown(f"### Found {len(filtered)} matches")
        
#         # ENHANCED: Show all matches with pagination
#         display = filtered[['match_date', 'season', 'team1_name', 'team2_name', 'match_winner_name', 'venue']]
#         display = format_columns(display)  # Format column names
        
#         # Add pagination
#         col1, col2 = st.columns([3, 1])
#         with col2:
#             rows_per_page = st.selectbox("Rows per page", [25, 50, 100, "All"], index=1)
        
#         if rows_per_page == "All":
#             st.dataframe(display, width='stretch', hide_index=True, height=600)
#         else:
#             total_pages = (len(display) - 1) // rows_per_page + 1
#             page = st.number_input("Page", min_value=1, max_value=total_pages, value=1)
#             start_idx = (page - 1) * rows_per_page
#             end_idx = start_idx + rows_per_page
            
#             st.dataframe(display.iloc[start_idx:end_idx], width='stretch', hide_index=True)
#             st.caption(f"Showing {start_idx + 1} to {min(end_idx, len(display))} of {len(display)} matches | Page {page} of {total_pages}")
        
#     except Exception as e:
#         st.error(f"❌ Error: {e}")

@st.cache_data(ttl=CHART_CONFIG['cache_ttl'], show_spinner=False)
@st.cache_data(ttl=CHART_CONFIG['cache_ttl'], show_spinner=False)
def get_season_stats(season: int, matches: pd.DataFrame):
    """Get cached season statistics - optimized"""
    return matches[matches['season'] == season].copy()

def show_season_insights():
    """Enhanced Season Insights with comprehensive analysis"""
    st.title("📊 Season Insights")
    
    try:
        matches = load_matches()
        if matches.empty:
            st.warning("⚠️ No data")
            return
        
        seasons = sorted(matches['season'].unique().tolist(), reverse=True)
        selected = st.selectbox("Select Season", seasons)
        
        if selected:
            season_matches = get_season_stats(selected, matches)
            st.markdown(f"## 🏏 IPL {selected} - Complete Analysis")
            
            # Key Metrics with tooltips
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                show_metric_with_tooltip("Matches", len(season_matches), 
                                       help_text="Total matches played in this season")
            with col2:
                show_metric_with_tooltip("Teams", season_matches['team1_name'].nunique(),
                                       help_text="Number of teams that participated")
            with col3:
                show_metric_with_tooltip("Venues", season_matches['venue'].nunique(),
                                       help_text="Number of venues used")
            with col4:
                winner = season_matches['match_winner_name'].value_counts().index[0] if len(season_matches) > 0 else "N/A"
                show_metric_with_tooltip("Champion", winner,
                                       help_text="Team with most wins in the season")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Row 1: Top Teams and Venues
            col1, col2 = st.columns(2)
            
            with col1:
                team_wins = season_matches['match_winner_name'].value_counts().head(8).sort_values(ascending=False)
                fig = px.bar(x=team_wins.values, y=team_wins.index, orientation='h',
                            title=f'🏆 Top Teams - IPL {selected}',
                            color=team_wins.values, color_continuous_scale='Blues')
                fig.update_layout(yaxis={'categoryorder': 'total ascending'}, xaxis_title='Wins')
                fig = apply_chart_theme(fig, height=CHART_CONFIG['default_height'], show_legend=False)
                st.plotly_chart(fig, width='stretch')
                add_chart_export_button(fig, f"Top_Teams_{selected}", f"teams_{selected}")

            with col2:
                venue_dist = season_matches['venue'].value_counts().head(8).sort_values(ascending=False)
                fig = px.bar(x=venue_dist.values, y=venue_dist.index, orientation='h',
                            title=f'🏟️ Top Venues - IPL {selected}',
                            color=venue_dist.values, color_continuous_scale='Greens')
                fig.update_layout(yaxis={'categoryorder': 'total ascending'}, xaxis_title='Matches')
                fig = apply_chart_theme(fig, height=CHART_CONFIG['default_height'], show_legend=False)
                st.plotly_chart(fig, width='stretch')
                add_chart_export_button(fig, f"Top_Venues_{selected}", f"venues_{selected}")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Row 2: Match Distribution and Win Methods
            col1, col2 = st.columns(2)
            
            with col1:
                # Matches by month/date distribution
                if 'match_date' in season_matches.columns:
                    season_matches['month'] = pd.to_datetime(season_matches['match_date'], errors='coerce').dt.month
                    monthly_matches = season_matches['month'].value_counts().sort_index()
                    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                    monthly_matches.index = [month_names[int(m)-1] if pd.notna(m) else 'Unknown' for m in monthly_matches.index]
                    
                    fig = px.line(x=monthly_matches.index, y=monthly_matches.values,
                                title=f'📅 Match Distribution by Month - IPL {selected}',
                                markers=True)
                    fig = apply_chart_theme(fig, height=CHART_CONFIG['default_height'], show_legend=False)
                    fig.update_layout(xaxis_title='Month', yaxis_title='Matches')
                    st.plotly_chart(fig, width='stretch')
                    add_chart_export_button(fig, f"Match_Distribution_{selected}", f"dist_{selected}")
            
            with col2:
                # Win methods
                win_by_runs = (season_matches['win_by_runs'] > 0).sum()
                win_by_wickets = (season_matches['win_by_wickets'] > 0).sum()
                theme = get_chart_theme_colors()
                
                fig = go.Figure(data=[go.Pie(
                    labels=['Won by Runs', 'Won by Wickets'],
                    values=[win_by_runs, win_by_wickets],
                    hole=0.4,
                    marker=dict(colors=[theme['accent_primary'], theme['accent_secondary']]),
                    textinfo='label+percent+value',
                    textfont=dict(size=13, color=theme['text_color'])
                )])
                fig = apply_chart_theme(fig, title=f'🎯 Win Methods - IPL {selected}',
                                       height=CHART_CONFIG['default_height'], show_legend=False)
                st.plotly_chart(fig, width='stretch')
                add_chart_export_button(fig, f"Win_Methods_{selected}", f"methods_{selected}")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Row 3: Team Performance Table
            st.markdown("### 📋 Complete Team Standings")
            team_standings = []
            for team in season_matches['team1_name'].unique():
                if pd.notna(team):
                    team_season_matches = season_matches[
                        (season_matches['team1_name'] == team) | (season_matches['team2_name'] == team)
                    ]
                    wins = (team_season_matches['match_winner_name'] == team).sum()
                    total = len(team_season_matches)
                    team_standings.append({
                        'Team': team,
                        'Matches': total,
                        'Wins': wins,
                        'Losses': total - wins,
                        'Win %': round(100 * wins / total, 1) if total > 0 else 0
                    })
            
            if team_standings:
                standings_df = pd.DataFrame(team_standings).sort_values('Win %', ascending=False)
                standings_df = format_columns(standings_df)
                st.dataframe(standings_df, width='stretch', hide_index=True, height=400)
                add_export_buttons(standings_df, key_prefix=f"standings_{selected}")
                
    except Exception as e:
        error_msg = f"❌ Error loading season insights: {str(e)}"
        st.error(error_msg)
        logger.error(f"Season insights error: {e}\n{traceback.format_exc()}")
        st.info("💡 Try selecting a different season or refreshing the page.")

def show_head_to_head():
    """Head to head with formatted tables"""
    st.title("⚔️ Head to Head")
    
    try:
        teams = load_teams()
        matches = load_matches()
        
        if teams.empty or matches.empty:
            st.warning("⚠️ No data")
            return
        
        active = teams[teams['is_active'] == 1]['team_name'].tolist()
        
        col1, col2 = st.columns(2)
        with col1:
            team1 = st.selectbox("Team 1", active, key='t1')
        with col2:
            team2 = st.selectbox("Team 2", [t for t in active if t != team1], key='t2')
        
        if team1 and team2:
            st.markdown(f"## {team1} vs {team2}")
            conn = get_database_connection()
            
            h2h = pd.read_sql_query(f"""
                SELECT COUNT(*) as total,
                    SUM(CASE WHEN match_winner_name = '{team1}' THEN 1 ELSE 0 END) as team1_wins,
                    SUM(CASE WHEN match_winner_name = '{team2}' THEN 1 ELSE 0 END) as team2_wins
                FROM matches
                WHERE (team1_name = '{team1}' AND team2_name = '{team2}')
                   OR (team1_name = '{team2}' AND team2_name = '{team1}')
            """, conn)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(f"{team1} Wins", int(h2h['team1_wins'].iloc[0]))
            with col2:
                st.metric("Total", int(h2h['total'].iloc[0]))
            with col3:
                st.metric(f"{team2} Wins", int(h2h['team2_wins'].iloc[0]))
            
            st.plotly_chart(create_h2h_donut(team1, team2, matches))
            
    except Exception as e:
        st.error(f"❌ Error: {e}")

def show_player_records():
    """Player Records page - COMPREHENSIVE STATISTICS"""
    st.title("🌟 Player Records & Statistics")
    st.markdown("### IPL's Greatest Performers")
    
    try:
        conn = get_database_connection()
        matches = load_matches()
        
        # Check if deliveries data exists
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM deliveries")
        deliveries_count = cursor.fetchone()[0]
        
        if deliveries_count == 0:
            st.warning("⚠️ Player statistics require ball-by-ball data")
            st.info("💡 Load deliveries data to see player records")
            return
        
        # ============ FILTERS ============
        st.markdown("## 🔍 Filters")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            seasons = ['All Time'] + sorted(matches['season'].unique().tolist(), reverse=True)
            selected_season = st.selectbox("Season", seasons)
        
        with col2:
            stat_type = st.selectbox("View", ["Batting", "Bowling", "All-Round"])
        
        with col3:
            min_matches = st.number_input("Min Matches", min_value=1, value=10, step=5)
        
        # Build season filter
        season_filter = f"AND m.season = {selected_season}" if selected_season != 'All Time' else ""
        
        # ============ BATTING RECORDS ============
        if stat_type in ["Batting", "All-Round"]:
            st.markdown("---")
            st.markdown("## 🏏 Batting Records")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Top Run Scorers
                query = f"""
                    SELECT d.batter as player,
                           COUNT(DISTINCT d.match_id) as matches,
                           SUM(d.batter_runs) as total_runs,
                           MAX(innings_runs.runs) as highest_score,
                           ROUND(AVG(innings_runs.runs), 1) as average,
                           ROUND(SUM(d.batter_runs) * 100.0 / NULLIF(SUM(CASE WHEN d.is_wide_ball = 0 THEN 1 ELSE 0 END), 0), 1) as strike_rate,
                           SUM(CASE WHEN d.batter_runs = 6 THEN 1 ELSE 0 END) as sixes,
                           SUM(CASE WHEN d.batter_runs = 4 THEN 1 ELSE 0 END) as fours
                    FROM deliveries d
                    JOIN matches m ON d.match_id = m.match_id
                    LEFT JOIN (
                        SELECT match_id, innings, batter, SUM(batter_runs) as runs
                        FROM deliveries
                        GROUP BY match_id, innings, batter
                    ) innings_runs ON d.match_id = innings_runs.match_id 
                                   AND d.innings = innings_runs.innings 
                                   AND d.batter = innings_runs.batter
                    WHERE d.batter IS NOT NULL {season_filter}
                    GROUP BY d.batter
                    HAVING COUNT(DISTINCT d.match_id) >= {min_matches if selected_season == 'All Time' else 1}
                    ORDER BY total_runs DESC
                    LIMIT 15
                """
                top_scorers = pd.read_sql_query(query, conn)
                top_scorers = format_columns(top_scorers)
                
                st.markdown("### 👑 Top Run Scorers")
                # Show as chart only (table removed)
                fig = px.bar(top_scorers.head(10),
                            y=top_scorers.head(10)['Player'], x=top_scorers.head(10)['Total Runs'],
                            orientation='h',
                            title='Top 10 Run Scorers',
                            color=top_scorers.head(10)['Total Runs'],
                            color_continuous_scale='Oranges')
                fig.update_layout(yaxis={'title': ''}, xaxis_title='Total Runs', yaxis_autorange='reversed')
                fig = apply_chart_theme(fig, height=CHART_CONFIG['default_height'], show_legend=False)
                st.plotly_chart(fig, width='stretch')
                add_chart_export_button(fig, "Top_10_Run_Scorers_Player_Records", "player_top_scorers")
            
            with col2:
                # Best Strike Rates
                run_threshold = 200 if selected_season == 'All Time' else 50
                match_threshold = min_matches if selected_season == 'All Time' else 1
                
                query = f"""
                    SELECT d.batter as player,
                           COUNT(DISTINCT d.match_id) as matches,
                           SUM(d.batter_runs) as total_runs,
                           SUM(CASE WHEN d.is_wide_ball = 0 THEN 1 ELSE 0 END) as balls_faced,
                           ROUND(SUM(d.batter_runs) * 100.0 / NULLIF(SUM(CASE WHEN d.is_wide_ball = 0 THEN 1 ELSE 0 END), 0), 1) as strike_rate,
                           SUM(CASE WHEN d.batter_runs = 6 THEN 1 ELSE 0 END) as sixes
                    FROM deliveries d
                    JOIN matches m ON d.match_id = m.match_id
                    WHERE d.batter IS NOT NULL {season_filter}
                    GROUP BY d.batter
                    HAVING COUNT(DISTINCT d.match_id) >= {match_threshold} AND SUM(d.batter_runs) >= {run_threshold}
                    ORDER BY strike_rate DESC
                    LIMIT 15
                """
                best_sr = pd.read_sql_query(query, conn)
                best_sr = format_columns(best_sr)
                
                st.markdown("### ⚡ Best Strike Rates")
                # Show as chart only (table removed)
                fig = px.bar(best_sr.head(10),
                            y=best_sr.head(10)['Player'], x=best_sr.head(10)['Strike Rate'],
                            orientation='h',
                            title='Top 10 Strike Rates',
                            color=best_sr.head(10)['Strike Rate'],
                            color_continuous_scale='Reds')
                fig.update_layout(yaxis={'title': ''}, xaxis_title='Strike Rate', yaxis_autorange='reversed')
                fig = apply_chart_theme(fig, height=400, show_legend=False)
                st.plotly_chart(fig, width='stretch')
        
        # ============ BOWLING RECORDS ============
        if stat_type in ["Bowling", "All-Round"]:
            st.markdown("---")
            st.markdown("## 🎯 Bowling Records")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Top Wicket Takers
                query = f"""
                    SELECT d.bowler as player,
                           COUNT(DISTINCT d.match_id) as matches,
                           SUM(CASE WHEN d.is_wicket = 1 AND d.wicket_kind NOT IN ('run out', 'retired hurt', 'obstructing the field') THEN 1 ELSE 0 END) as total_wickets,
                           SUM(CASE WHEN d.is_wide_ball = 0 AND d.is_no_ball = 0 THEN 1 ELSE 0 END) as balls_bowled,
                           SUM(d.batter_runs + d.wide_ball_runs + d.no_ball_runs) as runs_conceded,
                           ROUND(SUM(d.batter_runs + d.wide_ball_runs + d.no_ball_runs) * 6.0 / NULLIF(SUM(CASE WHEN d.is_wide_ball = 0 AND d.is_no_ball = 0 THEN 1 ELSE 0 END), 0), 2) as economy,
                           ROUND(SUM(d.batter_runs + d.wide_ball_runs + d.no_ball_runs) * 1.0 / NULLIF(SUM(CASE WHEN d.is_wicket = 1 AND d.wicket_kind NOT IN ('run out', 'retired hurt', 'obstructing the field') THEN 1 ELSE 0 END), 0), 1) as average,
                           ROUND(SUM(CASE WHEN d.is_wide_ball = 0 AND d.is_no_ball = 0 THEN 1 ELSE 0 END) * 1.0 / NULLIF(SUM(CASE WHEN d.is_wicket = 1 AND d.wicket_kind NOT IN ('run out', 'retired hurt', 'obstructing the field') THEN 1 ELSE 0 END), 0), 1) as strike_rate
                    FROM deliveries d
                    JOIN matches m ON d.match_id = m.match_id
                    WHERE d.bowler IS NOT NULL {season_filter}
                    GROUP BY d.bowler
                    HAVING COUNT(DISTINCT d.match_id) >= {min_matches if selected_season == 'All Time' else 1}
                    ORDER BY total_wickets DESC
                    LIMIT 15
                """
                top_bowlers = pd.read_sql_query(query, conn)
                top_bowlers = format_columns(top_bowlers)
                
                st.markdown("### 🎯 Top Wicket Takers")
                st.dataframe(top_bowlers, width='stretch', hide_index=True, height=400)
                
                # Visualization
                fig = px.bar(top_bowlers.head(10),
                            y='Player', x='Total Wickets',
                            orientation='h',
                            title='Top 10 Wicket Takers',
                            color='Total Wickets',
                            color_continuous_scale='Reds')
                fig = apply_chart_theme(fig, height=CHART_CONFIG['default_height'], show_legend=False)
                fig.update_layout(yaxis=dict(autorange="reversed"))
                st.plotly_chart(fig, width='stretch')
                add_chart_export_button(fig, "Top_10_Wicket_Takers_Player_Records", "player_top_bowlers")
            
            with col2:
                # Best Economy Rates
                run_threshold_bowling = 100 if selected_season == 'All Time' else 24
                match_threshold_bowling = min_matches if selected_season == 'All Time' else 1

                query = f"""
                    SELECT d.bowler as player,
                           COUNT(DISTINCT d.match_id) as matches,
                           SUM(CASE WHEN d.is_wicket = 1 AND d.wicket_kind NOT IN ('run out', 'retired hurt', 'obstructing the field') THEN 1 ELSE 0 END) as wickets,
                           SUM(CASE WHEN d.is_wide_ball = 0 AND d.is_no_ball = 0 THEN 1 ELSE 0 END) as balls_bowled,
                           SUM(d.batter_runs + d.wide_ball_runs + d.no_ball_runs) as runs_conceded,
                           ROUND(SUM(d.batter_runs + d.wide_ball_runs + d.no_ball_runs) * 6.0 / NULLIF(SUM(CASE WHEN d.is_wide_ball = 0 AND d.is_no_ball = 0 THEN 1 ELSE 0 END), 0), 2) as economy
                    FROM deliveries d
                    JOIN matches m ON d.match_id = m.match_id
                    WHERE d.bowler IS NOT NULL {season_filter}
                    GROUP BY d.bowler
                    HAVING COUNT(DISTINCT d.match_id) >= {match_threshold_bowling} AND SUM(CASE WHEN d.is_wide_ball = 0 AND d.is_no_ball = 0 THEN 1 ELSE 0 END) >= {run_threshold_bowling}
                    ORDER BY economy ASC
                    LIMIT 15
                """
                best_economy = pd.read_sql_query(query, conn)
                best_economy = format_columns(best_economy)
                
                st.markdown("### 💰 Best Economy Rates")
                st.dataframe(best_economy, width='stretch', hide_index=True, height=400)
                
                # Visualization
                fig = px.bar(best_economy.head(10),
                            y='Player', x='Economy',
                            orientation='h',
                            title='Top 10 Economy Rates',
                            color='Wickets',
                            color_continuous_scale='Greens')
                fig = apply_chart_theme(fig, height=CHART_CONFIG['default_height'], show_legend=False)
                fig.update_layout(yaxis=dict(autorange="reversed"))
                st.plotly_chart(fig, width='stretch')
                add_chart_export_button(fig, "Best_Economy_Rates", "best_economy")
        
        # ============ PLAYER COMPARISON ============
        st.markdown("---")
        st.markdown("## 🔄 Player Comparison")
        
        # Get all players
        all_players = pd.read_sql_query(f"""
            SELECT DISTINCT batter as player FROM deliveries
            WHERE batter IS NOT NULL
            UNION
            SELECT DISTINCT bowler as player FROM deliveries
            WHERE bowler IS NOT NULL
            ORDER BY player
        """, conn)['player'].tolist()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            player1 = st.selectbox("Player 1", all_players, key='p1')
        with col2:
            player2 = st.selectbox("Player 2", [p for p in all_players if p != player1], key='p2')
        with col3:
            player3 = st.selectbox("Player 3 (Optional)", ['None'] + [p for p in all_players if p not in [player1, player2]], key='p3')
        
        if st.button("🔄 Compare Players", type="primary"):
            players = [player1, player2] if player3 == 'None' else [player1, player2, player3]
            
            # Get comparison data
            comparison_data = []
            for player in players:
                batting = pd.read_sql_query(f"""
                    SELECT 
                        '{player}' as player,
                        COUNT(DISTINCT match_id) as matches,
                        SUM(batter_runs) as runs,
                        ROUND(SUM(batter_runs) * 100.0 / COUNT(*), 1) as strike_rate,
                        SUM(CASE WHEN batter_runs = 6 THEN 1 ELSE 0 END) as sixes
                    FROM deliveries
                    WHERE batter = '{player}'
                """, conn)
                
                bowling = pd.read_sql_query(f"""
                    SELECT 
                        SUM(CASE WHEN is_wicket = 1 AND wicket_kind NOT IN ('run out', 'retired hurt', 'obstructing the field') THEN 1 ELSE 0 END) as wickets,
                        ROUND(SUM(batter_runs + wide_ball_runs + no_ball_runs) * 6.0 / NULLIF(SUM(CASE WHEN is_wide_ball = 0 AND is_no_ball = 0 THEN 1 ELSE 0 END), 0), 2) as economy
                    FROM deliveries
                    WHERE bowler = '{player}'
                """, conn)
                
                comparison_data.append({
                    'Player': player,
                    'Matches': int(batting['matches'].iloc[0]),
                    'Runs': int(batting['runs'].iloc[0]),
                    'Strike Rate': float(batting['strike_rate'].iloc[0]),
                    'Sixes': int(batting['sixes'].iloc[0]),
                    'Wickets': int(bowling['wickets'].iloc[0]) if bowling['wickets'].iloc[0] else 0,
                    'Economy': float(bowling['economy'].iloc[0]) if bowling['economy'].iloc[0] else 0
                })
            
            comp_df = pd.DataFrame(comparison_data)
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.dataframe(comp_df, width='stretch', hide_index=True)
            
            with col2:
                # Radar chart
                categories = ['Runs', 'Strike Rate', 'Sixes', 'Wickets']
                theme = get_chart_theme_colors()

                fig = go.Figure()

                radar_colors = [theme['accent_primary'], theme['accent_secondary'], theme['accent_success']]
                for idx, player in enumerate(players):
                    player_data = comp_df[comp_df['Player'] == player].iloc[0]
                    values = [
                        player_data['Runs'] / comp_df['Runs'].max() * 100,
                        player_data['Strike Rate'] / comp_df['Strike Rate'].max() * 100,
                        player_data['Sixes'] / comp_df['Sixes'].max() * 100 if comp_df['Sixes'].max() > 0 else 0,
                        player_data['Wickets'] / comp_df['Wickets'].max() * 100 if comp_df['Wickets'].max() > 0 else 0
                    ]

                    fig.add_trace(go.Scatterpolar(
                        r=values,
                        theta=categories,
                        fill='toself',
                        name=player,
                        line_color=radar_colors[idx % len(radar_colors)]
                    ))

                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(visible=True, range=[0, 100], color=theme['text_color']),
                        angularaxis=dict(color=theme['text_color']),
                        bgcolor=theme['bg_color']
                    ),
                    title=dict(text="Player Comparison", font=dict(color=theme['title_color'])),
                    height=400,
                    plot_bgcolor=theme['bg_color'],
                    paper_bgcolor=theme['paper_color'],
                    font=dict(color=theme['text_color']),
                    legend=dict(font=dict(color=theme['text_color']))
                )
                st.plotly_chart(fig, width='stretch')
                add_chart_export_button(fig, "Player_Comparison_Radar", "player_comparison")
        
        # ============ HALL OF FAME ============
        st.markdown("---")
        st.markdown("## 🏆 Hall of Fame - All-Time Records")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 🎯 Highest Score")
            query = """
                SELECT batter as player, SUM(batter_runs) as runs
                FROM deliveries
                GROUP BY match_id, innings, batter
                ORDER BY runs DESC
                LIMIT 5
            """
            highest = pd.read_sql_query(query, conn)
            highest = format_columns(highest)
            # Show as bar chart
            fig = px.bar(highest, x='Runs', y='Player', orientation='h', title='Top Innings - Highest Scores', color='Runs', color_continuous_scale='Oranges')
            fig = apply_chart_theme(fig, height=CHART_CONFIG['small_height'], show_legend=False)
            fig.update_layout(yaxis=dict(autorange='reversed'))
            st.plotly_chart(fig, width='stretch')
            add_chart_export_button(fig, "Hall_of_Fame_Highest_Scores", "hall_highest")
        
        with col2:
            st.markdown("### 🎯 Best Bowling")
            query = """
                SELECT bowler as player, 
                       SUM(CASE WHEN is_wicket = 1 AND wicket_kind NOT IN ('run out', 'retired hurt', 'obstructing the field') THEN 1 ELSE 0 END) as wickets,
                       SUM(batter_runs + wide_ball_runs + no_ball_runs) as runs
                FROM deliveries
                GROUP BY match_id, innings, bowler
                ORDER BY wickets DESC, runs ASC
                LIMIT 5
            """
            best_bowling = pd.read_sql_query(query, conn)
            best_bowling = format_columns(best_bowling)
            # Show as bar chart (wickets)
            fig = px.bar(best_bowling, x='Wickets', y='Player', orientation='h', title='Best Bowling Performances', color='Wickets', color_continuous_scale='Reds')
            fig = apply_chart_theme(fig, height=CHART_CONFIG['small_height'], show_legend=False)
            fig.update_layout(yaxis=dict(autorange='reversed'))
            st.plotly_chart(fig, width='stretch')
            add_chart_export_button(fig, "Hall_of_Fame_Best_Bowling", "hall_bowling")
        
        with col3:
            st.markdown("### 🎯 Most Sixes")
            query = """
                SELECT batter as player, COUNT(*) as total_sixes
                FROM deliveries
                WHERE batter_runs = 6
                GROUP BY batter
                ORDER BY total_sixes DESC
                LIMIT 5
            """
            most_sixes = pd.read_sql_query(query, conn)
            most_sixes = format_columns(most_sixes)
            # Show as bar chart
            fig = px.bar(most_sixes, x='Total Sixes', y='Player', orientation='h', title='Most Sixes (Innings)', color='Total Sixes', color_continuous_scale='Purples')
            fig = apply_chart_theme(fig, height=CHART_CONFIG['small_height'], show_legend=False)
            fig.update_layout(yaxis=dict(autorange='reversed'))
            st.plotly_chart(fig, width='stretch')
            add_chart_export_button(fig, "Hall_of_Fame_Most_Sixes", "hall_sixes")
        
    except Exception as e:
        st.error(f"❌ Error loading player records: {e}")
        import traceback
        st.code(traceback.format_exc())

# ==================== AI DASHBOARD (REDESIGNED) ====================

def show_ai_dashboard():
    """Enhanced AI Dashboard with independent but linked buttons and proper state management"""
    theme = get_chart_theme_colors()
    
    st.markdown(f"""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h1 style="margin-bottom: 0.5rem; color: {theme['title_color']};"> AI-Powered Analytics Dashboard</h1>
            <p style="font-size: 1.2rem; color: {theme['text_color']}; opacity: 0.8;">Ask questions in natural language and get intelligent insights</p>
        </div>
    """, unsafe_allow_html=True)
    
    if not GEMINI_AVAILABLE or not GEMINI_API_KEY:
        st.warning("⚠️ Gemini API not configured. Please set GEMINI_API_KEY in your .env file.")
        return
    
    # --- INTERNAL HELPER: Data Fetching Logic ---
    def fetch_and_process_data(user_question):
        """Fetches data and updates session state. Returns (Success_Bool, Data_Frame or Error_Msg)"""
        try:
            # Generate SQL (Assuming generate_sql_from_question uses the appropriate model internally)
            # If you need to enforce gemini-3-pro-preview for SQL, update that function separately
            sql = generate_sql_from_question(user_question)
            
            if not sql:
                return False, "Could not translate question to SQL."

            # Get data
            conn = get_database_connection()
            # Assuming safe_query_execution returns a dataframe
            df = safe_query_execution(sql, conn, "Unable to fetch data")
            
            if df is None or df.empty:
                return False, "No data found for this query."
                
            # Update Session State
            st.session_state.last_query_data = df
            st.session_state.last_query_question = user_question
            return True, df
            
        except Exception as e:
            return False, str(e)

    # --- UI LAYOUT ---

    # Example questions
    st.markdown("### 💡 Try These Questions")
    example_cols = st.columns(3)
    examples = [
        "Who are the top 5 run scorers in IPL history?",
        "Compare Mumbai Indians vs Chennai Super Kings",
        "Which team has the best win percentage?",
        "Show me the top 10 wicket takers",
        "How many matches were played in 2019?",
        "Head to head record RCB vs CSK"
    ]
    
    if 'ai_query' not in st.session_state:
        st.session_state.ai_query = ''
    
    for idx, ex in enumerate(examples):
        with example_cols[idx % 3]:
            if st.button(ex, key=f"ai_example_{idx}", use_container_width=True):
                st.session_state.ai_query = ex
                st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Question Input
    st.markdown("### ❓ Ask Your Question")
    question = st.text_area(
        "Enter your question about IPL data:",
        value=st.session_state.get('ai_query', ''),
        placeholder="Example: Top 5 batsman in the 2019 IPL run wise",
        height=120,
        key="ai_question_input"
    )
    
    # Sync input to state
    if question:
        st.session_state.ai_query = question
    
    # Action Buttons
    col1, col2 = st.columns([1, 1])
    with col1:
        get_answer_btn = st.button("🔍 Get Answer", type="primary", use_container_width=True)
    with col2:
        generate_image_btn = st.button("🎨 Generate Visualization", type="secondary", use_container_width=True)

    # --- LOGIC HANDLERS ---

    # HANDLER 1: Get Answer (Text + Data)
    if get_answer_btn and question:
        with st.status("🤔 Analyzing your question...", expanded=True) as status:
            
            # Step 1: Fetch Data
            status.write("🔍 Converting question to SQL and fetching data...")
            success, result = fetch_and_process_data(question)
            
            if success:
                data = result
                status.write("✅ Data fetched successfully!")
                
                # Show Data Table
                st.markdown("### 📊 Data Results")
                formatted_data = format_columns(data.head(20))
                st.dataframe(formatted_data, width='stretch', hide_index=True, height=300)
                
                # Step 2: Generate AI Text Insight
                status.write("🤖 Generating AI insight...")
                try:
                    # Specific model for text analysis
                    model_text = genai.GenerativeModel('gemini-3-pro-preview') 
                    
                    data_summary = data.head(10).to_string(index=False)
                    prompt = f"""You are an IPL analyst. Answer concisely based on this data:
                    Question: {question}
                    Data: {data_summary}
                    Keep it conversational, mention specific numbers."""
                    
                    response = model_text.generate_content(prompt)
                    answer = response.text.strip()
                    
                    st.markdown("### 💡 AI Insight")
                    st.markdown(f"""
                        <div style="background: linear-gradient(135deg, {theme['accent_primary']} 0%, {theme['accent_secondary']} 100%); 
                                   padding: 1.5rem; border-radius: 12px; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                            <div style="font-size: 1.1rem; line-height: 1.8;">{answer}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    status.update(label="Analysis Complete!", state="complete", expanded=True)
                    
                except Exception as e:
                    status.update(label="Analysis Failed", state="error")
                    st.error(f"AI Text Error: {str(e)}")
            else:
                status.update(label="Data Fetch Failed", state="error")
                st.error(f"❌ {result}")

    # HANDLER 2: Generate Image (Visual Only)
    if generate_image_btn and question:
        with st.status("🎨 Preparing Visualization...", expanded=True) as status:
            
            # Step 1: Check if we have VALID data for THIS question
            # If data is missing OR the question in box is different from the last cached question -> Fetch new
            current_data = st.session_state.get('last_query_data')
            last_q = st.session_state.get('last_query_question')
            
            data_ready = False
            
            if current_data is None or last_q != question:
                status.write("🔄 Fetching fresh data for visualization...")
                success, result = fetch_and_process_data(question)
                if success:
                    current_data = result
                    data_ready = True
                    status.write("✅ Data fetched!")
                else:
                    status.update(label="Data Fetch Failed", state="error")
                    st.error(f"❌ {result}")
            else:
                status.write("⚡ Using cached data...")
                data_ready = True

            # Step 2: Generate Image
            if data_ready:
                status.write("🖌️ AI is drawing the chart (Gemini 3 Pro Image)...")
                try:
                    data_ctx = prepare_data_context(current_data, max_rows=15)
                    
                    ai_prompt = f"""Generate a professional IPL cricket infographic.
                    Question: {question}
                    Data Summary: {data_ctx}
                    Style: High resolution 1920x1080, dark modern theme, neon accents. 
                    Include clear data labels, team logos or cricket elements. 
                    Make it look like a broadcast graphic."""
                    
                    # Specific model for Image Generation
                    model_image = genai.GenerativeModel('gemini-3-pro-image-preview')
                    
                    response = model_image.generate_content(
                        ai_prompt,
                        generation_config=genai.GenerationConfig(temperature=0.4),
                        request_options={'timeout': 60}
                    )
                    
                    if response and hasattr(response, 'parts'):
                        # Extract Image
                        for part in response.parts:
                            if hasattr(part, 'inline_data') and part.inline_data:
                                ai_img = part.inline_data.data
                                # Assuming add_watermark_to_image exists
                                watermarked = add_watermark_to_image(ai_img, "@rkjat65")
                                
                                st.image(watermarked, width="stretch", caption=f"Visual: {question}")
                                st.download_button(
                                    "Download Image", 
                                    watermarked, 
                                    "ipl_viz.png", 
                                    "image/png"
                                )
                                status.update(label="Visualization Generated!", state="complete", expanded=True)
                                break
                        else:
                             status.update(label="Generation Failed", state="error")
                             st.error("Model returned no image data.")
                    else:
                        status.update(label="Generation Failed", state="error")
                        st.error("No response from Image API.")
                        
                except Exception as e:
                    status.update(label="Generation Error", state="error")
                    st.error(f"Image Gen Error: {str(e)}")

    # SECTION 2: Portfolio Images (Keeping your existing code for static images)
    st.markdown("---")
    st.markdown("## 🖼️ AI Viz Showcase")
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.markdown("### 🏆 Championship Analysis")
        # Use st.image with file path check or fallback
        try: st.image("generated_images/champ.png", width="stretch")
        except: st.info("Placeholder: Championship Stats")
        
        st.markdown("### ⚔️ MI vs CSK")
        try: st.image("generated_images/micsk.png", width="stretch")
        except: st.info("Placeholder: MI vs CSK")

    with col_p2:
        st.markdown("### 🏏 Top Batsmen")
        try: st.image("generated_images/top5batsmen.png", width="stretch")
        except: st.info("Placeholder: Top Batsmen")
        
        st.markdown("### 🎯 Top Bowlers")
        try: st.image("generated_images/top5b.png", width="stretch")
        except: st.info("Placeholder: Top Bowlers")
                    
def show_generated_gallery():
    """Show history of generated images"""
    st.markdown("## 🖼️ Generated Images Gallery")
    st.markdown("*Your AI-generated visualizations*")
    
    # Check for generated images
    if GENERATED_IMAGES_DIR.exists():
        images = list(GENERATED_IMAGES_DIR.glob("*.png"))
        
        if images:
            st.info(f"📊 Found {len(images)} generated images")
            
            # Sort by modification time (newest first)
            images = sorted(images, key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Display in grid
            cols = st.columns(3)
            for idx, img_path in enumerate(images):
                with cols[idx % 3]:
                    st.image(str(img_path), caption=img_path.name)
                    
                    # Download button with unique key
                    st.download_button(
                        "📥 Download",
                        open(img_path, 'rb').read(),
                        img_path.name,
                        "image/png",
                        key=f"gallery_dl_{idx}_{img_path.stem}",  # Unique key
                        width='stretch'
                    )
        else:
            st.info("💡 No images generated yet. Create some from the Smart Query or Quick Insights tabs!")
    else:
        st.info("💡 Start generating images to build your gallery!")
        # Create directory if it doesn't exist
        GENERATED_IMAGES_DIR.mkdir(exist_ok=True)

    



if __name__ == "__main__":
    main()
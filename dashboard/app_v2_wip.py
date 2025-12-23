# """
# IPL Cricket Analytics Dashboard - ENHANCED VERSION
# Better table styling and proper column names throughout
# """

# import streamlit as st
# import sqlite3
# import pandas as pd
# import plotly.express as px
# import plotly.graph_objects as go
# from pathlib import Path
# import os
# from dotenv import load_dotenv
# from PIL import Image, ImageDraw, ImageFont
# import io
# from datetime import datetime
# from contextlib import contextmanager  # FIXED: For database connection management

# def format_columns(df):
#     """Format column names to proper case - ENHANCED VERSION"""
#     rename_map = {
#         'match_date': 'Match Date',
#         'season': 'Season',
#         'team1_name': 'Team 1',
#         'team2_name': 'Team 2',
#         'match_winner_name': 'Winner',
#         'venue': 'Venue',
#         'city': 'City',
#         'toss_winner_name': 'Toss Winner',
#         'toss_decision': 'Toss Decision',
#         'win_by_runs': 'Win By Runs',
#         'win_by_wickets': 'Win By Wickets',
#         'player_of_match': 'Player of Match',
#         'match_id': 'Match ID',
#         'team': 'Team',
#         'total_matches': 'Matches',
#         'matches_played': 'Matches',
#         'wins': 'Wins',
#         'losses': 'Losses',
#         'win_percentage': 'Win %',
#         'total': 'Total',
#         'teams': 'Teams',
#         'venues': 'Venues',
#         'matches': 'Matches'
#     }
#     return df.rename(columns=rename_map)

# # Load environment
# load_dotenv()

# # Try to import Gemini
# try:
#     import google.generativeai as genai
#     GEMINI_AVAILABLE = True
# except ImportError:
#     GEMINI_AVAILABLE = False

# GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# # Initialize session state
# if 'messages' not in st.session_state:
#     st.session_state.messages = []

# # Page configuration
# st.set_page_config(
#     page_title="IPL Analytics Dashboard",
#     page_icon="🏏",
#     layout="wide",
#     initial_sidebar_state="collapsed"
# )

# # Create directory for generated images
# GENERATED_IMAGES_DIR = Path("generated_images")
# GENERATED_IMAGES_DIR.mkdir(exist_ok=True)

# # ==================== DATABASE FUNCTIONS ====================

# @contextmanager  # FIXED: Prevents memory leaks
# def get_database_connection():
#     """Get database connection with automatic cleanup"""
#     db_path = Path("data/cricket_analytics.db")
#     if not db_path.exists():
#         st.error("❌ Database not found! Run `python scripts/create_database.py` first.")
#         st.stop()
    
#     conn = sqlite3.connect(db_path, check_same_thread=False)
#     try:
#         yield conn
#     finally:
#         conn.close()  # FIXED: Always closes connection

# @st.cache_data(ttl=3600)
# def load_teams():
#     """Load teams data"""
#     with get_database_connection() as conn:  # FIXED: Uses context manager
#         return pd.read_sql_query("SELECT * FROM teams ORDER BY team_name", conn)

# @st.cache_data(ttl=3600)
# def load_matches():
#     """Load all matches"""
#     with get_database_connection() as conn:  # FIXED: Uses context manager
#         return pd.read_sql_query("SELECT * FROM matches ORDER BY match_date DESC", conn)

# @st.cache_data(ttl=3600)
# def get_team_stats():
#     """Get overall team statistics"""
#     with get_database_connection() as conn:  # FIXED
#         return pd.read_sql_query("""
#             WITH team_matches AS (
#                 SELECT team1_name as team FROM matches
#                 UNION ALL SELECT team2_name as team FROM matches
#             ),
#             team_wins AS (
#                 SELECT match_winner_name as team FROM matches WHERE match_winner_name IS NOT NULL
#             )
#             SELECT 
#                 tm.team,
#                 COUNT(*) as matches_played,
#                 COALESCE(tw.wins, 0) as wins,
#                 COUNT(*) - COALESCE(tw.wins, 0) as losses,
#                 ROUND(100.0 * COALESCE(tw.wins, 0) / COUNT(*), 1) as win_percentage
#             FROM team_matches tm
#             LEFT JOIN (SELECT team, COUNT(*) as wins FROM team_wins GROUP BY team) tw 
#             ON tm.team = tw.team
#             WHERE tm.team IS NOT NULL
#             GROUP BY tm.team
#             ORDER BY win_percentage DESC
#         """, conn)

# # ==================== IMAGE HELPER FUNCTIONS ====================

# def plotly_to_image_bytes(fig, width=1200, height=675):
#     """Convert Plotly figure to image bytes"""
#     try:
#         import plotly.io as pio
#         # Try to set kaleido as engine (needed for image export)
#         try:
#             pio.kaleido.scope.mathjax = None
#         except:
#             pass
#         return pio.to_image(fig, format='png', width=width, height=height, engine='kaleido')
#     except ImportError as e:
#         st.error("❌ Install kaleido: `pip install kaleido`")
#         st.info("Kaleido is required to export Plotly charts as images")
#         return None
#     except Exception as e:
#         st.warning(f"Could not convert chart to image: {e}")
#         st.info("💡 The chart is still visible above. To enable downloads, install: `pip install kaleido`")
#         return None

# def add_watermark_to_image(image_bytes, text="@rkjat65"):
#     """Add watermark to image"""
#     try:
#         img = Image.open(io.BytesIO(image_bytes))
#         if img.mode != 'RGBA':
#             img = img.convert('RGBA')
        
#         overlay = Image.new('RGBA', img.size, (255, 255, 255, 0))
#         draw = ImageDraw.Draw(overlay)
        
#         try:
#             font = ImageFont.truetype("arial.ttf", 36)
#         except:
#             try:
#                 font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
#             except:
#                 font = ImageFont.load_default()
        
#         bbox = draw.textbbox((0, 0), text, font=font)
#         text_width = bbox[2] - bbox[0]
#         text_height = bbox[3] - bbox[1]
        
#         margin = 20
#         x = img.width - text_width - margin
#         y = img.height - text_height - margin
        
#         draw.text((x + 2, y + 2), text, fill=(0, 0, 0, 128), font=font)
#         draw.text((x, y), text, fill=(255, 255, 255, 200), font=font)
        
#         watermarked = Image.alpha_composite(img, overlay).convert('RGB')
        
#         output = io.BytesIO()
#         watermarked.save(output, format='PNG', quality=95)
#         output.seek(0)
#         return output.getvalue()
#     except Exception as e:
#         st.warning(f"Watermark warning: {e}")
#         return image_bytes

# def save_image_to_folder(image_bytes, prefix="ai_generated"):
#     """Save image locally"""
#     try:
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#         filename = f"{prefix}_{timestamp}.png"
#         filepath = GENERATED_IMAGES_DIR / filename
#         with open(filepath, 'wb') as f:
#             f.write(image_bytes)
#         return str(filepath)
#     except Exception as e:
#         st.warning(f"Could not save: {e}")
#         return None

# def prepare_data_context(dataframe, max_rows=20):
#     """Prepare data for AI prompt"""
#     if dataframe is None or len(dataframe) == 0:
#         return ""
#     df_subset = dataframe.head(max_rows)
#     return f"""
# Dataset Information:
# - Total Rows: {len(dataframe)}
# - Columns: {', '.join(dataframe.columns.tolist())}

# Data (first {min(len(dataframe), max_rows)} rows):
# {df_subset.to_string(index=False)}
# """

# def get_chart_info(fig):
#     """Extract chart information"""
#     try:
#         chart_type = fig.data[0].type if len(fig.data) > 0 else "unknown"
#         layout = fig.layout
#         return f"""
# Chart Type: {chart_type}
# Title: {layout.title.text if layout.title else "No title"}
# """
#     except:
#         return "Chart info not available"

# # ==================== PLOTLY CHART GENERATOR ====================

# def detect_best_chart_type(dataframe):
#     """Detect best chart type from data"""
#     if len(dataframe.columns) < 2:
#         return "table"
#     numeric_cols = dataframe.select_dtypes(include=['number']).columns.tolist()
#     text_cols = dataframe.select_dtypes(include=['object']).columns.tolist()
#     if len(numeric_cols) >= 1 and len(text_cols) >= 1:
#         return "bar"
#     elif len(numeric_cols) >= 2:
#         return "scatter"
#     return "table"

# def generate_plotly_chart(dataframe, chart_type=None, title="IPL Data Visualization"):
#     """Generate Plotly chart from data"""
#     if dataframe is None or len(dataframe) == 0:
#         return None
    
#     if chart_type is None:
#         chart_type = detect_best_chart_type(dataframe)
    
#     numeric_cols = dataframe.select_dtypes(include=['number']).columns.tolist()
#     text_cols = dataframe.select_dtypes(include=['object']).columns.tolist()
    
#     try:
#         if chart_type == "bar":
#             fig = px.bar(dataframe,
#                 y=text_cols[0] if text_cols else dataframe.columns[0],
#                 x=numeric_cols[0] if numeric_cols else dataframe.columns[1],
#                 title=title, orientation='h',
#                 color=numeric_cols[0] if numeric_cols else None,
#                 color_continuous_scale='Viridis')
#         elif chart_type == "pie":
#             fig = px.pie(dataframe,
#                 names=text_cols[0] if text_cols else dataframe.columns[0],
#                 values=numeric_cols[0] if numeric_cols else dataframe.columns[1],
#                 title=title)
#         elif chart_type == "line":
#             fig = px.line(dataframe,
#                 x=dataframe.columns[0],
#                 y=numeric_cols[0] if numeric_cols else dataframe.columns[1],
#                 title=title, markers=True)
#         else:
#             fig = px.bar(dataframe,
#                 x=dataframe.columns[0],
#                 y=numeric_cols[0] if numeric_cols else dataframe.columns[1],
#                 title=title)
        
#         fig.update_layout(
#             height=500, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
#             font=dict(size=12), title_font=dict(size=18, color='#667eea'),
#             margin=dict(l=80, r=80, t=80, b=80), showlegend=False)
#         return fig
#     except Exception as e:
#         st.error(f"Error generating chart: {e}")
#         return None

# def get_chart_type_options(dataframe):
#     """Get available chart types for data"""
#     options = []
#     numeric_cols = dataframe.select_dtypes(include=['number']).columns.tolist()
#     text_cols = dataframe.select_dtypes(include=['object']).columns.tolist()
    
#     if len(text_cols) >= 1 and len(numeric_cols) >= 1:
#         options.extend([("bar", "📊 Bar Chart"), ("pie", "🥧 Pie Chart")])
#     if len(numeric_cols) >= 1:
#         options.append(("line", "📈 Line Chart"))
#     if len(numeric_cols) >= 2:
#         options.append(("scatter", "🔵 Scatter Plot"))
#     if not options:
#         options.append(("bar", "📊 Bar Chart"))
#     return options

# # ==================== GEMINI AI FUNCTIONS ====================

# def initialize_gemini():
#     """Initialize Gemini API"""
#     if not GEMINI_API_KEY:
#         return False
#     try:
#         genai.configure(api_key=GEMINI_API_KEY)
#         return True
#     except:
#         return False

# def generate_sql_from_question(question):
#     """Generate SQL from natural language with smart preprocessing"""
#     try:
#         # Check for common patterns and provide better SQL directly
#         question_lower = question.lower()
        
#         # Pattern: "Compare Team A vs Team B"
#         if 'compare' in question_lower and ' vs ' in question_lower:
#             # Extract team names
#             parts = question_lower.split(' vs ')
#             if len(parts) == 2:
#                 team1 = parts[0].replace('compare', '').strip()
#                 team2 = parts[1].strip()
                
#                 # Map common abbreviations to full names
#                 team_map = {
#                     'mi': 'Mumbai Indians',
#                     'mumbai': 'Mumbai Indians',
#                     'mumbai indians': 'Mumbai Indians',
#                     'csk': 'Chennai Super Kings',
#                     'chennai': 'Chennai Super Kings',
#                     'chennai super kings': 'Chennai Super Kings',
#                     'rcb': 'Royal Challengers Bangalore',
#                     'bangalore': 'Royal Challengers Bangalore',
#                     'kkr': 'Kolkata Knight Riders',
#                     'kolkata': 'Kolkata Knight Riders',
#                     'dc': 'Delhi Capitals',
#                     'delhi': 'Delhi Capitals',
#                     'pbks': 'Punjab Kings',
#                     'punjab': 'Punjab Kings',
#                     'rr': 'Rajasthan Royals',
#                     'rajasthan': 'Rajasthan Royals',
#                     'srh': 'Sunrisers Hyderabad',
#                     'hyderabad': 'Sunrisers Hyderabad',
#                     'gt': 'Gujarat Titans',
#                     'gujarat': 'Gujarat Titans',
#                     'lsg': 'Lucknow Super Giants',
#                     'lucknow': 'Lucknow Super Giants'
#                 }
                
#                 team1_full = team_map.get(team1, team1.title())
#                 team2_full = team_map.get(team2, team2.title())
                
#                 # Return proper comparison SQL
#                 return f"""
# SELECT 
#     '{team1_full}' as team,
#     COUNT(*) as total_matches,
#     SUM(CASE WHEN match_winner_name = '{team1_full}' THEN 1 ELSE 0 END) as wins,
#     ROUND(100.0 * SUM(CASE WHEN match_winner_name = '{team1_full}' THEN 1 ELSE 0 END) / COUNT(*), 1) as win_percentage
# FROM matches
# WHERE team1_name = '{team1_full}' OR team2_name = '{team1_full}'
# UNION ALL
# SELECT 
#     '{team2_full}' as team,
#     COUNT(*) as total_matches,
#     SUM(CASE WHEN match_winner_name = '{team2_full}' THEN 1 ELSE 0 END) as wins,
#     ROUND(100.0 * SUM(CASE WHEN match_winner_name = '{team2_full}' THEN 1 ELSE 0 END) / COUNT(*), 1) as win_percentage
# FROM matches
# WHERE team1_name = '{team2_full}' OR team2_name = '{team2_full}'
#                 """.strip()
        
#         # Pattern: "Head to head Team A vs Team B"
#         if ('head' in question_lower or 'h2h' in question_lower) and ' vs ' in question_lower:
#             parts = question_lower.replace('head to head', '').replace('h2h', '').split(' vs ')
#             if len(parts) == 2:
#                 team1 = parts[0].strip()
#                 team2 = parts[1].strip()
                
#                 team_map = {
#                     'mi': 'Mumbai Indians', 'mumbai': 'Mumbai Indians', 'mumbai indians': 'Mumbai Indians',
#                     'csk': 'Chennai Super Kings', 'chennai': 'Chennai Super Kings', 'chennai super kings': 'Chennai Super Kings',
#                     'rcb': 'Royal Challengers Bangalore', 'kkr': 'Kolkata Knight Riders',
#                     'dc': 'Delhi Capitals', 'pbks': 'Punjab Kings', 'rr': 'Rajasthan Royals',
#                     'srh': 'Sunrisers Hyderabad', 'gt': 'Gujarat Titans', 'lsg': 'Lucknow Super Giants'
#                 }
                
#                 team1_full = team_map.get(team1, team1.title())
#                 team2_full = team_map.get(team2, team2.title())
                
#                 return f"""
# SELECT 
#     '{team1_full}' as team,
#     SUM(CASE WHEN match_winner_name = '{team1_full}' THEN 1 ELSE 0 END) as wins
# FROM matches
# WHERE (team1_name = '{team1_full}' AND team2_name = '{team2_full}')
#    OR (team1_name = '{team2_full}' AND team2_name = '{team1_full}')
# UNION ALL
# SELECT 
#     '{team2_full}' as team,
#     SUM(CASE WHEN match_winner_name = '{team2_full}' THEN 1 ELSE 0 END) as wins
# FROM matches
# WHERE (team1_name = '{team1_full}' AND team2_name = '{team2_full}')
#    OR (team1_name = '{team2_full}' AND team2_name = '{team1_full}')
#                 """.strip()
        
#         # Otherwise use Gemini for SQL generation
#         model = genai.GenerativeModel('gemini-exp-1206')  # Use latest text model for SQL
#         schema = """Database Schema:

# Table: teams (team_id, team_name, short_name, is_active)
# Table: matches (match_id, season, match_date, venue, city, team1_name, team2_name, 
#                toss_winner_name, toss_decision, match_winner_name, win_by_runs, 
#                win_by_wickets, player_of_match, result)
# Table: deliveries (match_id, innings, batter, non_striker, bowler, over_number, ball_number,
#                    batter_runs, extras, total_runs, is_wicket, player_out, wicket_kind)

# CRITICAL RULES FOR PLAYER QUERIES:
# - Player names are stored as TEXT in 'batter' and 'bowler' columns (e.g., 'V Kohli', 'RG Sharma')
# - NEVER query player_id or team_batting_id - query the actual NAME columns (batter, bowler)
# - For run scorers: SELECT batter as player, SUM(batter_runs) as runs FROM deliveries
# - For wicket takers: SELECT bowler as player, SUM(is_wicket) as wickets FROM deliveries
# - ALWAYS use column aliases to make output readable (e.g., 'total_runs' not 'sum')

# Team name rules:
# - Full names: 'Mumbai Indians', 'Chennai Super Kings', 'Royal Challengers Bangalore'
# - NEVER use team IDs in SELECT - always use team_name

# Data: 1,169 matches, 18 seasons (2008-2025), 16 teams, 200k+ deliveries"""
        
#         prompt = f"""You are an expert SQL developer for an IPL cricket database.

# {schema}

# User Question: {question}

# CRITICAL: 
# - For player statistics, query 'batter' and 'bowler' TEXT columns (NOT IDs)
# - For team statistics, query 'team_name' TEXT columns (NOT IDs)
# - Return ONLY valid SQL - no markdown, no explanations
# - Use readable column aliases (player, total_runs, total_wickets)
# - Add LIMIT 20 for large result sets

# Examples of CORRECT queries:
# ✅ SELECT batter as player, SUM(batter_runs) as total_runs FROM deliveries GROUP BY batter ORDER BY total_runs DESC LIMIT 10
# ✅ SELECT bowler as player, SUM(is_wicket) as total_wickets FROM deliveries GROUP BY bowler ORDER BY total_wickets DESC LIMIT 10
# ✅ SELECT team_name as team, COUNT(*) as matches FROM matches WHERE team1_name = 'Team' OR team2_name = 'Team'

# Examples of WRONG queries:
# ❌ SELECT team_batting_id, player_id FROM deliveries (NEVER query IDs)
# ❌ SELECT COUNT(*) FROM deliveries (missing GROUP BY and readable columns)

# Generate the SQL now:"""
        
#         response = model.generate_content(prompt)
#         sql = response.text.strip()
        
#         # Remove ALL markdown artifacts
#         sql = sql.replace('```sql', '')
#         sql = sql.replace('```sqlite', '')
#         sql = sql.replace('```SQL', '')
#         sql = sql.replace('```', '')
#         sql = sql.replace('`', '')
        
#         # Remove common prefixes
#         sql = sql.replace('sqlite', '', 1)
#         sql = sql.replace('ite', '', 1)
#         sql = sql.replace('SQLite', '', 1)
        
#         # Clean up whitespace
#         sql = sql.strip()
        
#         # Ensure it starts with SELECT, WITH, INSERT, UPDATE, or DELETE
#         if not any(sql.upper().startswith(kw) for kw in ['SELECT', 'WITH', 'INSERT', 'UPDATE', 'DELETE']):
#             for keyword in ['SELECT', 'WITH', 'INSERT', 'UPDATE', 'DELETE']:
#                 if keyword in sql.upper():
#                     idx = sql.upper().index(keyword)
#                     sql = sql[idx:]
#                     break
        
#         return sql
#     except Exception as e:
#         return f"Error: {e}"

# def generate_insight_from_data(question, data):
#     """Generate insights from data"""
#     try:
#         model = genai.GenerativeModel('gemini-exp-1206')  # Use text model for analysis
#         prompt = f"""You are a cricket analyst.

# User asked: {question}
# Data: {data.head(10).to_string() if len(data) > 0 else "No results"}

# Provide a 2-3 sentence analysis with the answer and one interesting insight."""
#         response = model.generate_content(prompt)
#         return response.text
#     except Exception as e:
#         return f"Analysis unavailable: {e}"

# def load_database_data_options():
#     """Pre-configured data queries"""
#     return {
#         "Team Statistics": {
#             "query": """
#                 SELECT t.team_name, COUNT(m.match_id) as total_matches,
#                     SUM(CASE WHEN m.match_winner_name = t.team_name THEN 1 ELSE 0 END) as wins,
#                     ROUND(100.0 * SUM(CASE WHEN m.match_winner_name = t.team_name THEN 1 ELSE 0 END) / COUNT(m.match_id), 1) as win_percentage
#                 FROM teams t
#                 LEFT JOIN matches m ON t.team_name = m.team1_name OR t.team_name = m.team2_name
#                 WHERE t.is_active = 1
#                 GROUP BY t.team_name
#                 ORDER BY win_percentage DESC
#             """,
#             "description": "Overall statistics for all active teams"
#         },
#         "Toss Impact": {
#             "query": """
#                 SELECT toss_decision, COUNT(*) as total,
#                     SUM(CASE WHEN toss_winner_id = match_winner_id THEN 1 ELSE 0 END) as wins,
#                     ROUND(100.0 * SUM(CASE WHEN toss_winner_id = match_winner_id THEN 1 ELSE 0 END) / COUNT(*), 1) as win_pct
#                 FROM matches
#                 WHERE toss_decision IS NOT NULL
#                 GROUP BY toss_decision
#             """,
#             "description": "Win rates: bat vs field first"
#         },
#         "Top Venues": {
#             "query": """
#                 SELECT venue, city, COUNT(*) as matches
#                 FROM matches WHERE venue IS NOT NULL
#                 GROUP BY venue, city ORDER BY matches DESC LIMIT 10
#             """,
#             "description": "Top 10 stadiums by matches"
#         },
#         "Recent Seasons": {
#             "query": """
#                 SELECT season, COUNT(*) as matches, 
#                     COUNT(DISTINCT venue) as venues,
#                     COUNT(DISTINCT team1_name) as teams
#                 FROM matches WHERE season >= 2020
#                 GROUP BY season ORDER BY season DESC
#             """,
#             "description": "Recent IPL seasons (2020+)"
#         }
#     }

# # ==================== ENHANCED CSS ====================

# def load_css():
#     """Load custom CSS with enhanced table styling"""
#     st.markdown("""
#         <style>
#         .main { padding: 0rem 1rem; }
#         .metric-card {
#             background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#             padding: 1.5rem; border-radius: 10px; color: white; text-align: center;
#             box-shadow: 0 4px 6px rgba(0,0,0,0.1);
#         }
#         .metric-value { font-size: 2.5rem; font-weight: bold; margin: 0.5rem 0; }
#         .metric-label { font-size: 1rem; opacity: 0.9; }
#         h1 { color: #667eea; font-weight: 700; }
#         h2 { color: #764ba2; }
#         h3 { color: #667eea; }
#         .stButton>button {
#             background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#             color: white; border: none; padding: 0.5rem 2rem;
#             border-radius: 5px; font-weight: 600;
#         }
#         .stButton>button:hover {
#             opacity: 0.9; transform: translateY(-2px);
#             transition: all 0.3s ease;
#         }
#         [data-testid="stSidebar"] {
#             background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
#         }
#         [data-testid="stSidebar"] * { color: white !important; }
        
#         /* ENHANCED TABLE STYLING - FIXED */
#         div[data-testid="stDataFrame"] > div {
#             border-radius: 8px;
#             overflow: hidden;
#         }
        
#         /* Target the actual table element */
#         div[data-testid="stDataFrame"] table {
#             border-collapse: collapse !important;
#         }
        
#         /* Header styling */
#         div[data-testid="stDataFrame"] thead th {
#             background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
#             color: white !important;
#             font-weight: 700 !important;
#             font-size: 0.95rem !important;
#             padding: 12px 8px !important;
#             text-transform: uppercase !important;
#             letter-spacing: 0.5px !important;
#             border: none !important;
#         }
        
#         /* Alternating row colors */
#         div[data-testid="stDataFrame"] tbody tr:nth-child(even) td {
#             background-color: rgba(102, 126, 234, 0.08) !important;
#         }
        
#         div[data-testid="stDataFrame"] tbody tr:nth-child(odd) td {
#             background-color: rgba(255, 255, 255, 0.02) !important;
#         }
        
#         /* Hover effect */
#         div[data-testid="stDataFrame"] tbody tr:hover td {
#             background-color: rgba(102, 126, 234, 0.15) !important;
#             transition: all 0.2s ease !important;
#         }
        
#         /* Cell styling */
#         div[data-testid="stDataFrame"] tbody td {
#             padding: 10px 8px !important;
#             border-bottom: 1px solid rgba(0,0,0,0.1) !important;
#         }
#         </style>
#     """, unsafe_allow_html=True)

# # ==================== CHART FUNCTIONS ====================

# def create_win_trend_chart(matches_df):
#     """Win trend over seasons"""
#     wins_by_season = matches_df.groupby(['season', 'match_winner_name']).size().reset_index(name='wins')
#     top_teams = ['Mumbai Indians', 'Chennai Super Kings', 'Kolkata Knight Riders', 
#                  'Royal Challengers Bangalore', 'Delhi Capitals', 'Sunrisers Hyderabad']
#     wins_filtered = wins_by_season[wins_by_season['match_winner_name'].isin(top_teams)]
    
#     fig = px.line(wins_filtered, x='season', y='wins', color='match_winner_name',
#                   title='🏆 Team Performance Trends Over Seasons', markers=True)
#     fig.update_layout(height=500, hovermode='x unified',
#                      legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
#                      plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
#     return fig

# def create_toss_impact_chart(matches_df):
#     """Toss impact visualization"""
#     toss_data = matches_df[matches_df['toss_decision'].notna()].copy()
#     toss_data['won_after_toss'] = (toss_data['toss_winner_id'] == toss_data['match_winner_id'])
#     impact = toss_data.groupby('toss_decision')['won_after_toss'].agg(['sum', 'count']).reset_index()
#     impact['win_percentage'] = (impact['sum'] / impact['count'] * 100).round(1)
    
#     fig = go.Figure(data=[go.Bar(x=impact['toss_decision'], y=impact['win_percentage'],
#                                  text=impact['win_percentage'].astype(str) + '%', textposition='auto',
#                                  marker=dict(color=['#667eea', '#764ba2'], line=dict(color='white', width=2)))])
#     fig.update_layout(title='⚖️ Toss Impact: Bat First vs Field First', height=400,
#                      plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', showlegend=False)
#     return fig

# def create_team_comparison_chart(team_stats_df):
#     """Team comparison bar chart"""
#     top_10 = team_stats_df.head(10)
#     fig = go.Figure(data=[go.Bar(y=top_10['team'], x=top_10['win_percentage'], orientation='h',
#                                  text=top_10['win_percentage'].astype(str) + '%', textposition='auto',
#                                  marker=dict(color=top_10['win_percentage'], colorscale='Viridis',
#                                            showscale=True, colorbar=dict(title="Win %")))])
#     fig.update_layout(title='📊 Top 10 Teams by Win Percentage', height=500,
#                      plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
#     return fig

# def create_venue_chart(matches_df):
#     """Top venues chart"""
#     venue_counts = matches_df['venue'].value_counts().head(10).reset_index()
#     venue_counts.columns = ['venue', 'matches']
#     fig = px.bar(venue_counts, x='matches', y='venue', orientation='h',
#                  title='🏟️ Top 10 Venues by Matches Hosted',
#                  color='matches', color_continuous_scale='Blues')
#     fig.update_layout(height=450, showlegend=False,
#                      plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
#     return fig

# def create_season_matches_chart(matches_df):
#     """Matches per season chart"""
#     season_counts = matches_df.groupby('season').size().reset_index(name='matches')
#     fig = px.area(season_counts, x='season', y='matches',
#                   title='📈 Matches Played Per Season',
#                   color_discrete_sequence=['#667eea'])
#     fig.update_layout(height=400, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
#     return fig

# def create_team_season_performance(team_name, matches_df):
#     """Team performance over seasons"""
#     team_matches = matches_df[
#         (matches_df['team1_name'] == team_name) | (matches_df['team2_name'] == team_name)
#     ].copy()
#     team_matches['is_win'] = team_matches['match_winner_name'] == team_name
#     season_perf = team_matches.groupby('season').agg({
#         'match_id': 'count', 'is_win': 'sum'
#     }).reset_index()
#     season_perf.columns = ['season', 'matches', 'wins']
#     season_perf['losses'] = season_perf['matches'] - season_perf['wins']
    
#     fig = go.Figure()
#     fig.add_trace(go.Bar(x=season_perf['season'], y=season_perf['wins'], name='Wins',
#                         marker_color='#667eea', text=season_perf['wins'], textposition='auto'))
#     fig.add_trace(go.Bar(x=season_perf['season'], y=season_perf['losses'], name='Losses',
#                         marker_color='#764ba2', text=season_perf['losses'], textposition='auto'))
#     fig.update_layout(title=f'📊 {team_name} - Season by Season Performance',
#                      barmode='stack', height=400,
#                      plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
#                      legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
#     return fig

# def create_win_loss_pie(team_name, matches_df):
#     """Win/loss pie chart"""
#     team_matches = matches_df[
#         (matches_df['team1_name'] == team_name) | (matches_df['team2_name'] == team_name)
#     ].copy()
#     wins = (team_matches['match_winner_name'] == team_name).sum()
#     losses = len(team_matches) - wins
    
#     fig = go.Figure(data=[go.Pie(labels=['Wins', 'Losses'], values=[wins, losses], hole=0.4,
#                                  marker=dict(colors=['#667eea', '#764ba2']),
#                                  textinfo='label+percent', textfont_size=14)])
#     fig.update_layout(title=f'🎯 {team_name} - Overall Win/Loss', height=400,
#                      plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
#     return fig

# def create_h2h_donut(team1, team2, matches_df):
#     """H2H donut chart"""
#     h2h_matches = matches_df[
#         ((matches_df['team1_name'] == team1) & (matches_df['team2_name'] == team2)) |
#         ((matches_df['team1_name'] == team2) & (matches_df['team2_name'] == team1))
#     ]
#     team1_wins = (h2h_matches['match_winner_name'] == team1).sum()
#     team2_wins = (h2h_matches['match_winner_name'] == team2).sum()
    
#     fig = go.Figure(data=[go.Pie(labels=[team1, team2], values=[team1_wins, team2_wins],
#                                  hole=0.5, marker=dict(colors=['#667eea', '#764ba2']),
#                                  textinfo='label+value', textfont_size=14)])
#     fig.update_layout(title='🏆 Head to Head Wins', height=400,
#                      annotations=[dict(text=f'{team1_wins + team2_wins}<br>Matches', 
#                                      x=0.5, y=0.5, font_size=20, showarrow=False)],
#                      plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
#     return fig

# # ==================== MAIN APP ====================

# def main():
#     """Main dashboard"""
#     load_css()
    
#     # Sidebar
#     with st.sidebar:
#         st.title("🏏 IPL Analytics")
#         st.markdown("---")
        
#         page = st.radio("Navigate to:",
#             ["🏠 Home", "🏏 Team Analysis", "📊 Season Insights", "🌟 Player Records", "🤖 AI Dashboard"],  # FIXED: Removed unimplemented pages
#             label_visibility="collapsed")
        
#         st.markdown("---")
#         st.subheader("Quick Stats")
        
#         try:
#             matches = load_matches()
#             teams = load_teams()
#             st.metric("Total Matches", f"{len(matches):,}")
#             st.metric("Total Teams", len(teams))
#             st.metric("Seasons", matches['season'].nunique())
#         except:
#             st.warning("Loading...")
        
#         st.markdown("---")
#         st.caption("📊 Data: 2008-2025")
    
#     # Route to pages
#     if page == "🏠 Home":
#         show_home_page()
#     elif page == "🏏 Team Analysis":
#         show_team_analysis()
#     elif page == "📊 Season Insights":
#         show_season_insights()
#     elif page == "🌟 Player Records":
#         show_player_records()
#     elif page == "🤖 AI Dashboard":
#         show_ai_dashboard()

# # ==================== PAGE FUNCTIONS ====================

# def show_home_page():
#     """Home page - COMPLETELY REDESIGNED"""
#     st.title("🏏 IPL Cricket Analytics Dashboard")
#     st.markdown("### Welcome to Complete IPL Analysis")
    
#     try:
#         matches = load_matches()
#         teams = load_teams()
#         team_stats = get_team_stats()

#         if matches.empty:
#             st.warning("⚠️ No data loaded")
#             return

#         # ============ SECTION 1: KEY METRICS ============
#         col1, col2, col3, col4 = st.columns(4)
        
#         with col1:
#             st.markdown(f"""<div class="metric-card">
#                 <div class="metric-label">Total Matches</div>
#                 <div class="metric-value">{len(matches):,}</div>
#             </div>""", unsafe_allow_html=True)
#         with col2:
#             st.markdown(f"""<div class="metric-card">
#                 <div class="metric-label">IPL Teams</div>
#                 <div class="metric-value">{len(teams)}</div>
#             </div>""", unsafe_allow_html=True)
#         with col3:
#             st.markdown(f"""<div class="metric-card">
#                 <div class="metric-label">Seasons</div>
#                 <div class="metric-value">{matches['season'].nunique()}</div>
#             </div>""", unsafe_allow_html=True)
#         with col4:
#             st.markdown(f"""<div class="metric-card">
#                 <div class="metric-label">Venues</div>
#                 <div class="metric-value">{matches['venue'].nunique()}</div>
#             </div>""", unsafe_allow_html=True)
        
#         st.markdown("<br>", unsafe_allow_html=True)
        
#         # ============ SECTION 2: VISUAL INSIGHTS ============
#         st.markdown("## 📈 Visual Insights")
        
#         # Row 1: Team Trends + Toss Impact
#         col1, col2 = st.columns(2)
        
#         with col1:
#             # TOP 5 TEAMS PERFORMANCE TREND (Less cluttered)
#             wins_by_season = matches.groupby(['season', 'match_winner_name']).size().reset_index(name='wins')
            
#             # Get top 5 teams by total wins
#             top_teams = matches['match_winner_name'].value_counts().head(5).index.tolist()
#             wins_filtered = wins_by_season[wins_by_season['match_winner_name'].isin(top_teams)]
            
#             fig = px.line(wins_filtered, x='season', y='wins', color='match_winner_name',
#                           title='🏆 Top 5 Teams Performance Trends',
#                           markers=True, line_shape='spline')
#             fig.update_layout(
#                 height=400, 
#                 hovermode='x unified',
#                 legend=dict(
#                     title="Team",
#                     orientation="v",
#                     yanchor="top",
#                     y=0.99,
#                     xanchor="right",
#                     x=0.99,
#                     bgcolor="rgba(0,0,0,0.5)"
#                 ),
#                 plot_bgcolor='rgba(0,0,0,0)', 
#                 paper_bgcolor='rgba(0,0,0,0)',
#                 xaxis_title="Season",
#                 yaxis_title="Wins"
#             )
#             st.plotly_chart(fig, use_container_width=True)
        
#         with col2:
#             # 3D PIE CHART FOR TOSS IMPACT (Coin-like)
#             toss_data = matches[matches['toss_decision'].notna()].copy()
#             toss_data['won_after_toss'] = (toss_data['toss_winner_id'] == toss_data['match_winner_id'])
            
#             # Calculate stats
#             bat_first = toss_data[toss_data['toss_decision'] == 'bat']
#             field_first = toss_data[toss_data['toss_decision'] == 'field']
            
#             bat_win_pct = (bat_first['won_after_toss'].sum() / len(bat_first) * 100) if len(bat_first) > 0 else 0
#             field_win_pct = (field_first['won_after_toss'].sum() / len(field_first) * 100) if len(field_first) > 0 else 0
            
#             # Create 3D pie chart
#             labels = ['Bat First', 'Field First']
#             values = [bat_win_pct, field_win_pct]
#             colors = ['#667eea', '#764ba2']
            
#             fig = go.Figure(data=[go.Pie(
#                 labels=labels,
#                 values=values,
#                 hole=0.3,
#                 marker=dict(
#                     colors=colors,
#                     line=dict(color='white', width=3)
#                 ),
#                 textinfo='label+percent',
#                 textfont_size=14,
#                 pull=[0.05, 0.05],  # Slightly pull out for 3D effect
#                 rotation=45
#             )])
            
#             fig.update_layout(
#                 title='🪙 Toss Impact: Win After Winning Toss',
#                 height=400,
#                 plot_bgcolor='rgba(0,0,0,0)',
#                 paper_bgcolor='rgba(0,0,0,0)',
#                 showlegend=True,
#                 legend=dict(
#                     orientation="h",
#                     yanchor="bottom",
#                     y=-0.15,
#                     xanchor="center",
#                     x=0.5
#                 ),
#                 annotations=[dict(
#                     text=f'{bat_win_pct:.1f}% vs {field_win_pct:.1f}%',
#                     x=0.5, y=0.5,
#                     font_size=16,
#                     showarrow=False,
#                     font=dict(color='#667eea')
#                 )]
#             )
#             st.plotly_chart(fig, use_container_width=True)
        
#         # Row 2: Top 10 Teams + Win Methods
#         col1, col2 = st.columns(2)
        
#         with col1:
#             # TOP 10 TEAMS - SORTED HIGH TO LOW
#             top_10 = team_stats.sort_values('win_percentage', ascending=False).head(10)
            
#             fig = go.Figure(data=[go.Bar(
#                 y=top_10['team'],
#                 x=top_10['win_percentage'],
#                 orientation='h',
#                 text=top_10['win_percentage'].round(1).astype(str) + '%',
#                 textposition='auto',
#                 marker=dict(
#                     color=top_10['win_percentage'],
#                     colorscale='Viridis',
#                     showscale=True,
#                     colorbar=dict(title="Win %", x=1.15)
#                 ),
#                 hovertemplate='<b>%{y}</b><br>Win %: %{x:.1f}%<br>Matches: %{customdata[0]}<br>Wins: %{customdata[1]}<extra></extra>',
#                 customdata=top_10[['matches_played', 'wins']].values
#             )])
            
#             fig.update_layout(
#                 title='📊 Top 10 Teams by Win Percentage',
#                 height=450,
#                 plot_bgcolor='rgba(0,0,0,0)',
#                 paper_bgcolor='rgba(0,0,0,0)',
#                 xaxis_title="Win Percentage (%)",
#                 yaxis_title="",
#                 yaxis=dict(autorange="reversed")  # High to low
#             )
#             st.plotly_chart(fig, use_container_width=True)
        
#         with col2:
#             # WIN METHODS DISTRIBUTION
#             win_by_runs = matches[matches['win_by_runs'] > 0]['win_by_runs'].count()
#             win_by_wickets = matches[matches['win_by_wickets'] > 0]['win_by_wickets'].count()
            
#             fig = go.Figure(data=[go.Pie(
#                 labels=['Won by Runs', 'Won by Wickets'],
#                 values=[win_by_runs, win_by_wickets],
#                 hole=0.4,
#                 marker=dict(colors=['#667eea', '#764ba2']),
#                 textinfo='label+percent+value',
#                 textfont_size=13
#             )])
            
#             fig.update_layout(
#                 title='⚔️ Match Winning Methods',
#                 height=450,
#                 plot_bgcolor='rgba(0,0,0,0)',
#                 paper_bgcolor='rgba(0,0,0,0)',
#                 annotations=[dict(
#                     text=f'{win_by_runs + win_by_wickets}<br>Matches',
#                     x=0.5, y=0.5,
#                     font_size=18,
#                     showarrow=False
#                 )]
#             )
#             st.plotly_chart(fig, use_container_width=True)
        
#         # ============ SECTION 3: PLAYER SPOTLIGHT ============
#         st.markdown("## 🌟 Player Spotlight")

#         # Check if deliveries table has data
#         try:
#             with get_database_connection() as conn:
#                 cursor = conn.cursor()
#                 cursor.execute("SELECT COUNT(*) FROM deliveries")
#                 deliveries_count = cursor.fetchone()[0]

#                 if deliveries_count > 0:
#                     col1, col2 = st.columns(2)

#                     with col1:
#                         # TOP 10 RUN SCORERS
#                         top_scorers = pd.read_sql_query("""
#                             SELECT batter as player,
#                                    SUM(batter_runs) as total_runs,
#                                    COUNT(DISTINCT match_id) as matches,
#                                    ROUND(SUM(batter_runs) * 1.0 / COUNT(DISTINCT match_id), 1) as avg_per_match
#                             FROM deliveries
#                             WHERE batter IS NOT NULL
#                             GROUP BY batter
#                             ORDER BY total_runs DESC
#                             LIMIT 10
#                         """, conn)

#                         fig = go.Figure(data=[go.Bar(
#                             y=top_scorers['player'],
#                             x=top_scorers['total_runs'],
#                             orientation='h',
#                             text=top_scorers['total_runs'],
#                             textposition='auto',
#                             marker=dict(
#                                 color=top_scorers['total_runs'],
#                                 colorscale='Oranges',
#                                 showscale=False
#                             ),
#                             hovertemplate='<b>%{y}</b><br>Runs: %{x}<br>Matches: %{customdata[0]}<br>Avg: %{customdata[1]}/match<extra></extra>',
#                             customdata=top_scorers[['matches', 'avg_per_match']].values
#                         )])

#                         fig.update_layout(
#                             title='🏏 Top 10 Run Scorers (All-Time)',
#                             height=450,
#                             plot_bgcolor='rgba(0,0,0,0)',
#                             paper_bgcolor='rgba(0,0,0,0)',
#                             xaxis_title="Total Runs",
#                             yaxis=dict(autorange="reversed")
#                         )
#                         st.plotly_chart(fig, use_container_width=True)

#                     with col2:
#                         # TOP 10 WICKET TAKERS
#                         top_bowlers = pd.read_sql_query("""
#                             SELECT bowler as player,
#                                    SUM(is_wicket) as total_wickets,
#                                    COUNT(DISTINCT match_id) as matches,
#                                    ROUND(SUM(is_wicket) * 1.0 / COUNT(DISTINCT match_id), 2) as avg_per_match
#                             FROM deliveries
#                             WHERE bowler IS NOT NULL
#                             GROUP BY bowler
#                             ORDER BY total_wickets DESC
#                             LIMIT 10
#                         """, conn)

#                         fig = go.Figure(data=[go.Bar(
#                             y=top_bowlers['player'],
#                             x=top_bowlers['total_wickets'],
#                             orientation='h',
#                             text=top_bowlers['total_wickets'],
#                             textposition='auto',
#                             marker=dict(
#                                 color=top_bowlers['total_wickets'],
#                                 colorscale='Reds',
#                                 showscale=False
#                             ),
#                             hovertemplate='<b>%{y}</b><br>Wickets: %{x}<br>Matches: %{customdata[0]}<br>Avg: %{customdata[1]}/match<extra></extra>',
#                             customdata=top_bowlers[['matches', 'avg_per_match']].values
#                         )])

#                         fig.update_layout(
#                             title='🎯 Top 10 Wicket Takers (All-Time)',
#                             height=450,
#                             plot_bgcolor='rgba(0,0,0,0)',
#                             paper_bgcolor='rgba(0,0,0,0)',
#                             xaxis_title="Total Wickets",
#                             yaxis=dict(autorange="reversed")
#                         )
#                         st.plotly_chart(fig, use_container_width=True)
#                 else:
#                     st.info("💡 Player statistics available after loading ball-by-ball data")

#         except Exception as e:
#             st.info("💡 Player statistics will appear once ball-by-ball data is loaded")
        
#         # ============ SECTION 4: SEASON ANALYSIS ============
#         st.markdown("## 📊 Season Analysis")
        
#         col1, col2 = st.columns(2)
        
#         with col1:
#             # AVERAGE RUNS PER SEASON (Scoring trends)
#             try:
#                 with get_database_connection() as conn:
#                     scoring_trends = pd.read_sql_query("""
#                         SELECT m.season,
#                                AVG(d.total_runs) as avg_runs_per_ball,
#                                COUNT(DISTINCT m.match_id) as matches
#                         FROM matches m
#                         JOIN deliveries d ON m.match_id = d.match_id
#                         GROUP BY m.season
#                         ORDER BY m.season
#                     """, conn)
                
#                 if len(scoring_trends) > 0:
#                     # Calculate runs per match
#                     scoring_trends['runs_per_match'] = scoring_trends['avg_runs_per_ball'] * 240  # Approx 240 balls/match
                    
#                     fig = px.line(scoring_trends, 
#                                   x='season', 
#                                   y='runs_per_match',
#                                   title='📈 Scoring Evolution Over Seasons',
#                                   markers=True,
#                                   line_shape='spline')
                    
#                     fig.update_traces(
#                         line=dict(color='#667eea', width=3),
#                         marker=dict(size=8, color='#764ba2')
#                     )
                    
#                     fig.update_layout(
#                         height=400,
#                         plot_bgcolor='rgba(0,0,0,0)',
#                         paper_bgcolor='rgba(0,0,0,0)',
#                         xaxis_title="Season",
#                         yaxis_title="Avg Runs per Match",
#                         hovermode='x'
#                     )
#                     st.plotly_chart(fig, use_container_width=True)
#                 else:
#                     raise Exception("No data")
#             except:
#                 # Fallback: Matches per season (simple version)
#                 season_counts = matches.groupby('season').size().reset_index(name='matches')
#                 fig = px.bar(season_counts, x='season', y='matches',
#                             title='📊 Matches Played Per Season',
#                             color='matches',
#                             color_continuous_scale='Blues')
#                 fig.update_layout(height=400, showlegend=False,
#                                  plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
#                 st.plotly_chart(fig, use_container_width=True)
        
#         with col2:
#             # TOP VENUES BY MATCHES
#             venue_counts = matches['venue'].value_counts().head(10).reset_index()
#             venue_counts.columns = ['venue', 'matches']
            
#             fig = px.bar(venue_counts, 
#                          x='matches', 
#                          y='venue', 
#                          orientation='h',
#                          title='🏟️ Top 10 Venues by Matches Hosted',
#                          color='matches', 
#                          color_continuous_scale='Blues')
            
#             fig.update_layout(
#                 height=400, 
#                 showlegend=False,
#                 plot_bgcolor='rgba(0,0,0,0)', 
#                 paper_bgcolor='rgba(0,0,0,0)',
#                 yaxis=dict(autorange="reversed")
#             )
#             st.plotly_chart(fig, use_container_width=True)
        
#         # ============ SECTION 5: RECENT MATCHES ============
#         with st.expander("📅 Recent Matches", expanded=False):
#             recent = matches.head(15)[['match_date', 'season', 'team1_name', 'team2_name', 'match_winner_name', 'venue', 'city']]
#             recent = format_columns(recent)
#             st.dataframe(recent, use_container_width=True, hide_index=True, height=400)
            
#     except Exception as e:
#         st.error(f"❌ Error loading dashboard: {e}")
#         import traceback
#         st.code(traceback.format_exc())

# def show_team_analysis():
#     """Team analysis page with formatted tables"""
#     st.title("🏏 Team Analysis")
    
#     try:
#         teams = load_teams()
#         matches = load_matches()
        
#         if teams.empty or matches.empty:
#             st.warning("⚠️ No data")
#             return
        
#         active = teams[teams['is_active'] == 1]['team_name'].tolist()
#         selected = st.selectbox("Select Team", active)
        
#         if selected:
#             st.markdown(f"## {selected}")
#             with get_database_connection() as conn:  # FIXED
#                 stats = pd.read_sql_query(f"""
#                 WITH team_matches AS (
#                     SELECT * FROM matches 
#                     WHERE team1_name = '{selected}' OR team2_name = '{selected}'
#                 )
#                 SELECT
#                     COUNT(*) as total_matches,
#                     SUM(CASE WHEN match_winner_name = '{selected}' THEN 1 ELSE 0 END) as wins,
#                     ROUND(100.0 * SUM(CASE WHEN match_winner_name = '{selected}' THEN 1 ELSE 0 END) / COUNT(*), 1) as win_pct
#                 FROM team_matches
#                 """, conn)

#             col1, col2, col3 = st.columns(3)
#             with col1:
#                 st.metric("Matches", int(stats['total_matches'].iloc[0]))
#             with col2:
#                 st.metric("Wins", int(stats['wins'].iloc[0]))
#             with col3:
#                 st.metric("Win %", f"{stats['win_pct'].iloc[0]}%")
            
#             col1, col2 = st.columns(2)
#             with col1:
#                 st.plotly_chart(create_team_season_performance(selected, matches), use_container_width=True)
#             with col2:
#                 st.plotly_chart(create_win_loss_pie(selected, matches), use_container_width=True)
                
#     except Exception as e:
#         st.error(f"❌ Error: {e}")

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
#             st.dataframe(display, use_container_width=True, hide_index=True, height=600)
#         else:
#             total_pages = (len(display) - 1) // rows_per_page + 1
#             page = st.number_input("Page", min_value=1, max_value=total_pages, value=1)
#             start_idx = (page - 1) * rows_per_page
#             end_idx = start_idx + rows_per_page
            
#             st.dataframe(display.iloc[start_idx:end_idx], use_container_width=True, hide_index=True)
#             st.caption(f"Showing {start_idx + 1} to {min(end_idx, len(display))} of {len(display)} matches | Page {page} of {total_pages}")
        
#     except Exception as e:
#         st.error(f"❌ Error: {e}")

# def show_season_insights():
#     """Season insights with formatted tables"""
#     st.title("📊 Season Insights")
    
#     try:
#         matches = load_matches()
#         if matches.empty:
#             st.warning("⚠️ No data")
#             return
        
#         seasons = sorted(matches['season'].unique().tolist(), reverse=True)
#         selected = st.selectbox("Select Season", seasons)
        
#         if selected:
#             season_matches = matches[matches['season'] == selected]
#             st.markdown(f"## IPL {selected}")
            
#             col1, col2, col3 = st.columns(3)
#             with col1:
#                 st.metric("Matches", len(season_matches))
#             with col2:
#                 st.metric("Teams", season_matches['team1_name'].nunique())
#             with col3:
#                 st.metric("Venues", season_matches['venue'].nunique())
            
#             col1, col2 = st.columns(2)
            
#             with col1:
#                 team_wins = season_matches['match_winner_name'].value_counts().head(8)
#                 fig = px.bar(x=team_wins.values, y=team_wins.index, orientation='h',
#                             title=f'🏆 Top Teams - IPL {selected}')
#                 fig.update_layout(height=400, showlegend=False)
#                 st.plotly_chart(fig, use_container_width=True)
            
#             with col2:
#                 venue_dist = season_matches['venue'].value_counts().head(8)
#                 fig = px.pie(values=venue_dist.values, names=venue_dist.index,
#                             title=f'🏟️ Venues - IPL {selected}')
#                 fig.update_layout(height=400)
#                 st.plotly_chart(fig, use_container_width=True)
                
#     except Exception as e:
#         st.error(f"❌ Error: {e}")

# def show_head_to_head():
#     """Head to head with formatted tables"""
#     st.title("⚔️ Head to Head")
    
#     try:
#         teams = load_teams()
#         matches = load_matches()
        
#         if teams.empty or matches.empty:
#             st.warning("⚠️ No data")
#             return
        
#         active = teams[teams['is_active'] == 1]['team_name'].tolist()
        
#         col1, col2 = st.columns(2)
#         with col1:
#             team1 = st.selectbox("Team 1", active, key='t1')
#         with col2:
#             team2 = st.selectbox("Team 2", [t for t in active if t != team1], key='t2')
        
#         if team1 and team2:
#             st.markdown(f"## {team1} vs {team2}")
#             with get_database_connection() as conn:
#                 h2h = pd.read_sql_query(f"""
#                     SELECT COUNT(*) as total,
#                         SUM(CASE WHEN match_winner_name = '{team1}' THEN 1 ELSE 0 END) as team1_wins,
#                         SUM(CASE WHEN match_winner_name = '{team2}' THEN 1 ELSE 0 END) as team2_wins
#                     FROM matches
#                     WHERE (team1_name = '{team1}' AND team2_name = '{team2}')
#                        OR (team1_name = '{team2}' AND team2_name = '{team1}')
#                 """, conn)

#             col1, col2, col3 = st.columns(3)
#             with col1:
#                 st.metric(f"{team1} Wins", int(h2h['team1_wins'].iloc[0]))
#             with col2:
#                 st.metric("Total", int(h2h['total'].iloc[0]))
#             with col3:
#                 st.metric(f"{team2} Wins", int(h2h['team2_wins'].iloc[0]))

#             st.plotly_chart(create_h2h_donut(team1, team2, matches), use_container_width=True)
            
#     except Exception as e:
#         st.error(f"❌ Error: {e}")

# def show_player_records():
#     """Player Records page - COMPREHENSIVE STATISTICS"""
#     st.title("🌟 Player Records & Statistics")
#     st.markdown("### IPL's Greatest Performers")
    
#     try:
#         matches = load_matches()

#         # ============ FILTERS ============
#         st.markdown("## 🔍 Filters")
#         col1, col2, col3 = st.columns(3)

#         with col1:
#             seasons = ['All Time'] + sorted(matches['season'].unique().tolist(), reverse=True)
#             selected_season = st.selectbox("Season", seasons)

#         with col2:
#             stat_type = st.selectbox("View", ["Batting", "Bowling", "All-Round"])

#         with col3:
#             min_matches = st.number_input("Min Matches", min_value=1, value=10, step=5)

#         # Build season filter
#         season_filter = f"AND m.season = {selected_season}" if selected_season != 'All Time' else ""

#         with get_database_connection() as conn:
#             # Check if deliveries data exists
#             cursor = conn.cursor()
#             cursor.execute("SELECT COUNT(*) FROM deliveries")
#             deliveries_count = cursor.fetchone()[0]

#             if deliveries_count == 0:
#                 st.warning("⚠️ Player statistics require ball-by-ball data")
#                 st.info("💡 Load deliveries data to see player records")
#                 return

#             # ============ BATTING RECORDS ============
#             if stat_type in ["Batting", "All-Round"]:
#                 st.markdown("---")
#                 st.markdown("## 🏏 Batting Records")

#                 col1, col2 = st.columns(2)
            
#             with col1:
#                 # Top Run Scorers
#                 query = f"""
#                     SELECT d.batter as player,
#                            COUNT(DISTINCT d.match_id) as matches,
#                            SUM(d.batter_runs) as total_runs,
#                            MAX(innings_runs.runs) as highest_score,
#                            ROUND(AVG(innings_runs.runs), 1) as average,
#                            ROUND(SUM(d.batter_runs) * 100.0 / COUNT(*), 1) as strike_rate,
#                            SUM(CASE WHEN d.batter_runs = 6 THEN 1 ELSE 0 END) as sixes,
#                            SUM(CASE WHEN d.batter_runs = 4 THEN 1 ELSE 0 END) as fours
#                     FROM deliveries d
#                     JOIN matches m ON d.match_id = m.match_id
#                     LEFT JOIN (
#                         SELECT match_id, innings, batter, SUM(batter_runs) as runs
#                         FROM deliveries
#                         GROUP BY match_id, innings, batter
#                     ) innings_runs ON d.match_id = innings_runs.match_id 
#                                    AND d.innings = innings_runs.innings 
#                                    AND d.batter = innings_runs.batter
#                     WHERE d.batter IS NOT NULL {season_filter}
#                     GROUP BY d.batter
#                     HAVING matches >= {min_matches}
#                     ORDER BY total_runs DESC
#                     LIMIT 15
#                 """
#                 top_scorers = pd.read_sql_query(query, conn)
#                 top_scorers = format_columns(top_scorers)
                
#                 st.markdown("### 👑 Top Run Scorers")
#                 st.dataframe(top_scorers, use_container_width=True, hide_index=True, height=400)
                
#                 # Visualization
#                 fig = px.bar(top_scorers.head(10), 
#                             y='Player', x='Total Runs',
#                             orientation='h',
#                             title='Top 10 Run Scorers',
#                             color='Total Runs',
#                             color_continuous_scale='Oranges')
#                 fig.update_layout(height=400, yaxis=dict(autorange="reversed"),
#                                  plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
#                 st.plotly_chart(fig, use_container_width=True)
            
#             with col2:
#                 # Best Strike Rates
#                 query = f"""
#                     SELECT d.batter as player,
#                            COUNT(DISTINCT d.match_id) as matches,
#                            SUM(d.batter_runs) as total_runs,
#                            COUNT(*) as balls_faced,
#                            ROUND(SUM(d.batter_runs) * 100.0 / COUNT(*), 1) as strike_rate,
#                            SUM(CASE WHEN d.batter_runs = 6 THEN 1 ELSE 0 END) as sixes
#                     FROM deliveries d
#                     JOIN matches m ON d.match_id = m.match_id
#                     WHERE d.batter IS NOT NULL {season_filter}
#                     GROUP BY d.batter
#                     HAVING matches >= {min_matches} AND total_runs >= 200
#                     ORDER BY strike_rate DESC
#                     LIMIT 15
#                 """
#                 best_sr = pd.read_sql_query(query, conn)
#                 best_sr = format_columns(best_sr)
                
#                 st.markdown("### ⚡ Best Strike Rates")
#                 st.dataframe(best_sr, use_container_width=True, hide_index=True, height=400)
                
#                 # Visualization
#                 fig = px.bar(best_sr.head(10),
#                             y='Player', x='Strike Rate',
#                             orientation='h',
#                             title='Top 10 Strike Rates',
#                             color='Sixes',
#                             color_continuous_scale='Reds')
#                 fig.update_layout(height=400, yaxis=dict(autorange="reversed"),
#                                  plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
#                 st.plotly_chart(fig, use_container_width=True)
        
#         # ============ BOWLING RECORDS ============
#         if stat_type in ["Bowling", "All-Round"]:
#             st.markdown("---")
#             st.markdown("## 🎯 Bowling Records")
            
#             col1, col2 = st.columns(2)
            
#             with col1:
#                 # Top Wicket Takers
#                 query = f"""
#                     SELECT d.bowler as player,
#                            COUNT(DISTINCT d.match_id) as matches,
#                            SUM(d.is_wicket) as total_wickets,
#                            COUNT(*) as balls_bowled,
#                            SUM(d.total_runs) as runs_conceded,
#                            ROUND(SUM(d.total_runs) * 6.0 / COUNT(*), 2) as economy,
#                            ROUND(SUM(d.total_runs) * 1.0 / NULLIF(SUM(d.is_wicket), 0), 1) as average,
#                            ROUND(COUNT(*) * 1.0 / NULLIF(SUM(d.is_wicket), 0), 1) as strike_rate
#                     FROM deliveries d
#                     JOIN matches m ON d.match_id = m.match_id
#                     WHERE d.bowler IS NOT NULL {season_filter}
#                     GROUP BY d.bowler
#                     HAVING matches >= {min_matches}
#                     ORDER BY total_wickets DESC
#                     LIMIT 15
#                 """
#                 top_bowlers = pd.read_sql_query(query, conn)
#                 top_bowlers = format_columns(top_bowlers)
                
#                 st.markdown("### 🎯 Top Wicket Takers")
#                 st.dataframe(top_bowlers, use_container_width=True, hide_index=True, height=400)
                
#                 # Visualization
#                 fig = px.bar(top_bowlers.head(10),
#                             y='Player', x='Total Wickets',
#                             orientation='h',
#                             title='Top 10 Wicket Takers',
#                             color='Total Wickets',
#                             color_continuous_scale='Reds')
#                 fig.update_layout(height=400, yaxis=dict(autorange="reversed"),
#                                  plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
#                 st.plotly_chart(fig, use_container_width=True)
            
#             with col2:
#                 # Best Economy Rates
#                 query = f"""
#                     SELECT d.bowler as player,
#                            COUNT(DISTINCT d.match_id) as matches,
#                            SUM(d.is_wicket) as wickets,
#                            COUNT(*) as balls_bowled,
#                            SUM(d.total_runs) as runs_conceded,
#                            ROUND(SUM(d.total_runs) * 6.0 / COUNT(*), 2) as economy
#                     FROM deliveries d
#                     JOIN matches m ON d.match_id = m.match_id
#                     WHERE d.bowler IS NOT NULL {season_filter}
#                     GROUP BY d.bowler
#                     HAVING matches >= {min_matches} AND balls_bowled >= 200
#                     ORDER BY economy ASC
#                     LIMIT 15
#                 """
#                 best_economy = pd.read_sql_query(query, conn)
#                 best_economy = format_columns(best_economy)
                
#                 st.markdown("### 💰 Best Economy Rates")
#                 st.dataframe(best_economy, use_container_width=True, hide_index=True, height=400)
                
#                 # Visualization
#                 fig = px.bar(best_economy.head(10),
#                             y='Player', x='Economy',
#                             orientation='h',
#                             title='Top 10 Economy Rates',
#                             color='Wickets',
#                             color_continuous_scale='Greens')
#                 fig.update_layout(height=400, yaxis=dict(autorange="reversed"),
#                                  plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
#                 st.plotly_chart(fig, use_container_width=True)
        
#         # ============ PLAYER COMPARISON ============
#         st.markdown("---")
#         st.markdown("## 🔄 Player Comparison")
        
#         # Get all players
#         all_players = pd.read_sql_query(f"""
#             SELECT DISTINCT batter as player FROM deliveries
#             WHERE batter IS NOT NULL
#             UNION
#             SELECT DISTINCT bowler as player FROM deliveries
#             WHERE bowler IS NOT NULL
#             ORDER BY player
#         """, conn)['player'].tolist()
        
#         col1, col2, col3 = st.columns(3)
#         with col1:
#             player1 = st.selectbox("Player 1", all_players, key='p1')
#         with col2:
#             player2 = st.selectbox("Player 2", [p for p in all_players if p != player1], key='p2')
#         with col3:
#             player3 = st.selectbox("Player 3 (Optional)", ['None'] + [p for p in all_players if p not in [player1, player2]], key='p3')
        
#         if st.button("🔄 Compare Players", type="primary"):
#             players = [player1, player2] if player3 == 'None' else [player1, player2, player3]
            
#             # Get comparison data
#             comparison_data = []
#             for player in players:
#                 batting = pd.read_sql_query(f"""
#                     SELECT 
#                         '{player}' as player,
#                         COUNT(DISTINCT match_id) as matches,
#                         SUM(batter_runs) as runs,
#                         ROUND(SUM(batter_runs) * 100.0 / COUNT(*), 1) as strike_rate,
#                         SUM(CASE WHEN batter_runs = 6 THEN 1 ELSE 0 END) as sixes
#                     FROM deliveries
#                     WHERE batter = '{player}'
#                 """, conn)
                
#                 bowling = pd.read_sql_query(f"""
#                     SELECT 
#                         SUM(is_wicket) as wickets,
#                         ROUND(SUM(total_runs) * 6.0 / COUNT(*), 2) as economy
#                     FROM deliveries
#                     WHERE bowler = '{player}'
#                 """, conn)
                
#                 comparison_data.append({
#                     'Player': player,
#                     'Matches': int(batting['matches'].iloc[0]),
#                     'Runs': int(batting['runs'].iloc[0]),
#                     'Strike Rate': float(batting['strike_rate'].iloc[0]),
#                     'Sixes': int(batting['sixes'].iloc[0]),
#                     'Wickets': int(bowling['wickets'].iloc[0]) if bowling['wickets'].iloc[0] else 0,
#                     'Economy': float(bowling['economy'].iloc[0]) if bowling['economy'].iloc[0] else 0
#                 })
            
#             comp_df = pd.DataFrame(comparison_data)
            
#             col1, col2 = st.columns([1, 2])
            
#             with col1:
#                 st.dataframe(comp_df, use_container_width=True, hide_index=True)
            
#             with col2:
#                 # Radar chart
#                 categories = ['Runs', 'Strike Rate', 'Sixes', 'Wickets']
                
#                 fig = go.Figure()
                
#                 colors = ['#667eea', '#764ba2', '#f093fb']
#                 for idx, player in enumerate(players):
#                     player_data = comp_df[comp_df['Player'] == player].iloc[0]
#                     values = [
#                         player_data['Runs'] / comp_df['Runs'].max() * 100,
#                         player_data['Strike Rate'] / comp_df['Strike Rate'].max() * 100,
#                         player_data['Sixes'] / comp_df['Sixes'].max() * 100 if comp_df['Sixes'].max() > 0 else 0,
#                         player_data['Wickets'] / comp_df['Wickets'].max() * 100 if comp_df['Wickets'].max() > 0 else 0
#                     ]
                    
#                     fig.add_trace(go.Scatterpolar(
#                         r=values,
#                         theta=categories,
#                         fill='toself',
#                         name=player,
#                         line_color=colors[idx]
#                     ))
                
#                 fig.update_layout(
#                     polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
#                     title="Player Comparison Radar",
#                     height=400,
#                     plot_bgcolor='rgba(0,0,0,0)',
#                     paper_bgcolor='rgba(0,0,0,0)'
#                 )
#                 st.plotly_chart(fig, use_container_width=True)
        
#         # ============ HALL OF FAME ============
#         st.markdown("---")
#         st.markdown("## 🏆 Hall of Fame - All-Time Records")
        
#         col1, col2, col3 = st.columns(3)
        
#         with col1:
#             st.markdown("### 🎯 Highest Score")
#             query = """
#                 SELECT batter as player, match_id, SUM(batter_runs) as runs
#                 FROM deliveries
#                 GROUP BY match_id, innings, batter
#                 ORDER BY runs DESC
#                 LIMIT 5
#             """
#             highest = pd.read_sql_query(query, conn)
#             highest = format_columns(highest)
#             st.dataframe(highest, use_container_width=True, hide_index=True)
        
#         with col2:
#             st.markdown("### 🎯 Best Bowling")
#             query = """
#                 SELECT bowler as player, match_id, SUM(is_wicket) as wickets,
#                        SUM(total_runs) as runs
#                 FROM deliveries
#                 GROUP BY match_id, innings, bowler
#                 ORDER BY wickets DESC, runs ASC
#                 LIMIT 5
#             """
#             best_bowling = pd.read_sql_query(query, conn)
#             best_bowling = format_columns(best_bowling)
#             st.dataframe(best_bowling, use_container_width=True, hide_index=True)
        
#         with col3:
#             st.markdown("### 🎯 Most Sixes")
#             query = """
#                 SELECT batter as player, COUNT(*) as total_sixes
#                 FROM deliveries
#                 WHERE batter_runs = 6
#                 GROUP BY batter
#                 ORDER BY total_sixes DESC
#                 LIMIT 5
#             """
#             most_sixes = pd.read_sql_query(query, conn)
#             most_sixes = format_columns(most_sixes)
#             st.dataframe(most_sixes, use_container_width=True, hide_index=True)
        
#     except Exception as e:
#         st.error(f"❌ Error loading player records: {e}")
#         import traceback
#         st.code(traceback.format_exc())

# # ==================== AI DASHBOARD (REDESIGNED) ====================

# def show_ai_dashboard():
#     """AI Dashboard - THE USP FEATURE"""
#     st.title("🤖 AI-Powered Analytics Dashboard")
#     st.markdown("### Transform Data into Professional Visualizations with Google Gemini 2.0")
    
#     if not GEMINI_AVAILABLE:
#         st.error("❌ Install: `pip install google-generativeai python-dotenv`")
#         return
    
#     if not GEMINI_API_KEY:
#         st.error("❌ Add GEMINI_API_KEY to .env file")
#         return
    
#     if not initialize_gemini():
#         st.error("❌ Failed to initialize Gemini")
#         return
    
#     # Tabs for different sections
#     tab1, tab2, tab3, tab4 = st.tabs([
#         "🎨 AI Gallery", 
#         "💬 Smart Query", 
#         "⚡ Quick Insights",
#         "🖼️ Generated Gallery"
#     ])
    
#     # ============ TAB 1: AI GALLERY (SHOWCASE) ============
#     with tab1:
#         st.markdown("## 🎨 AI-Generated IPL Visualizations")
#         st.markdown("*Powered by Google Gemini 2.0 Flash*")
        
#         st.info("💡 **Portfolio Showcase**: These professional visualizations were generated entirely by AI from IPL match data")
        
#         # Placeholder for 4 hero images
#         col1, col2 = st.columns(2)
        
#         with col1:
#             st.markdown("### 📊 Team Performance Comparison")
#             # Placeholder image 1
#             try:
#                 st.image("generated_images/showcase_team_comparison.png", 
#                         caption="AI-Generated: Top Teams Win Rate Analysis",
#                         use_container_width=True)
#             except:
#                 st.info("🖼️ **Placeholder**: Team performance bar chart with custom styling\n\n*Add image: `showcase_team_comparison.png`*")
            
#             st.markdown("**Features**: Custom color gradients, team logos, professional typography")
            
#         with col2:
#             st.markdown("### 📈 Season Trends Analysis")
#             # Placeholder image 2
#             try:
#                 st.image("generated_images/showcase_season_trends.png",
#                         caption="AI-Generated: Multi-Season Performance Trends",
#                         use_container_width=True)
#             except:
#                 st.info("🖼️ **Placeholder**: Line chart showing season-wise trends\n\n*Add image: `showcase_season_trends.png`*")
            
#             st.markdown("**Features**: Smooth curves, data annotations, IPL branding")
        
#         col1, col2 = st.columns(2)
        
#         with col1:
#             st.markdown("### 🌟 Player Statistics Radar")
#             # Placeholder image 3
#             try:
#                 st.image("generated_images/showcase_player_radar.png",
#                         caption="AI-Generated: Player Multi-Dimensional Comparison",
#                         use_container_width=True)
#             except:
#                 st.info("🖼️ **Placeholder**: Radar chart for player comparison\n\n*Add image: `showcase_player_radar.png`*")
            
#             st.markdown("**Features**: Multi-axis visualization, color-coded metrics, legends")
        
#         with col2:
#             st.markdown("### 🏟️ Venue Performance Heatmap")
#             # Placeholder image 4
#             try:
#                 st.image("generated_images/showcase_venue_heatmap.png",
#                         caption="AI-Generated: Win Rate by Venue Analysis",
#                         use_container_width=True)
#             except:
#                 st.info("🖼️ **Placeholder**: Heatmap showing venue statistics\n\n*Add image: `showcase_venue_heatmap.png`*")
            
#             st.markdown("**Features**: Geographic insights, gradient coloring, data-driven design")
    
#     # ============ TAB 2: SMART QUERY ============
#     with tab2:
#         show_smart_query_interface()
    
#     # ============ TAB 3: QUICK INSIGHTS ============
#     with tab3:
#         show_quick_insights_interface()
    
#     # ============ TAB 4: GENERATED GALLERY ============
#     with tab4:
#         show_generated_gallery()

# def show_smart_query_interface():
#     """Smart query interface with data download and AI generation"""
#     st.markdown("## Smart Query Interface")
#     st.markdown("*Ask questions in natural language to get instant AI visualizations*")
    
#     # Example queries - clickable
#     with st.expander("Example Queries (Click to use)"):
#         examples = [
#             "Show top 5 teams by win percentage",
#             "Compare Mumbai Indians vs Chennai Super Kings",
#             "Which players scored most runs in 2024?",
#             "Show toss impact statistics",
#             "Top 10 run scorers overall"
#         ]
        
#         for idx, ex in enumerate(examples):
#             if st.button(f"{ex}", key=f"smart_example_btn_{idx}", use_container_width=True):
#                 st.session_state.smart_query_text = ex
#                 st.rerun()
    
#     # Query input - use session state for auto-fill
#     query = st.text_area("Ask your question:", 
#                         value=st.session_state.get('smart_query_text', ''),
#                         placeholder="Example: Show me the top run scorers in IPL 2024",
#                         height=100,
#                         key="smart_query_input")
    
#     col1, col2, col3 = st.columns([1, 1, 2])
#     with col1:
#         if st.button("Get Data", type="primary", use_container_width=True, key="smart_query_data_btn"):
#             if query:
#                 st.session_state.smart_query = query
#                 st.session_state.smart_query_executed = True
#             else:
#                 st.warning("Please enter a question")
    
#     with col2:
#         if st.button("Direct AI Image", type="secondary", use_container_width=True, key="smart_query_direct_ai_btn"):
#             if query:
#                 st.session_state.smart_query = query
#                 st.session_state.direct_ai_mode = True
#             else:
#                 st.warning("Please enter a question")
    
#     # Execute query for data
#     if st.session_state.get('smart_query_executed') and st.session_state.get('smart_query'):
#         with st.spinner("Fetching data..."):
#             try:
#                 sql = generate_sql_from_question(st.session_state.smart_query)
#                 with get_database_connection() as conn:
#                     data = pd.read_sql_query(sql, conn)
                
#                 if len(data) > 0:
#                     st.success(f"Found {len(data)} rows")
                    
#                     # Show data
#                     formatted_data = format_columns(data)
#                     st.dataframe(formatted_data, use_container_width=True, hide_index=True, height=300)
                    
#                     # Download CSV
#                     csv = data.to_csv(index=False)
#                     st.download_button("Download CSV", csv, "query_results.csv", "text/csv",
#                                      use_container_width=False, key="smart_csv_dl")
                    
#                     # Store data
#                     st.session_state.smart_query_data = data
#                     st.session_state.smart_query_question = st.session_state.smart_query
                    
#                     # Optional visualization section
#                     st.markdown("---")
#                     st.markdown("### Optional: Create Visualization")
                    
#                     col1, col2 = st.columns(2)
#                     with col1:
#                         chart_types = get_chart_type_options(data)
#                         chart_type = st.selectbox("Chart Type", [o[0] for o in chart_types],
#                                                  format_func=lambda x: next(o[1] for o in chart_types if o[0] == x),
#                                                  key="smart_chart_type")
#                     with col2:
#                         title = st.text_input("Chart Title", value=st.session_state.smart_query, key="smart_chart_title")
                    
#                     col1, col2, col3 = st.columns(3)
                    
#                     with col1:
#                         if st.button("Plotly Chart", use_container_width=True, key="smart_plotly_btn"):
#                             fig = generate_plotly_chart(data, chart_type, title)
#                             if fig:
#                                 st.session_state.smart_plotly_fig = fig
#                                 st.session_state.smart_chart_title = title
#                                 st.plotly_chart(fig, use_container_width=True, key="smart_plotly_preview")
                    
#                     with col2:
#                         if st.button("AI Image", type="primary", use_container_width=True, key="smart_ai_btn"):
#                             with st.spinner("Creating AI visualization... (15-30 sec)"):
#                                 try:
#                                     data_ctx = prepare_data_context(data, max_rows=10)
                                    
#                                     prompt = f"""Generate a professional IPL cricket data visualization image.

# Question: {st.session_state.smart_query}
# Title: {title}
# Chart Type: {chart_type}

# Data:
# {data_ctx}

# Create a complete visualization with:
# - High resolution (1920x1080)
# - IPL purple/violet color scheme (#667eea, #764ba2)
# - Clear, readable labels
# - Professional typography
# - All data accurately displayed
# - Modern, clean design
# """
                                    
#                                     # Use image generation model
#                                     model = genai.GenerativeModel('gemini-exp-1206')
#                                     response = model.generate_content(
#                                         prompt,
#                                         generation_config=genai.GenerationConfig(
#                                             temperature=0.4,
#                                             max_output_tokens=8192,
#                                         ),
#                                         request_options={'timeout': 60}
#                                     )
                                    
#                                     if response and hasattr(response, 'parts'):
#                                         for part in response.parts:
#                                             if hasattr(part, 'inline_data') and part.inline_data:
#                                                 ai_img = part.inline_data.data
#                                                 watermarked = add_watermark_to_image(ai_img, "@rkjat65")
#                                                 saved = save_image_to_folder(watermarked, "smart_query")
                                                
#                                                 st.session_state.smart_ai_image = watermarked
#                                                 st.success(f"AI image generated! Saved: {saved}")
#                                                 break
#                                         else:
#                                             st.error("No image generated")
#                                     else:
#                                         st.error("Generation failed")
#                                 except Exception as e:
#                                     st.error(f"Error: {str(e)[:100]}")
                    
#                     with col3:
#                         if 'smart_ai_image' in st.session_state:
#                             st.download_button(
#                                 "Download AI",
#                                 st.session_state.smart_ai_image,
#                                 "ai_visualization.png",
#                                 "image/png",
#                                 use_container_width=True,
#                                 key="smart_ai_dl"
#                             )
                    
#                     # Show AI image if generated (NO TABLE)
#                     if 'smart_ai_image' in st.session_state:
#                         st.markdown("---")
#                         st.markdown("### AI Generated Visualization")
#                         st.image(st.session_state.smart_ai_image, use_container_width=True)
                    
#                     # Show Plotly if generated
#                     if 'smart_plotly_fig' in st.session_state:
#                         st.markdown("---")
#                         st.markdown("### Plotly Chart")
#                         st.plotly_chart(st.session_state.smart_plotly_fig, use_container_width=True, key="smart_plotly_display")
                
#                 else:
#                     st.warning("No results found. Try rephrasing your question.")
                    
#             except Exception as e:
#                 st.error(f"Query failed: {str(e)[:100]}")
        
#         # Reset flag
#         st.session_state.smart_query_executed = False
    
#     # Direct AI mode (no data table unless data requested)
#     if st.session_state.get('direct_ai_mode') and st.session_state.get('smart_query'):
#         with st.spinner("Generating AI visualization directly... (15-30 sec)"):
#             try:
#                 sql = generate_sql_from_question(st.session_state.smart_query)
#                 with get_database_connection() as conn:
#                     data = pd.read_sql_query(sql, conn)
                
#                 if len(data) > 0:
#                     data_ctx = prepare_data_context(data, max_rows=15)
                    
#                     prompt = f"""Generate a professional IPL cricket data visualization image.

# Question: {st.session_state.smart_query}

# Data:
# {data_ctx}

# Create a complete visualization with:
# - High resolution (1920x1080)
# - IPL purple/violet color scheme (#667eea, #764ba2)
# - Clear, readable labels and title
# - Professional typography
# - Choose the best chart type for this data
# - All data accurately displayed
# - Modern, clean design
# """
                    
#                     # Use image generation model
#                     model = genai.GenerativeModel('gemini-exp-1206')
#                     response = model.generate_content(
#                         prompt,
#                         generation_config=genai.GenerationConfig(
#                             temperature=0.4,
#                             max_output_tokens=8192,
#                         ),
#                         request_options={'timeout': 60}
#                     )
                    
#                     if response and hasattr(response, 'parts'):
#                         for part in response.parts:
#                             if hasattr(part, 'inline_data') and part.inline_data:
#                                 ai_img = part.inline_data.data
#                                 watermarked = add_watermark_to_image(ai_img, "@rkjat65")
#                                 saved = save_image_to_folder(watermarked, "direct_ai")
                                
#                                 st.success(f"AI visualization created! Saved: {saved}")
#                                 st.image(watermarked, use_container_width=True)
#                                 st.download_button(
#                                     "Download AI Image",
#                                     watermarked,
#                                     "ai_visualization.png",
#                                     "image/png",
#                                     use_container_width=False,
#                                     key="direct_ai_dl"
#                                 )
#                                 break
#                         else:
#                             st.error("No image generated")
#                     else:
#                         st.error("Generation failed")
#                 else:
#                     st.warning("No data found for this query")
#             except Exception as e:
#                 st.error(f"Error: {str(e)[:100]}")
        
#         # Reset flag
#         st.session_state.direct_ai_mode = False
#     """Smart query interface with data download and AI generation"""
#     st.markdown("## 💬 Smart Query Interface")
#     st.markdown("*Ask questions in natural language → Get instant AI visualizations*")
    
#     # Example queries - clickable
#     with st.expander("💡 Example Queries (Click to use)"):
#         examples = [
#             "Show top 5 teams by win percentage",
#             "Compare Mumbai Indians vs Chennai Super Kings",
#             "Which players scored most runs in 2024?",
#             "Show toss impact statistics",
#             "Top 10 run scorers overall"
#         ]
        
#         for idx, ex in enumerate(examples):
#             if st.button(f"{ex}", key=f"old_example_{idx}", use_container_width=True):
#                 st.session_state.smart_query_text = ex
#                 st.rerun()
    
#     # Query input - use session state for auto-fill
#     query = st.text_area("Ask your question:", 
#                         value=st.session_state.get('smart_query_text', ''),
#                         placeholder="Example: Show me the top run scorers in IPL 2024",
#                         height=100,
#                         key="smart_query_input")
    
#     col1, col2, col3 = st.columns([1, 1, 2])
#     with col1:
#         if st.button("📊 Get Data", type="primary", use_container_width=True, key="smart_query_data_btn"):
#             if query:
#                 st.session_state.smart_query = query
#                 st.session_state.smart_query_executed = True
#             else:
#                 st.warning("⚠️ Please enter a question")
    
#     with col2:
#         if st.button("🤖 Direct AI Image", type="secondary", use_container_width=True, key="smart_query_direct_ai_btn"):
#             if query:
#                 st.session_state.smart_query = query
#                 st.session_state.direct_ai_mode = True
#             else:
#                 st.warning("⚠️ Please enter a question")
    
#     # Execute query for data
#     if st.session_state.get('smart_query_executed') and st.session_state.get('smart_query'):
#         with st.spinner("🤔 Fetching data..."):
#             try:
#                 sql = generate_sql_from_question(st.session_state.smart_query)
#                 with get_database_connection() as conn:
#                     data = pd.read_sql_query(sql, conn)
                
#                 if len(data) > 0:
#                     st.success(f"✅ Found {len(data)} rows")
                    
#                     # Show data
#                     formatted_data = format_columns(data)
#                     st.dataframe(formatted_data, use_container_width=True, hide_index=True, height=300)
                    
#                     # Download CSV
#                     csv = data.to_csv(index=False)
#                     st.download_button("📥 Download CSV", csv, "query_results.csv", "text/csv",
#                                      use_container_width=False, key="smart_csv_dl")
                    
#                     # Store data
#                     st.session_state.smart_query_data = data
#                     st.session_state.smart_query_question = st.session_state.smart_query
                    
#                     # Optional visualization section
#                     st.markdown("---")
#                     st.markdown("### 📊 Optional: Create Visualization")
                    
#                     col1, col2 = st.columns(2)
#                     with col1:
#                         chart_types = get_chart_type_options(data)
#                         chart_type = st.selectbox("Chart Type", [o[0] for o in chart_types],
#                                                  format_func=lambda x: next(o[1] for o in chart_types if o[0] == x),
#                                                  key="smart_chart_type")
#                     with col2:
#                         title = st.text_input("Chart Title", value=st.session_state.smart_query, key="smart_chart_title")
                    
#                     col1, col2, col3 = st.columns(3)
                    
#                     with col1:
#                         if st.button("📊 Plotly Chart", use_container_width=True, key="smart_plotly_btn"):
#                             fig = generate_plotly_chart(data, chart_type, title)
#                             if fig:
#                                 st.session_state.smart_plotly_fig = fig
#                                 st.session_state.smart_chart_title = title
#                                 st.plotly_chart(fig, use_container_width=True, key="smart_plotly_preview")
                    
#                     with col2:
#                         if st.button("🤖 AI Image", type="primary", use_container_width=True, key="smart_ai_btn"):
#                             with st.spinner("🎨 Creating AI visualization... (10-20 sec)"):
#                                 try:
#                                     data_ctx = prepare_data_context(data, max_rows=10)
                                    
#                                     prompt = f"""Generate a professional IPL cricket data visualization.

# Question: {st.session_state.smart_query}
# Title: {title}
# Chart Type: {chart_type}

# Data:
# {data_ctx}

# Requirements:
# - High resolution (1920x1080)
# - IPL purple/violet color scheme (#667eea, #764ba2)
# - Clear, readable labels
# - Professional typography
# - Data accuracy is critical
# - Modern, clean design
# """
                                    
#                                     model = genai.GenerativeModel('gemini-2.0-flash-exp')
#                                     response = model.generate_content(prompt)
                                    
#                                     if response and hasattr(response, 'parts'):
#                                         for part in response.parts:
#                                             if hasattr(part, 'inline_data') and part.inline_data:
#                                                 ai_img = part.inline_data.data
#                                                 watermarked = add_watermark_to_image(ai_img, "@rkjat65")
#                                                 saved = save_image_to_folder(watermarked, "smart_query")
                                                
#                                                 st.session_state.smart_ai_image = watermarked
#                                                 st.success(f"✅ AI image generated! Saved: {saved}")
#                                                 break
#                                         else:
#                                             st.error("No image generated")
#                                     else:
#                                         st.error("Generation failed")
#                                 except Exception as e:
#                                     st.error(f"❌ {e}")
                    
#                     with col3:
#                         if 'smart_ai_image' in st.session_state:
#                             st.download_button(
#                                 "📥 Download AI",
#                                 st.session_state.smart_ai_image,
#                                 "ai_visualization.png",
#                                 "image/png",
#                                 use_container_width=True,
#                                 key="smart_ai_dl"
#                             )
                    
#                     # Show AI image if generated
#                     if 'smart_ai_image' in st.session_state:
#                         st.markdown("---")
#                         st.markdown("### 🤖 AI Generated Visualization")
#                         st.image(st.session_state.smart_ai_image, use_container_width=True)
                    
#                     # Show Plotly if generated
#                     if 'smart_plotly_fig' in st.session_state:
#                         st.markdown("---")
#                         st.markdown("### 📊 Plotly Chart")
#                         st.plotly_chart(st.session_state.smart_plotly_fig, use_container_width=True, key="smart_plotly_display")
                
#                 else:
#                     st.warning("No results found. Try rephrasing your question.")
                    
#             except Exception as e:
#                 st.error(f"❌ Query failed: {e}")
        
#         # Reset flag
#         st.session_state.smart_query_executed = False
    
#     # Direct AI mode (no data table)
#     if st.session_state.get('direct_ai_mode') and st.session_state.get('smart_query'):
#         with st.spinner("🎨 Generating AI visualization directly... (15-25 sec)"):
#             try:
#                 sql = generate_sql_from_question(st.session_state.smart_query)
#                 with get_database_connection() as conn:
#                     data = pd.read_sql_query(sql, conn)
                
#                 if len(data) > 0:
#                     data_ctx = prepare_data_context(data, max_rows=15)
                    
#                     prompt = f"""Generate a professional IPL cricket data visualization.

# Question: {st.session_state.smart_query}

# Data:
# {data_ctx}

# Requirements:
# - High resolution (1920x1080)
# - IPL purple/violet color scheme (#667eea, #764ba2)
# - Clear, readable labels and title
# - Professional typography
# - Data accuracy is critical
# - Choose the best chart type for this data
# - Modern, clean design
# """
                    
#                     model = genai.GenerativeModel('gemini-2.0-flash-exp')
#                     response = model.generate_content(prompt)
                    
#                     if response and hasattr(response, 'parts'):
#                         for part in response.parts:
#                             if hasattr(part, 'inline_data') and part.inline_data:
#                                 ai_img = part.inline_data.data
#                                 watermarked = add_watermark_to_image(ai_img, "@rkjat65")
#                                 saved = save_image_to_folder(watermarked, "direct_ai")
                                
#                                 st.success(f"✅ AI visualization created! Saved: {saved}")
#                                 st.image(watermarked, use_container_width=True)
#                                 st.download_button(
#                                     "📥 Download AI Image",
#                                     watermarked,
#                                     "ai_visualization.png",
#                                     "image/png",
#                                     use_container_width=False,
#                                     key="direct_ai_dl"
#                                 )
#                                 break
#                         else:
#                             st.error("No image generated")
#                     else:
#                         st.error("Generation failed")
#                 else:
#                     st.warning("No data found for this query")
#             except Exception as e:
#                 st.error(f"❌ {e}")
        
#         # Reset flag
#         st.session_state.direct_ai_mode = False

# def show_quick_insights_interface():
#     """Pre-built queries with one-click AI generation"""
#     st.markdown("## Quick Insights")
#     st.markdown("*One-click AI visualizations for common queries*")
    
#     with get_database_connection() as conn:
#         # Check if deliveries table has data
#         cursor = conn.cursor()
#         cursor.execute("SELECT COUNT(*) FROM deliveries")
#         has_deliveries = cursor.fetchone()[0] > 0

#         insights = {
#         "Top 5 Teams": {
#             "query": """
#                 SELECT team_name as team, COUNT(*) as matches,
#                        SUM(CASE WHEN match_winner_name = team_name THEN 1 ELSE 0 END) as wins,
#                        ROUND(100.0 * SUM(CASE WHEN match_winner_name = team_name THEN 1 ELSE 0 END) / COUNT(*), 1) as win_percentage
#                 FROM teams t
#                 LEFT JOIN matches m ON t.team_name = m.team1_name OR t.team_name = m.team2_name
#                 WHERE t.is_active = 1
#                 GROUP BY t.team_name
#                 ORDER BY win_percentage DESC
#                 LIMIT 5
#             """,
#             "chart": "bar",
#             "title": "Top 5 Teams by Win Percentage"
#         },
#         "Season Trends": {
#             "query": """
#                 SELECT season, COUNT(*) as matches,
#                        COUNT(DISTINCT venue) as venues
#                 FROM matches
#                 GROUP BY season
#                 ORDER BY season
#             """,
#             "chart": "line",
#             "title": "IPL Growth Over Seasons"
#         },
#         "Top Venues": {
#             "query": """
#                 SELECT venue, COUNT(*) as matches
#                 FROM matches
#                 WHERE venue IS NOT NULL
#                 GROUP BY venue
#                 ORDER BY matches DESC
#                 LIMIT 10
#             """,
#             "chart": "bar",
#             "title": "Top 10 IPL Venues"
#         },
#         "Toss Impact": {
#             "query": """
#                 SELECT toss_decision as decision,
#                        COUNT(*) as total_matches,
#                        SUM(CASE WHEN toss_winner_id = match_winner_id THEN 1 ELSE 0 END) as wins_after_toss,
#                        ROUND(100.0 * SUM(CASE WHEN toss_winner_id = match_winner_id THEN 1 ELSE 0 END) / COUNT(*), 1) as win_percentage
#                 FROM matches
#                 WHERE toss_decision IS NOT NULL
#                 GROUP BY toss_decision
#             """,
#             "chart": "pie",
#             "title": "Toss Decision Impact on Wins"
#         }
#     }
    
#     # Add player stats if deliveries data exists
#     if has_deliveries:
#         insights["Top Scorers"] = {
#             "query": """
#                 SELECT batter as player, SUM(batter_runs) as total_runs,
#                        COUNT(DISTINCT match_id) as matches
#                 FROM deliveries
#                 WHERE batter IS NOT NULL
#                 GROUP BY batter
#                 ORDER BY total_runs DESC
#                 LIMIT 10
#             """,
#             "chart": "bar",
#             "title": "Top 10 Run Scorers (All-Time)"
#         }
        
#         insights["Top Bowlers"] = {
#             "query": """
#                 SELECT bowler as player, SUM(is_wicket) as total_wickets,
#                        COUNT(DISTINCT match_id) as matches
#                 FROM deliveries
#                 WHERE bowler IS NOT NULL
#                 GROUP BY bowler
#                 ORDER BY total_wickets DESC
#                 LIMIT 10
#             """,
#             "chart": "bar",
#             "title": "Top 10 Wicket Takers (All-Time)"
#         }
    
#     # Display insights in grid
#     cols_per_row = 3
#     insight_items = list(insights.items())
    
#     for row_start in range(0, len(insight_items), cols_per_row):
#         cols = st.columns(cols_per_row)
        
#         for col_idx, insight_idx in enumerate(range(row_start, min(row_start + cols_per_row, len(insight_items)))):
#             if insight_idx >= len(insight_items):
#                 break
                
#             name, config = insight_items[insight_idx]
            
#             with cols[col_idx]:
#                 st.markdown(f"### {name}")
#                 st.markdown(f"*{config['title']}*")
                
#                 # Generate button
#                 if st.button(f"Generate", key=f"qi_gen_{insight_idx}", use_container_width=True):
#                     st.session_state[f'qi_generating_{insight_idx}'] = True
                
#                 # Check if this insight is being generated
#                 if st.session_state.get(f'qi_generating_{insight_idx}', False):
#                     with st.spinner("Generating AI visualization..."):
#                         try:
#                             # Fetch data
#                             data = pd.read_sql_query(config['query'], conn)
                            
#                             if len(data) > 0:
#                                 # Don't show data table for image generation (only show the image)
                                
#                                 # Generate AI image directly using IMAGE model
#                                 data_ctx = prepare_data_context(data, max_rows=15)
                                
#                                 prompt = f"""Generate a professional IPL cricket data visualization image.

# Title: {config['title']}
# Chart Type: {config['chart']}

# Data:
# {data_ctx}

# Create a complete visualization with:
# - High resolution (1920x1080)
# - IPL purple/violet color scheme (#667eea, #764ba2)
# - Clear, readable labels and values
# - Professional typography
# - Chart type: {config['chart']}
# - All data points visible
# - Modern, clean design
# - Title prominently displayed
# """
                                
#                                 # Use image generation model
#                                 model = genai.GenerativeModel('gemini-exp-1206')
#                                 response = model.generate_content(
#                                     prompt,
#                                     generation_config=genai.GenerationConfig(
#                                         temperature=0.4,
#                                         top_p=0.95,
#                                         max_output_tokens=8192,
#                                     ),
#                                     request_options={'timeout': 60}
#                                 )
                                
#                                 if response and hasattr(response, 'parts'):
#                                     for part in response.parts:
#                                         if hasattr(part, 'inline_data') and part.inline_data:
#                                             ai_img = part.inline_data.data
#                                             watermarked = add_watermark_to_image(ai_img, "@rkjat65")
#                                             saved = save_image_to_folder(watermarked, f"quick_insight")
                                            
#                                             # Store in session state
#                                             st.session_state[f'qi_image_{insight_idx}'] = watermarked
#                                             st.session_state[f'qi_saved_{insight_idx}'] = saved
                                            
#                                             st.success(f"Generated! Saved: {saved}")
#                                             break
#                                     else:
#                                         st.error("No image generated. Please try again.")
#                                 else:
#                                     st.error("Generation failed. Please try again.")
#                             else:
#                                 st.warning("No data found")
                                
#                         except Exception as e:
#                             st.error(f"Error: {str(e)[:100]}")
#                             # Show troubleshooting
#                             if "timeout" in str(e).lower() or "deadline" in str(e).lower():
#                                 st.info("Generation timed out. Try a simpler query or try again.")
                        
#                         # Reset generating flag
#                         st.session_state[f'qi_generating_{insight_idx}'] = False
                
#                 # Show generated image if exists
#                 if st.session_state.get(f'qi_image_{insight_idx}'):
#                     st.image(st.session_state[f'qi_image_{insight_idx}'], use_container_width=True)
#                     st.download_button(
#                         "Download",
#                         st.session_state[f'qi_image_{insight_idx}'],
#                         f"ai_{name.replace(' ', '_').lower()}.png",
#                         "image/png",
#                         use_container_width=True,
#                         key=f"qi_dl_{insight_idx}"
#                     )
#     """Pre-built queries with one-click AI generation"""
#     st.markdown("## ⚡ Quick Insights")
#     st.markdown("*One-click AI visualizations for common queries*")
    
#     with get_database_connection() as conn:
#         # Check if deliveries table has data
#         cursor = conn.cursor()
#         cursor.execute("SELECT COUNT(*) FROM deliveries")
#         has_deliveries = cursor.fetchone()[0] > 0

#         insights = {
#         "🏆 Top 5 Teams": {
#             "query": """
#                 SELECT team_name as team, COUNT(*) as matches,
#                        SUM(CASE WHEN match_winner_name = team_name THEN 1 ELSE 0 END) as wins,
#                        ROUND(100.0 * SUM(CASE WHEN match_winner_name = team_name THEN 1 ELSE 0 END) / COUNT(*), 1) as win_percentage
#                 FROM teams t
#                 LEFT JOIN matches m ON t.team_name = m.team1_name OR t.team_name = m.team2_name
#                 WHERE t.is_active = 1
#                 GROUP BY t.team_name
#                 ORDER BY win_percentage DESC
#                 LIMIT 5
#             """,
#             "chart": "bar",
#             "title": "Top 5 Teams by Win Percentage"
#         },
#         "📈 Season Trends": {
#             "query": """
#                 SELECT season, COUNT(*) as matches,
#                        COUNT(DISTINCT venue) as venues
#                 FROM matches
#                 GROUP BY season
#                 ORDER BY season
#             """,
#             "chart": "line",
#             "title": "IPL Growth Over Seasons"
#         },
#         "🏟️ Top Venues": {
#             "query": """
#                 SELECT venue, COUNT(*) as matches
#                 FROM matches
#                 WHERE venue IS NOT NULL
#                 GROUP BY venue
#                 ORDER BY matches DESC
#                 LIMIT 10
#             """,
#             "chart": "bar",
#             "title": "Top 10 IPL Venues"
#         },
#         "⚖️ Toss Impact": {
#             "query": """
#                 SELECT toss_decision as decision,
#                        COUNT(*) as total_matches,
#                        SUM(CASE WHEN toss_winner_id = match_winner_id THEN 1 ELSE 0 END) as wins_after_toss,
#                        ROUND(100.0 * SUM(CASE WHEN toss_winner_id = match_winner_id THEN 1 ELSE 0 END) / COUNT(*), 1) as win_percentage
#                 FROM matches
#                 WHERE toss_decision IS NOT NULL
#                 GROUP BY toss_decision
#             """,
#             "chart": "pie",
#             "title": "Toss Decision Impact on Wins"
#         }
#     }
    
#     # Add player stats if deliveries data exists
#     if has_deliveries:
#         insights["🌟 Top Scorers"] = {
#             "query": """
#                 SELECT batter as player, SUM(batter_runs) as total_runs,
#                        COUNT(DISTINCT match_id) as matches
#                 FROM deliveries
#                 WHERE batter IS NOT NULL
#                 GROUP BY batter
#                 ORDER BY total_runs DESC
#                 LIMIT 10
#             """,
#             "chart": "bar",
#             "title": "Top 10 Run Scorers (All-Time)"
#         }
        
#         insights["🎯 Top Bowlers"] = {
#             "query": """
#                 SELECT bowler as player, SUM(is_wicket) as total_wickets,
#                        COUNT(DISTINCT match_id) as matches
#                 FROM deliveries
#                 WHERE bowler IS NOT NULL
#                 GROUP BY bowler
#                 ORDER BY total_wickets DESC
#                 LIMIT 10
#             """,
#             "chart": "bar",
#             "title": "Top 10 Wicket Takers (All-Time)"
#         }
    
#     # Display insights in grid
#     cols_per_row = 3
#     insight_items = list(insights.items())
    
#     for row_start in range(0, len(insight_items), cols_per_row):
#         cols = st.columns(cols_per_row)
        
#         for col_idx, insight_idx in enumerate(range(row_start, min(row_start + cols_per_row, len(insight_items)))):
#             if insight_idx >= len(insight_items):
#                 break
                
#             name, config = insight_items[insight_idx]
            
#             with cols[col_idx]:
#                 st.markdown(f"### {name}")
#                 st.markdown(f"*{config['title']}*")
                
#                 # Generate button
#                 if st.button(f"📊 Generate", key=f"qi_gen_{insight_idx}", use_container_width=True):
#                     st.session_state[f'qi_generating_{insight_idx}'] = True
                
#                 # Check if this insight is being generated
#                 if st.session_state.get(f'qi_generating_{insight_idx}', False):
#                     with st.spinner("🎨 Generating AI visualization..."):
#                         try:
#                             # Fetch data
#                             data = pd.read_sql_query(config['query'], conn)
                            
#                             if len(data) > 0:
#                                 # Format and show data
#                                 formatted_data = format_columns(data)
#                                 st.dataframe(formatted_data, use_container_width=True, hide_index=True, height=200)
                                
#                                 # Generate AI image directly
#                                 data_ctx = prepare_data_context(data, max_rows=15)
                                
#                                 prompt = f"""Generate a professional IPL cricket data visualization.

# Title: {config['title']}
# Chart Type: {config['chart']}

# Data:
# {data_ctx}

# Requirements:
# - High resolution (1920x1080)
# - IPL purple/violet color scheme (#667eea, #764ba2)
# - Clear, readable labels
# - Professional typography
# - Data accuracy is critical
# - Modern, clean design
# - Chart type: {config['chart']}
# """
                                
#                                 model = genai.GenerativeModel('gemini-2.0-flash-exp')
#                                 response = model.generate_content(prompt)
                                
#                                 if response and hasattr(response, 'parts'):
#                                     for part in response.parts:
#                                         if hasattr(part, 'inline_data') and part.inline_data:
#                                             ai_img = part.inline_data.data
#                                             watermarked = add_watermark_to_image(ai_img, "@rkjat65")
#                                             saved = save_image_to_folder(watermarked, f"quick_insight")
                                            
#                                             # Store in session state
#                                             st.session_state[f'qi_image_{insight_idx}'] = watermarked
#                                             st.session_state[f'qi_saved_{insight_idx}'] = saved
                                            
#                                             st.success(f"✅ Generated! Saved: {saved}")
#                                             break
#                                     else:
#                                         st.error("❌ No image generated")
#                                 else:
#                                     st.error("❌ Generation failed")
#                             else:
#                                 st.warning("⚠️ No data found")
                                
#                         except Exception as e:
#                             st.error(f"❌ Error: {e}")
                        
#                         # Reset generating flag
#                         st.session_state[f'qi_generating_{insight_idx}'] = False
                
#                 # Show generated image if exists
#                 if st.session_state.get(f'qi_image_{insight_idx}'):
#                     st.image(st.session_state[f'qi_image_{insight_idx}'], use_container_width=True)
#                     st.download_button(
#                         "📥 Download",
#                         st.session_state[f'qi_image_{insight_idx}'],
#                         f"ai_{name.replace(' ', '_').lower()}.png",
#                         "image/png",
#                         use_container_width=True,
#                         key=f"qi_dl_{insight_idx}"
#                     )

# def show_generated_gallery():
#     """Show history of generated images"""
#     st.markdown("## 🖼️ Generated Images Gallery")
#     st.markdown("*Your AI-generated visualizations*")
    
#     # Check for generated images
#     if GENERATED_IMAGES_DIR.exists():
#         images = list(GENERATED_IMAGES_DIR.glob("*.png"))
        
#         if images:
#             st.info(f"📊 Found {len(images)} generated images")
            
#             # Sort by modification time (newest first)
#             images = sorted(images, key=lambda x: x.stat().st_mtime, reverse=True)
            
#             # Display in grid
#             cols = st.columns(3)
#             for idx, img_path in enumerate(images):
#                 with cols[idx % 3]:
#                     st.image(str(img_path), caption=img_path.name, use_container_width=True)
                    
#                     # Download button with unique key
#                     st.download_button(
#                         "📥 Download",
#                         open(img_path, 'rb').read(),
#                         img_path.name,
#                         "image/png",
#                         key=f"gallery_dl_{idx}_{img_path.stem}",  # Unique key
#                         use_container_width=True
#                     )
#         else:
#             st.info("💡 No images generated yet. Create some from the Smart Query or Quick Insights tabs!")
#     else:
#         st.info("💡 Start generating images to build your gallery!")
#         # Create directory if it doesn't exist
#         GENERATED_IMAGES_DIR.mkdir(exist_ok=True)

# # ==================== OLD AI ASSISTANT (KEEP FOR REFERENCE) ====================
#     """AI Assistant with enhanced image generation"""
#     st.title("🤖 IPL AI Assistant")
#     st.markdown("### Ask questions in natural language")
    
#     if not GEMINI_AVAILABLE:
#         st.error("❌ Install: `pip install google-generativeai python-dotenv`")
#         return
    
#     if not GEMINI_API_KEY:
#         st.error("❌ Add GEMINI_API_KEY to .env file")
#         return
    
#     if not initialize_gemini():
#         st.error("❌ Failed to initialize")
#         return
    
#     st.success("✅ AI Ready!")
    
#     tab1, tab2 = st.tabs(["💬 Ask Questions", "🎨 Generate Images"])
    
#     # TAB 1: Questions
#     with tab1:
#         st.markdown("### 💬 Chat with AI")
        
#         with st.expander("💡 Examples"):
#             st.markdown("""
#             - Which team won the most matches?
#             - Show Mumbai Indians' win rate
#             - Compare CSK and MI
#             """)
        
#         if st.button("🗑️ Clear", key="clear"):
#             st.session_state.messages = []
#             st.rerun()
        
#         for msg in st.session_state.messages:
#             with st.chat_message(msg["role"]):
#                 st.markdown(msg["content"])
#                 if "data" in msg and msg["data"] is not None:
#                     formatted_data = format_columns(msg["data"])  # Format column names
#                     st.dataframe(formatted_data, use_container_width=True, hide_index=True)
#                 if "sql" in msg:
#                     with st.expander("🔍 SQL"):
#                         st.code(msg["sql"], language="sql")
        
#         if prompt := st.chat_input("Ask about IPL..."):
#             st.session_state.messages.append({"role": "user", "content": prompt})
#             with st.chat_message("user"):
#                 st.markdown(prompt)
            
#             with st.chat_message("assistant"):
#                 with st.spinner("🤔 Thinking..."):
#                     sql = generate_sql_from_question(prompt)
                    
#                     # Store SQL but don't show to user (kept for debugging if needed)
#                     # with st.expander("🔍 SQL"):
#                     #     st.code(sql, language="sql")
                    
#                     try:
#                         with get_database_connection() as conn:
#                             data = pd.read_sql_query(sql, conn)
                        
#                         if len(data) > 0:
#                             formatted_data = format_columns(data)  # Format column names
#                             st.dataframe(formatted_data, use_container_width=True, hide_index=True)
#                             insight = generate_insight_from_data(prompt, data)
#                             st.info(f"💡 {insight}")
#                             st.session_state.messages.append({
#                                 "role": "assistant", "content": insight,
#                                 "data": data, "sql": sql
#                             })
#                         else:
#                             msg = "No results. Try rephrasing."
#                             st.warning(msg)
#                             st.session_state.messages.append({
#                                 "role": "assistant", "content": msg, "sql": sql
#                             })
#                     except Exception as e:
#                         error = f"❌ Error: {e}"
#                         st.error(error)
#                         st.session_state.messages.append({
#                             "role": "assistant", "content": error, "sql": sql
#                         })
    
#     # TAB 2: Image Generation (keeping same as original - no changes needed)
#     with tab2:
#         st.markdown("### 🎨 AI Image Generation")
#         st.info("📊 **Workflow:** Load Data → Plotly Chart → AI Version → Compare!")
        
#         if 'workflow_step' not in st.session_state:
#             st.session_state.workflow_step = 1
        
#         col1, col2, col3 = st.columns([2, 1, 2])
#         with col2:
#             if st.button("🔄 Reset", type="secondary", use_container_width=True):
#                 for key in ['workflow_step', 'plotly_fig', 'plotly_image', 'ai_image', 'data']:
#                     if key in st.session_state:
#                         del st.session_state[key]
#                 st.rerun()
        
#         st.markdown("---")
#         st.markdown("#### 📊 Step 1: Select Data")
        
#         data_mode = st.radio("Choose:", ["Quick Select", "Custom Query"], horizontal=True)
        
#         if data_mode == "Quick Select":
#             opts = load_database_data_options()
#             sel = st.selectbox("Select Data", list(opts.keys()))
            
#             if sel:
#                 st.info(f"📝 {opts[sel]['description']}")
                
#                 if st.button("📊 Load Data", key="load_q", type="primary"):
#                     try:
#                         with st.spinner("Loading..."):
#                             with get_database_connection() as conn:
#                                 data = pd.read_sql_query(opts[sel]['query'], conn)
#                             st.session_state['data'] = data
#                             st.session_state['data_name'] = sel
#                             st.session_state.workflow_step = 2
#                             st.success(f"✅ Loaded {len(data)} rows!")
#                             st.rerun()
#                     except Exception as e:
#                         st.error(f"❌ {e}")
#         else:
#             query = st.text_input("Describe data:", placeholder="Example: Show top 5 teams by wins")
            
#             if st.button("🔍 Get Data", key="load_c", type="primary") and query:
#                 with st.spinner("Generating..."):
#                     try:
#                         sql = generate_sql_from_question(query)
#                         st.code(sql, language="sql")

#                         with get_database_connection() as conn:
#                             data = pd.read_sql_query(sql, conn)

#                         st.session_state['data'] = data
#                         st.session_state['data_name'] = "Custom"
#                         st.session_state.workflow_step = 2
#                         st.success(f"✅ Got {len(data)} rows!")
#                         st.rerun()
#                     except Exception as e:
#                         st.error(f"❌ {e}")
        
#         if 'data' in st.session_state and st.session_state.workflow_step >= 2:
#             st.markdown("---")
#             st.markdown("#### ✅ Data Loaded")
#             formatted_data = format_columns(st.session_state['data'])  # Format column names
#             st.dataframe(formatted_data, use_container_width=True, hide_index=True)
            
#             st.markdown("---")
#             st.markdown("#### 📈 Step 2: Generate Plotly Chart")
            
#             col1, col2 = st.columns(2)
#             with col1:
#                 opts = get_chart_type_options(st.session_state['data'])
#                 chart_type = st.selectbox("Chart Type", [o[0] for o in opts],
#                                          format_func=lambda x: next(o[1] for o in opts if o[0] == x))
#             with col2:
#                 title = st.text_input("Title", value=f"IPL - {st.session_state.get('data_name', 'Data')}")
            
#             if st.button("📊 Generate Plotly", type="primary"):
#                 with st.spinner("Creating..."):
#                     try:
#                         fig = generate_plotly_chart(st.session_state['data'], chart_type, title)
#                         if fig:
#                             st.session_state.plotly_fig = fig
#                             st.session_state.chart_title = title
#                             st.session_state.plotly_image = plotly_to_image_bytes(fig)
#                             st.session_state.workflow_step = 3
#                             st.success("✅ Chart generated!")
#                             st.rerun()
#                     except Exception as e:
#                         st.error(f"❌ {e}")
        
#         if st.session_state.workflow_step >= 3 and 'plotly_fig' in st.session_state:
#             st.markdown("---")
#             st.markdown("#### 📊 Your Plotly Chart")
#             st.plotly_chart(st.session_state.plotly_fig, use_container_width=True, key="plotly_preview")
            
#             col1, col2, col3 = st.columns([1, 2, 1])
#             with col2:
#                 if 'plotly_image' in st.session_state and st.session_state.plotly_image is not None:
#                     st.download_button("📥 Download Plotly",
#                                       st.session_state.plotly_image,
#                                       "plotly.png", "image/png",
#                                       use_container_width=True, key="dl_plotly_preview")
#                 else:
#                     st.caption("💡 Chart displayed above (download available after AI generation)")
            
#             st.markdown("---")
#             st.markdown("#### 🤖 Step 3: Generate AI Version")
#             st.info("💡 Data auto-included. Describe visual style!")
            
#             prompt = st.text_area("Describe chart:",
#                                  placeholder="Example: Modern bar chart with team logos and gradients",
#                                  height=100)
            
#             col1, col2, col3 = st.columns([1, 2, 1])
#             with col2:
#                 if st.button("🎨 Generate AI", type="primary", use_container_width=True):
#                     if not prompt:
#                         st.warning("⚠️ Please describe your chart!")
#                     else:
#                         with st.spinner("🎨 Generating... (10-20 sec)"):
#                             try:
#                                 data_ctx = prepare_data_context(st.session_state['data'])
#                                 chart_info = get_chart_info(st.session_state.plotly_fig)
                                
#                                 full_prompt = f"""Generate professional IPL visualization.

# {prompt}

# Chart: {chart_info}
# Data: {data_ctx}

# Requirements: High-res (1920x1080), IPL purple/violet colors, clear labels, accurate data.
# Title: "{st.session_state.get('chart_title', 'IPL')}"
# """
                                
#                                 model = genai.GenerativeModel('gemini-2.0-flash-exp')
#                                 response = model.generate_content(full_prompt)
                                
#                                 if response and hasattr(response, 'parts'):
#                                     for part in response.parts:
#                                         if hasattr(part, 'inline_data') and part.inline_data:
#                                             ai_img = part.inline_data.data
#                                             watermarked = add_watermark_to_image(ai_img, "@rkjat65")
#                                             saved = save_image_to_folder(watermarked)
                                            
#                                             st.session_state.ai_image = watermarked
#                                             st.session_state.workflow_step = 4
#                                             st.success(f"✅ Generated! Saved: {saved}")
#                                             st.rerun()
#                                             break
#                                     else:
#                                         st.error("No image in response")
#                                 else:
#                                     st.error("Generation failed")
#                             except Exception as e:
#                                 st.error(f"❌ {e}")
        
#         if st.session_state.workflow_step >= 4 and 'ai_image' in st.session_state:
#             st.markdown("---")
#             st.markdown("#### 🔥 Comparison")
            
#             col1, col2 = st.columns(2)
            
#             with col1:
#                 st.markdown("##### 📊 Plotly")
#                 st.plotly_chart(st.session_state.plotly_fig, use_container_width=True, key="plotly_comparison")
                
#                 if 'plotly_image' not in st.session_state or st.session_state.plotly_image is None:
#                     with st.spinner("Converting chart..."):
#                         st.session_state.plotly_image = plotly_to_image_bytes(st.session_state.plotly_fig)
                
#                 if st.session_state.get('plotly_image') is not None:
#                     st.download_button("📥 Download Plotly",
#                                       st.session_state.plotly_image,
#                                       "plotly.png", "image/png",
#                                       use_container_width=True, key="dl_p")
#                 else:
#                     st.caption("💡 Chart visible above. Install kaleido for downloads: `pip install kaleido`")
            
#             with col2:
#                 st.markdown("##### 🤖 AI Generated")
#                 st.image(st.session_state.ai_image, use_container_width=True)
#                 st.download_button("📥 Download AI (with @rkjat65)",
#                                   st.session_state.ai_image,
#                                   "ai_generated.png", "image/png",
#                                   use_container_width=True, key="dl_a")

# if __name__ == "__main__":
#     main()
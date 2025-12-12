"""
IPL Cricket Analytics Dashboard
Main application entry point
"""

import streamlit as st
import sqlite3
import pandas as pd
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="IPL Analytics Dashboard",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Database connection
@st.cache_resource
def get_database_connection():
    """Get database connection"""
    db_path = Path("data/cricket_analytics.db")
    if not db_path.exists():
        st.error("❌ Database not found! Run `python scripts/create_database.py` first.")
        st.stop()
    return sqlite3.connect(db_path, check_same_thread=False)

# Load data functions
@st.cache_data(ttl=3600)
def load_teams():
    """Load teams data"""
    conn = get_database_connection()
    df = pd.read_sql_query("""
        SELECT team_id, team_name, short_name, is_active
        FROM teams
        ORDER BY team_name
    """, conn)
    return df

@st.cache_data(ttl=3600)
def load_matches():
    """Load all matches"""
    conn = get_database_connection()
    df = pd.read_sql_query("""
        SELECT *
        FROM matches
        ORDER BY match_date DESC
    """, conn)
    return df

@st.cache_data(ttl=3600)
def get_team_stats():
    """Get overall team statistics"""
    conn = get_database_connection()
    df = pd.read_sql_query("""
        WITH team_matches AS (
            SELECT team1_name as team FROM matches
            UNION ALL
            SELECT team2_name as team FROM matches
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
        LEFT JOIN (
            SELECT team, COUNT(*) as wins
            FROM team_wins
            GROUP BY team
        ) tw ON tm.team = tw.team
        WHERE tm.team IS NOT NULL
        GROUP BY tm.team
        ORDER BY win_percentage DESC
    """, conn)
    return df

# Custom CSS
def load_css():
    """Load custom CSS"""
    st.markdown("""
        <style>
        /* Main container */
        .main {
            padding: 0rem 1rem;
        }
        
        /* Metric cards */
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1.5rem;
            border-radius: 10px;
            color: white;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .metric-value {
            font-size: 2.5rem;
            font-weight: bold;
            margin: 0.5rem 0;
        }
        
        .metric-label {
            font-size: 1rem;
            opacity: 0.9;
        }
        
        /* Team card */
        .team-card {
            background: white;
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid #667eea;
            margin: 0.5rem 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        /* Sidebar */
        .css-1d391kg {
            padding: 2rem 1rem;
        }
        
        /* Headers */
        h1 {
            color: #667eea;
            font-weight: 700;
        }
        
        h2, h3 {
            color: #764ba2;
        }
        
        /* Dataframe styling */
        .dataframe {
            font-size: 0.9rem;
        }
        
        /* Button styling */
        .stButton>button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 0.5rem 2rem;
            border-radius: 5px;
            font-weight: 600;
        }
        
        .stButton>button:hover {
            opacity: 0.9;
        }
        </style>
    """, unsafe_allow_html=True)

# Main app
def main():
    """Main dashboard"""
    
    # Load CSS
    load_css()
    
    # Sidebar
    with st.sidebar:
        st.image("https://www.iplt20.com/assets/images/ipl-logo-new-old.png", width=200)
        st.title("🏏 IPL Analytics")
        st.markdown("---")
        
        # Navigation
        page = st.radio(
            "Navigate to:",
            ["🏠 Home", "🏏 Team Analysis", "🔍 Match Explorer", "📊 Season Insights", "⚔️ Head to Head"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Quick stats in sidebar
        st.subheader("Quick Stats")
        matches = load_matches()
        teams = load_teams()
        
        st.metric("Total Matches", f"{len(matches):,}")
        st.metric("Total Teams", len(teams))
        st.metric("Seasons", matches['season'].nunique())
        
        st.markdown("---")
        st.caption("📊 Data: 2008-2025 (excl. 2020)")
        st.caption("🔄 Last updated: December 2025")
    
    # Main content based on navigation
    if page == "🏠 Home":
        show_home_page()
    elif page == "🏏 Team Analysis":
        show_team_analysis()
    elif page == "🔍 Match Explorer":
        show_match_explorer()
    elif page == "📊 Season Insights":
        show_season_insights()
    elif page == "⚔️ Head to Head":
        show_head_to_head()

def show_home_page():
    """Home page with overview"""
    st.title("🏏 IPL Cricket Analytics Dashboard")
    st.markdown("### Welcome to the comprehensive IPL statistics and analysis platform!")
    
    # Key metrics
    st.markdown("## 📊 Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    matches = load_matches()
    teams = load_teams()
    team_stats = get_team_stats()
    
    with col1:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-label">Total Matches</div>
                <div class="metric-value">{:,}</div>
            </div>
        """.format(len(matches)), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-label">IPL Teams</div>
                <div class="metric-value">{}</div>
            </div>
        """.format(len(teams)), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-label">Seasons</div>
                <div class="metric-value">{}</div>
            </div>
        """.format(matches['season'].nunique()), unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-label">Venues</div>
                <div class="metric-value">{}</div>
            </div>
        """.format(matches['venue'].nunique()), unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Two columns for content
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("## 🏆 Top Teams by Win %")
        top_teams = team_stats.head(8)
        
        for idx, row in top_teams.iterrows():
            st.markdown(f"""
                <div class="team-card">
                    <strong>{row['team']}</strong><br>
                    Matches: {row['matches_played']} | Wins: {row['wins']} | Win%: {row['win_percentage']}%
                </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("## 📅 Recent Matches")
        recent = matches.head(8)[['match_date', 'team1_name', 'team2_name', 'match_winner_name', 'venue']]
        
        for idx, row in recent.iterrows():
            winner = row['match_winner_name'] if pd.notna(row['match_winner_name']) else 'No Result'
            st.markdown(f"""
                <div class="team-card">
                    <strong>{row['match_date']}</strong><br>
                    {row['team1_name']} vs {row['team2_name']}<br>
                    Winner: {winner}
                </div>
            """, unsafe_allow_html=True)
    
    # Features section
    st.markdown("---")
    st.markdown("## 🎯 Dashboard Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🏏 Team Analysis")
        st.write("Deep dive into individual team performance, win rates, recent form, and historical trends.")
    
    with col2:
        st.markdown("### 📊 Season Insights")
        st.write("Analyze each IPL season with match statistics, top performers, and venue analysis.")
    
    with col3:
        st.markdown("### ⚔️ Head to Head")
        st.write("Compare any two teams with detailed head-to-head statistics and match history.")

def show_team_analysis():
    """Team analysis page"""
    st.title("🏏 Team Analysis")
    
    teams = load_teams()
    active_teams = teams[teams['is_active'] == 1]['team_name'].tolist()
    
    # Team selector
    selected_team = st.selectbox("Select Team", active_teams)
    
    if selected_team:
        st.markdown(f"## {selected_team}")
        
        # Get team stats
        conn = get_database_connection()
        
        # Overall stats
        stats = pd.read_sql_query(f"""
            WITH team_matches AS (
                SELECT * FROM matches 
                WHERE team1_name = '{selected_team}' OR team2_name = '{selected_team}'
            )
            SELECT 
                COUNT(*) as total_matches,
                SUM(CASE WHEN match_winner_name = '{selected_team}' THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN match_winner_name != '{selected_team}' AND match_winner_name IS NOT NULL THEN 1 ELSE 0 END) as losses,
                ROUND(100.0 * SUM(CASE WHEN match_winner_name = '{selected_team}' THEN 1 ELSE 0 END) / COUNT(*), 1) as win_pct
            FROM team_matches
        """, conn)
        
        # Display stats
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Matches", int(stats['total_matches'].iloc[0]))
        with col2:
            st.metric("Wins", int(stats['wins'].iloc[0]))
        with col3:
            st.metric("Losses", int(stats['losses'].iloc[0]))
        with col4:
            st.metric("Win %", f"{stats['win_pct'].iloc[0]}%")
        
        # Recent matches
        st.markdown("### Recent Matches")
        recent = pd.read_sql_query(f"""
            SELECT 
                match_date,
                season,
                CASE WHEN team1_name = '{selected_team}' THEN team2_name ELSE team1_name END as opponent,
                match_winner_name as winner,
                venue
            FROM matches
            WHERE team1_name = '{selected_team}' OR team2_name = '{selected_team}'
            ORDER BY match_date DESC
            LIMIT 10
        """, conn)
        
        recent['result'] = recent['winner'].apply(lambda x: '✅ Won' if x == selected_team else '❌ Lost')
        st.dataframe(recent[['match_date', 'opponent', 'result', 'venue']], use_container_width=True, hide_index=True)

def show_match_explorer():
    """Match explorer page"""
    st.title("🔍 Match Explorer")
    st.markdown("Search and filter IPL matches")
    
    matches = load_matches()
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        seasons = ['All'] + sorted(matches['season'].unique().tolist(), reverse=True)
        selected_season = st.selectbox("Season", seasons)
    
    with col2:
        teams = ['All'] + sorted(matches['team1_name'].dropna().unique().tolist())
        selected_team = st.selectbox("Team", teams)
    
    with col3:
        venues = ['All'] + sorted(matches['venue'].dropna().unique().tolist())
        selected_venue = st.selectbox("Venue", venues)
    
    # Filter data
    filtered = matches.copy()
    
    if selected_season != 'All':
        filtered = filtered[filtered['season'] == selected_season]
    
    if selected_team != 'All':
        filtered = filtered[(filtered['team1_name'] == selected_team) | (filtered['team2_name'] == selected_team)]
    
    if selected_venue != 'All':
        filtered = filtered[filtered['venue'] == selected_venue]
    
    # Display results
    st.markdown(f"### Found {len(filtered)} matches")
    
    # Show matches
    display_cols = ['match_date', 'season', 'team1_name', 'team2_name', 'match_winner_name', 'venue']
    st.dataframe(filtered[display_cols], use_container_width=True, hide_index=True)

def show_season_insights():
    """Season insights page"""
    st.title("📊 Season Insights")
    
    matches = load_matches()
    seasons = sorted(matches['season'].unique().tolist(), reverse=True)
    
    selected_season = st.selectbox("Select Season", seasons)
    
    if selected_season:
        season_matches = matches[matches['season'] == selected_season]
        
        st.markdown(f"## IPL {selected_season}")
        
        # Stats
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Matches", len(season_matches))
        with col2:
            st.metric("Teams", season_matches['team1_name'].nunique())
        with col3:
            st.metric("Venues", season_matches['venue'].nunique())
        with col4:
            avg_margin = season_matches['win_by_runs'].fillna(0).mean()
            st.metric("Avg Win Margin", f"{avg_margin:.0f} runs")
        
        # Top teams
        st.markdown("### Top Teams")
        
        team_wins = season_matches['match_winner_name'].value_counts().head(5)
        st.bar_chart(team_wins)

def show_head_to_head():
    """Head to head comparison"""
    st.title("⚔️ Head to Head")
    
    teams = load_teams()
    active_teams = teams[teams['is_active'] == 1]['team_name'].tolist()
    
    col1, col2 = st.columns(2)
    
    with col1:
        team1 = st.selectbox("Team 1", active_teams, key='team1')
    
    with col2:
        team2 = st.selectbox("Team 2", [t for t in active_teams if t != team1], key='team2')
    
    if team1 and team2:
        st.markdown(f"## {team1} vs {team2}")
        
        conn = get_database_connection()
        
        # H2H stats
        h2h = pd.read_sql_query(f"""
            SELECT 
                COUNT(*) as total_matches,
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
            st.metric("Total Matches", int(h2h['total_matches'].iloc[0]))
        with col3:
            st.metric(f"{team2} Wins", int(h2h['team2_wins'].iloc[0]))
        
        # Recent matches
        st.markdown("### Recent Matches")
        recent_h2h = pd.read_sql_query(f"""
            SELECT match_date, season, venue, match_winner_name as winner
            FROM matches
            WHERE (team1_name = '{team1}' AND team2_name = '{team2}')
               OR (team1_name = '{team2}' AND team2_name = '{team1}')
            ORDER BY match_date DESC
            LIMIT 10
        """, conn)
        
        st.dataframe(recent_h2h, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    main()

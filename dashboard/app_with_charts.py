"""
IPL Cricket Analytics Dashboard - Enhanced with Plotly Charts
Interactive visualizations for comprehensive IPL analysis
"""

import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Try to import Gemini
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Get API key from environment
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Page configuration
st.set_page_config(
    page_title="IPL Analytics Dashboard",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="collapsed"  # Collapsed by default
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
    """Load custom CSS with better light mode support"""
    st.markdown("""
        <style>
        /* Main container */
        .main {
            padding: 0rem 1rem;
        }
        
        /* Metric cards - works in both modes */
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
        
        /* Team card - adaptive colors */
        .team-card {
            background: rgba(255, 255, 255, 0.05);
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid #667eea;
            margin: 0.5rem 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        /* Chart container */
        .chart-container {
            background: transparent;
            padding: 1.5rem;
            border-radius: 10px;
            margin: 1rem 0;
        }
        
        /* Headers - better contrast */
        h1 {
            color: #667eea;
            font-weight: 700;
        }
        
        h2 {
            color: #764ba2;
        }
        
        h3 {
            color: #667eea;
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
            transform: translateY(-2px);
            transition: all 0.3s ease;
        }
        
        /* Data display box */
        .data-preview {
            background: rgba(102, 126, 234, 0.1);
            border: 2px solid #667eea;
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
        }
        
        /* Improve sidebar */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
        }
        
        [data-testid="stSidebar"] * {
            color: white !important;
        }
        </style>
    """, unsafe_allow_html=True)

# Chart functions
def create_win_trend_chart(matches_df):
    """Create win trend chart over seasons"""
    # Get wins per team per season
    wins_by_season = matches_df.groupby(['season', 'match_winner_name']).size().reset_index(name='wins')
    
    # Filter top teams
    top_teams = ['Mumbai Indians', 'Chennai Super Kings', 'Kolkata Knight Riders', 
                 'Royal Challengers Bangalore', 'Delhi Capitals', 'Sunrisers Hyderabad']
    
    wins_filtered = wins_by_season[wins_by_season['match_winner_name'].isin(top_teams)]
    
    fig = px.line(wins_filtered, 
                  x='season', 
                  y='wins', 
                  color='match_winner_name',
                  title='🏆 Team Performance Trends Over Seasons',
                  labels={'season': 'Season', 'wins': 'Wins', 'match_winner_name': 'Team'},
                  markers=True)
    
    fig.update_layout(
        height=500,
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def create_toss_impact_chart(matches_df):
    """Create toss impact visualization"""
    toss_data = matches_df[matches_df['toss_decision'].notna()].copy()
    toss_data['won_after_toss'] = (toss_data['toss_winner_id'] == toss_data['match_winner_id'])
    
    impact = toss_data.groupby('toss_decision')['won_after_toss'].agg(['sum', 'count']).reset_index()
    impact['win_percentage'] = (impact['sum'] / impact['count'] * 100).round(1)
    
    fig = go.Figure(data=[
        go.Bar(
            x=impact['toss_decision'],
            y=impact['win_percentage'],
            text=impact['win_percentage'].astype(str) + '%',
            textposition='auto',
            marker=dict(
                color=['#667eea', '#764ba2'],
                line=dict(color='white', width=2)
            )
        )
    ])
    
    fig.update_layout(
        title='⚖️ Toss Impact: Bat First vs Field First',
        xaxis_title='Toss Decision',
        yaxis_title='Win Percentage After Winning Toss',
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=False
    )
    
    return fig

def create_team_comparison_chart(team_stats_df):
    """Create team comparison bar chart"""
    top_10 = team_stats_df.head(10)
    
    fig = go.Figure(data=[
        go.Bar(
            y=top_10['team'],
            x=top_10['win_percentage'],
            orientation='h',
            text=top_10['win_percentage'].astype(str) + '%',
            textposition='auto',
            marker=dict(
                color=top_10['win_percentage'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Win %")
            )
        )
    ])
    
    fig.update_layout(
        title='📊 Top 10 Teams by Win Percentage',
        xaxis_title='Win Percentage (%)',
        yaxis_title='',
        height=500,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def create_venue_chart(matches_df):
    """Create top venues chart"""
    venue_counts = matches_df['venue'].value_counts().head(10).reset_index()
    venue_counts.columns = ['venue', 'matches']
    
    fig = px.bar(venue_counts, 
                 x='matches', 
                 y='venue',
                 orientation='h',
                 title='🏟️ Top 10 Venues by Matches Hosted',
                 labels={'matches': 'Total Matches', 'venue': 'Venue'},
                 color='matches',
                 color_continuous_scale='Blues')
    
    fig.update_layout(
        height=450,
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def create_season_matches_chart(matches_df):
    """Create matches per season chart"""
    season_counts = matches_df.groupby('season').size().reset_index(name='matches')
    
    fig = px.area(season_counts, 
                  x='season', 
                  y='matches',
                  title='📈 Matches Played Per Season',
                  labels={'season': 'Season', 'matches': 'Total Matches'},
                  color_discrete_sequence=['#667eea'])
    
    fig.update_layout(
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def create_team_season_performance(team_name, matches_df):
    """Create team performance over seasons"""
    team_matches = matches_df[
        (matches_df['team1_name'] == team_name) | (matches_df['team2_name'] == team_name)
    ].copy()
    
    # Calculate wins per season
    team_matches['is_win'] = team_matches['match_winner_name'] == team_name
    season_perf = team_matches.groupby('season').agg({
        'match_id': 'count',
        'is_win': 'sum'
    }).reset_index()
    season_perf.columns = ['season', 'matches', 'wins']
    season_perf['losses'] = season_perf['matches'] - season_perf['wins']
    season_perf['win_pct'] = (season_perf['wins'] / season_perf['matches'] * 100).round(1)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=season_perf['season'],
        y=season_perf['wins'],
        name='Wins',
        marker_color='#667eea',
        text=season_perf['wins'],
        textposition='auto'
    ))
    
    fig.add_trace(go.Bar(
        x=season_perf['season'],
        y=season_perf['losses'],
        name='Losses',
        marker_color='#764ba2',
        text=season_perf['losses'],
        textposition='auto'
    ))
    
    fig.update_layout(
        title=f'📊 {team_name} - Season by Season Performance',
        xaxis_title='Season',
        yaxis_title='Matches',
        barmode='stack',
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig

def create_win_loss_pie(team_name, matches_df):
    """Create win/loss pie chart for team"""
    team_matches = matches_df[
        (matches_df['team1_name'] == team_name) | (matches_df['team2_name'] == team_name)
    ].copy()
    
    wins = (team_matches['match_winner_name'] == team_name).sum()
    losses = len(team_matches) - wins
    
    fig = go.Figure(data=[go.Pie(
        labels=['Wins', 'Losses'],
        values=[wins, losses],
        hole=0.4,
        marker=dict(colors=['#667eea', '#764ba2']),
        textinfo='label+percent',
        textfont_size=14
    )])
    
    fig.update_layout(
        title=f'🎯 {team_name} - Overall Win/Loss',
        height=400,
        showlegend=True,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def create_h2h_timeline(team1, team2, matches_df):
    """Create head-to-head timeline"""
    h2h_matches = matches_df[
        ((matches_df['team1_name'] == team1) & (matches_df['team2_name'] == team2)) |
        ((matches_df['team1_name'] == team2) & (matches_df['team2_name'] == team1))
    ].copy()
    
    h2h_matches = h2h_matches.sort_values('match_date')
    h2h_matches['winner_color'] = h2h_matches['match_winner_name'].apply(
        lambda x: team1 if x == team1 else team2
    )
    
    fig = px.scatter(h2h_matches, 
                     x='match_date', 
                     y='season',
                     color='winner_color',
                     title=f'⚔️ {team1} vs {team2} - Match Timeline',
                     labels={'match_date': 'Date', 'season': 'Season', 'winner_color': 'Winner'},
                     hover_data=['venue', 'match_winner_name'],
                     color_discrete_map={team1: '#667eea', team2: '#764ba2'})
    
    fig.update_traces(marker=dict(size=12, line=dict(width=2, color='white')))
    
    fig.update_layout(
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig

def create_h2h_donut(team1, team2, matches_df):
    """Create head-to-head donut chart"""
    h2h_matches = matches_df[
        ((matches_df['team1_name'] == team1) & (matches_df['team2_name'] == team2)) |
        ((matches_df['team1_name'] == team2) & (matches_df['team2_name'] == team1))
    ]
    
    team1_wins = (h2h_matches['match_winner_name'] == team1).sum()
    team2_wins = (h2h_matches['match_winner_name'] == team2).sum()
    
    fig = go.Figure(data=[go.Pie(
        labels=[team1, team2],
        values=[team1_wins, team2_wins],
        hole=0.5,
        marker=dict(colors=['#667eea', '#764ba2']),
        textinfo='label+value',
        textfont_size=14
    )])
    
    fig.update_layout(
        title='🏆 Head to Head Wins',
        height=400,
        annotations=[dict(text=f'{team1_wins + team2_wins}<br>Matches', 
                          x=0.5, y=0.5, font_size=20, showarrow=False)],
        showlegend=True,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

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
            ["🏠 Home", "🏏 Team Analysis", "🔍 Match Explorer", "📊 Season Insights", "⚔️ Head to Head", "🤖 AI Assistant"],
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
    elif page == "🤖 AI Assistant":
        show_ai_assistant()

def show_home_page():
    """Home page with overview and charts"""
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
    
    # Charts section
    st.markdown("## 📈 Visual Insights")
    
    # Row 1: Win trends and toss impact
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(create_win_trend_chart(matches), use_container_width=True)
    
    with col2:
        st.plotly_chart(create_toss_impact_chart(matches), use_container_width=True)
    
    # Row 2: Team comparison and venues
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(create_team_comparison_chart(team_stats), use_container_width=True)
    
    with col2:
        st.plotly_chart(create_venue_chart(matches), use_container_width=True)
    
    # Row 3: Season matches timeline
    st.plotly_chart(create_season_matches_chart(matches), use_container_width=True)
    
    # Recent matches in expandable section
    with st.expander("📅 Recent Matches", expanded=False):
        recent = matches.head(10)[['match_date', 'team1_name', 'team2_name', 'match_winner_name', 'venue']]
        st.dataframe(recent, use_container_width=True, hide_index=True)

def show_team_analysis():
    """Team analysis page with charts"""
    st.title("🏏 Team Analysis")
    
    teams = load_teams()
    active_teams = teams[teams['is_active'] == 1]['team_name'].tolist()
    matches = load_matches()
    
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
        
        # Charts
        st.markdown("### 📊 Performance Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(create_team_season_performance(selected_team, matches), use_container_width=True)
        
        with col2:
            st.plotly_chart(create_win_loss_pie(selected_team, matches), use_container_width=True)
        
        # Recent matches
        st.markdown("### 📅 Recent Matches")
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
    
    # Show quick chart if filtered
    if len(filtered) > 0 and len(filtered) < len(matches):
        if selected_team != 'All':
            # Show team performance in filtered matches
            wins = (filtered['match_winner_name'] == selected_team).sum()
            losses = len(filtered) - wins
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Filtered Matches", len(filtered))
            with col2:
                st.metric("Wins", wins)
            with col3:
                st.metric("Losses", losses)
    
    # Show matches
    display_cols = ['match_date', 'season', 'team1_name', 'team2_name', 'match_winner_name', 'venue']
    st.dataframe(filtered[display_cols], use_container_width=True, hide_index=True)

def show_season_insights():
    """Season insights page with charts"""
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
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Top teams chart
            team_wins = season_matches['match_winner_name'].value_counts().head(8)
            fig = px.bar(x=team_wins.values, 
                        y=team_wins.index,
                        orientation='h',
                        title=f'🏆 Top Teams - IPL {selected_season}',
                        labels={'x': 'Wins', 'y': 'Team'},
                        color=team_wins.values,
                        color_continuous_scale='Viridis')
            fig.update_layout(height=400, showlegend=False, 
                            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Venue distribution
            venue_dist = season_matches['venue'].value_counts().head(8)
            fig = px.pie(values=venue_dist.values, 
                        names=venue_dist.index,
                        title=f'🏟️ Top Venues - IPL {selected_season}')
            fig.update_layout(height=400, 
                            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)

def show_head_to_head():
    """Head to head comparison with charts"""
    st.title("⚔️ Head to Head")
    
    teams = load_teams()
    active_teams = teams[teams['is_active'] == 1]['team_name'].tolist()
    matches = load_matches()
    
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
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(create_h2h_donut(team1, team2, matches), use_container_width=True)
        
        with col2:
            st.plotly_chart(create_h2h_timeline(team1, team2, matches), use_container_width=True)
        
        # Recent matches
        st.markdown("### 📅 Recent Matches")
        recent_h2h = pd.read_sql_query(f"""
            SELECT match_date, season, venue, match_winner_name as winner
            FROM matches
            WHERE (team1_name = '{team1}' AND team2_name = '{team2}')
               OR (team1_name = '{team2}' AND team2_name = '{team1}')
            ORDER BY match_date DESC
            LIMIT 10
        """, conn)
        
        st.dataframe(recent_h2h, use_container_width=True, hide_index=True)

# Gemini AI Helper Functions
def get_database_schema():
    """Get database schema for AI context"""
    return """
    Database Schema:
    
    Table: teams (team_id, team_name, short_name, is_active)
    Table: matches (match_id, season, match_date, venue, city, team1_name, team2_name, 
                   toss_winner_name, toss_decision, match_winner_name, win_by_runs, 
                   win_by_wickets, player_of_match)
    
    Data: 1,109 matches, 17 seasons (2008-2019, 2021-2025), 14 teams
    """

# Custom Theme System
def get_image_themes():
    """Define custom themes for different types of charts/images"""
    return {
        "IPL Official": {
            "primary_color": "#667eea",
            "secondary_color": "#764ba2",
            "accent_color": "#f5576c",
            "background": "gradient purple to violet",
            "style": "modern, official IPL branding, professional sports aesthetic",
            "best_for": "official announcements, championship posters, season highlights"
        },
        "Team Victory": {
            "primary_color": "#4ade80",
            "secondary_color": "#22c55e",
            "accent_color": "#fbbf24",
            "background": "energetic green with gold accents",
            "style": "celebratory, dynamic, victorious mood, confetti and trophies",
            "best_for": "win celebrations, championship posters, milestone achievements"
        },
        "Statistical Analysis": {
            "primary_color": "#3b82f6",
            "secondary_color": "#1e40af",
            "accent_color": "#06b6d4",
            "background": "clean white or light gray with blue accents",
            "style": "data-driven, minimalist, professional charts, clear typography",
            "best_for": "infographics, statistical comparisons, data visualizations"
        },
        "Rivalry Showdown": {
            "primary_color": "#ef4444",
            "secondary_color": "#dc2626",
            "accent_color": "#f59e0b",
            "background": "intense red vs blue split, dramatic lighting",
            "style": "competitive, high-energy, face-off aesthetic, versus layout",
            "best_for": "head-to-head matchups, rivalry posters, pre-match promotions"
        },
        "Vintage Cricket": {
            "primary_color": "#92400e",
            "secondary_color": "#78350f",
            "accent_color": "#fbbf24",
            "background": "sepia tones, aged paper texture, classic cricket aesthetic",
            "style": "retro, nostalgic, heritage cricket, vintage photography style",
            "best_for": "legacy content, historical comparisons, throwback posts"
        },
        "Night Match": {
            "primary_color": "#1e1b4b",
            "secondary_color": "#312e81",
            "accent_color": "#fbbf24",
            "background": "dark navy with stadium lights, evening atmosphere",
            "style": "dramatic, night match aesthetic, stadium lights, evening energy",
            "best_for": "night match promotions, evening game highlights, dramatic moments"
        },
        "Social Media": {
            "primary_color": "#ec4899",
            "secondary_color": "#db2777",
            "accent_color": "#f59e0b",
            "background": "vibrant gradient, eye-catching, mobile-optimized",
            "style": "bold, trendy, instagram-ready, high contrast, shareable",
            "best_for": "twitter posts, instagram stories, viral content, quick facts"
        },
        "Performance Dashboard": {
            "primary_color": "#8b5cf6",
            "secondary_color": "#7c3aed",
            "accent_color": "#06b6d4",
            "background": "dashboard UI, card-based layout, professional analytics",
            "style": "clean dashboard, KPI cards, progress bars, modern UI elements",
            "best_for": "player stats, team performance, season analytics, comparison charts"
        }
    }

def get_chart_type_suggestions():
    """Suggest chart types based on data"""
    return {
        "comparison": ["bar", "horizontal_bar", "radar", "grouped_bar"],
        "trend": ["line", "area", "stacked_area"],
        "distribution": ["pie", "donut", "treemap"],
        "relationship": ["scatter", "bubble", "heatmap"],
        "ranking": ["horizontal_bar", "lollipop", "ordered_bar"],
        "part_to_whole": ["pie", "donut", "stacked_bar", "treemap"]
    }

def load_database_data_options():
    """Load available data options for user selection"""
    conn = get_database_connection()
    
    return {
        "Team Statistics": {
            "query": """
                SELECT 
                    t.team_name,
                    COUNT(m.match_id) as total_matches,
                    SUM(CASE WHEN m.match_winner_name = t.team_name THEN 1 ELSE 0 END) as wins,
                    ROUND(100.0 * SUM(CASE WHEN m.match_winner_name = t.team_name THEN 1 ELSE 0 END) / COUNT(m.match_id), 1) as win_percentage
                FROM teams t
                LEFT JOIN matches m ON t.team_name = m.team1_name OR t.team_name = m.team2_name
                WHERE t.is_active = 1
                GROUP BY t.team_name
                ORDER BY win_percentage DESC
            """,
            "description": "Overall statistics for all active teams",
            "recommended_chart": "horizontal_bar",
            "recommended_theme": "Statistical Analysis"
        },
        "Season Winners": {
            "query": """
                SELECT 
                    season,
                    match_winner_name as champion,
                    COUNT(*) as total_wins
                FROM matches
                WHERE match_winner_name IS NOT NULL
                GROUP BY season, match_winner_name
                HAVING COUNT(*) >= 10
                ORDER BY season DESC, total_wins DESC
            """,
            "description": "Championship winners by season",
            "recommended_chart": "timeline",
            "recommended_theme": "Team Victory"
        },
        "Toss Impact Analysis": {
            "query": """
                SELECT 
                    toss_decision,
                    COUNT(*) as total_matches,
                    SUM(CASE WHEN toss_winner_id = match_winner_id THEN 1 ELSE 0 END) as wins_after_toss,
                    ROUND(100.0 * SUM(CASE WHEN toss_winner_id = match_winner_id THEN 1 ELSE 0 END) / COUNT(*), 1) as win_percentage
                FROM matches
                WHERE toss_decision IS NOT NULL
                GROUP BY toss_decision
            """,
            "description": "Win rates when winning toss - bat vs field",
            "recommended_chart": "bar_comparison",
            "recommended_theme": "Statistical Analysis"
        },
        "Top Venues": {
            "query": """
                SELECT 
                    venue,
                    city,
                    COUNT(*) as matches_hosted
                FROM matches
                WHERE venue IS NOT NULL
                GROUP BY venue, city
                ORDER BY matches_hosted DESC
                LIMIT 10
            """,
            "description": "Top 10 stadiums by matches hosted",
            "recommended_chart": "horizontal_bar",
            "recommended_theme": "IPL Official"
        },
        "Recent Season Stats": {
            "query": """
                SELECT 
                    season,
                    COUNT(*) as total_matches,
                    COUNT(DISTINCT venue) as venues_used,
                    COUNT(DISTINCT team1_name) as teams_participated
                FROM matches
                WHERE season >= 2020
                GROUP BY season
                ORDER BY season DESC
            """,
            "description": "Statistics for recent IPL seasons (2020+)",
            "recommended_chart": "grouped_bar",
            "recommended_theme": "Performance Dashboard"
        }
    }


def get_image_themes():
    """8 Custom themes for different image types"""
    return {
        "IPL Official": {
            "primary_color": "#667eea",
            "secondary_color": "#764ba2",
            "accent_color": "#f5576c",
            "background": "gradient purple to violet",
            "style": "modern, official IPL branding, professional sports",
            "best_for": "official announcements, championships"
        },
        "Statistical Analysis": {
            "primary_color": "#3b82f6",
            "secondary_color": "#1e40af",
            "accent_color": "#06b6d4",
            "background": "clean white with blue accents",
            "style": "data-driven, minimalist charts, clear typography",
            "best_for": "infographics, data visualizations"
        },
        "Team Victory": {
            "primary_color": "#4ade80",
            "secondary_color": "#22c55e",
            "accent_color": "#fbbf24",
            "background": "energetic green with gold",
            "style": "celebratory, dynamic, victorious, trophies",
            "best_for": "win celebrations, milestones"
        },
        "Rivalry Showdown": {
            "primary_color": "#ef4444",
            "secondary_color": "#dc2626",
            "accent_color": "#f59e0b",
            "background": "red vs blue split, dramatic",
            "style": "competitive, high-energy, face-off aesthetic",
            "best_for": "head-to-head matchups, rivalries"
        },
        "Vintage Cricket": {
            "primary_color": "#92400e",
            "secondary_color": "#78350f",
            "accent_color": "#fbbf24",
            "background": "sepia tones, aged paper",
            "style": "retro, nostalgic, heritage cricket",
            "best_for": "legacy content, historical"
        },
        "Night Match": {
            "primary_color": "#1e1b4b",
            "secondary_color": "#312e81",
            "accent_color": "#fbbf24",
            "background": "dark navy with stadium lights",
            "style": "dramatic night match, evening energy",
            "best_for": "night matches, dramatic moments"
        },
        "Social Media": {
            "primary_color": "#ec4899",
            "secondary_color": "#db2777",
            "accent_color": "#f59e0b",
            "background": "vibrant gradient, eye-catching",
            "style": "bold, trendy, instagram-ready, shareable",
            "best_for": "twitter, instagram, viral content"
        },
        "Performance Dashboard": {
            "primary_color": "#8b5cf6",
            "secondary_color": "#7c3aed",
            "accent_color": "#06b6d4",
            "background": "dashboard UI, card-based",
            "style": "clean dashboard, KPI cards, modern UI",
            "best_for": "player stats, team performance"
        }
    }

def load_database_data_options():
    """5 pre-configured data sources"""
    return {
        "Team Statistics": {
            "query": """
                SELECT 
                    t.team_name,
                    COUNT(m.match_id) as total_matches,
                    SUM(CASE WHEN m.match_winner_name = t.team_name THEN 1 ELSE 0 END) as wins,
                    ROUND(100.0 * SUM(CASE WHEN m.match_winner_name = t.team_name THEN 1 ELSE 0 END) / COUNT(m.match_id), 1) as win_percentage
                FROM teams t
                LEFT JOIN matches m ON t.team_name = m.team1_name OR t.team_name = m.team2_name
                WHERE t.is_active = 1
                GROUP BY t.team_name
                ORDER BY win_percentage DESC
            """,
            "description": "Overall statistics for all active teams",
            "recommended_chart": "horizontal_bar",
            "recommended_theme": "Statistical Analysis"
        },
        "Season Winners": {
            "query": """
                SELECT 
                    season,
                    match_winner_name as champion,
                    COUNT(*) as total_wins
                FROM matches
                WHERE match_winner_name IS NOT NULL
                GROUP BY season, match_winner_name
                HAVING COUNT(*) >= 10
                ORDER BY season DESC, total_wins DESC
            """,
            "description": "Championship winners by season",
            "recommended_chart": "timeline",
            "recommended_theme": "Team Victory"
        },
        "Toss Impact": {
            "query": """
                SELECT 
                    toss_decision,
                    COUNT(*) as total,
                    SUM(CASE WHEN toss_winner_id = match_winner_id THEN 1 ELSE 0 END) as wins,
                    ROUND(100.0 * SUM(CASE WHEN toss_winner_id = match_winner_id THEN 1 ELSE 0 END) / COUNT(*), 1) as win_pct
                FROM matches
                WHERE toss_decision IS NOT NULL
                GROUP BY toss_decision
            """,
            "description": "Win rates: bat vs field first",
            "recommended_chart": "bar",
            "recommended_theme": "Statistical Analysis"
        },
        "Top Venues": {
            "query": """
                SELECT venue, city, COUNT(*) as matches
                FROM matches
                WHERE venue IS NOT NULL
                GROUP BY venue, city
                ORDER BY matches DESC
                LIMIT 10
            """,
            "description": "Top 10 stadiums by matches",
            "recommended_chart": "horizontal_bar",
            "recommended_theme": "IPL Official"
        },
        "Recent Seasons": {
            "query": """
                SELECT season, COUNT(*) as matches, 
                       COUNT(DISTINCT venue) as venues,
                       COUNT(DISTINCT team1_name) as teams
                FROM matches
                WHERE season >= 2020
                GROUP BY season
                ORDER BY season DESC
            """,
            "description": "Recent IPL seasons (2020+)",
            "recommended_chart": "grouped_bar",
            "recommended_theme": "Performance Dashboard"
        }
    }

    

def initialize_gemini():
    """Initialize Gemini API with key from environment"""
    if not GEMINI_API_KEY:
        return False
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        return True
    except Exception as e:
        return False

def generate_sql_from_question(question):
    """Use Gemini to convert natural language to SQL"""
    try:
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        prompt = f"""You are an expert SQL developer for an IPL cricket database.

{get_database_schema()}

User Question: {question}

Generate a valid SQLite query. Return ONLY the SQL query, no explanations.
Use team_name columns for display, add LIMIT 20 for large results."""
        
        response = model.generate_content(prompt)
        sql_query = response.text.strip().replace('```sql', '').replace('```', '').strip()
        return sql_query
    except Exception as e:
        return f"Error: {e}"

def generate_insight_from_data(question, data):
    """Use Gemini to generate insights"""
    try:
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        prompt = f"""You are a cricket analyst.

User asked: {question}
Data: {data.head(10).to_string() if len(data) > 0 else "No results"}

Provide a 2-3 sentence analysis with the answer and one interesting insight."""
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Analysis unavailable: {e}"

def generate_image(user_prompt, theme_name, data_context=None):
    """Generate image with custom theme and optional data"""
    try:
        themes = get_image_themes()
        theme = themes.get(theme_name, themes["IPL Official"])
        
        prompt = f"""Generate high-quality IPL cricket image.

Request: {user_prompt}

Theme:
- Colors: {theme['primary_color']}, {theme['secondary_color']}, {theme['accent_color']}
- Background: {theme['background']}
- Style: {theme['style']}
"""
        
        if data_context:
            prompt += f"\n\nData to visualize:\n{data_context}\n\nUse this EXACT data in the image."
        
        prompt += "\n\nRequirements: Professional, 16:9, high-res, IPL branding, clear typography."
        
        model = genai.GenerativeModel('gemini-3-pro-image-preview')
        response = model.generate_content(prompt)
        return response
    except Exception as e:
        st.error(f"Error: {e}")
        return None

def generate_image_custom(user_prompt, theme_config, data_context=None):
    """Generate image with custom theme configuration"""
    try:
        prompt = f"""Generate high-quality IPL cricket image.

User Request: {user_prompt}

Theme Configuration:
- Theme Name: {theme_config['name']}
- Colors: {theme_config['colors']}
- Background: {theme_config['background']}
- Style: {theme_config['style']}

"""
        
        if data_context:
            prompt += f"""
Data to Visualize (USE THIS EXACT DATA):
{data_context}

IMPORTANT: Create the visualization using this EXACT data. Show accurate numbers, labels, and values.
"""
        
        prompt += """
Requirements:
- Professional quality, suitable for presentations and social media
- High resolution (1920x1080 or 16:9 aspect ratio)
- Clear, readable typography
- IPL branding elements where appropriate
- Accurate data representation if data is provided
- Visually striking and share-worthy
"""
        
        model = genai.GenerativeModel('gemini-3-pro-image-preview')
        response = model.generate_content(prompt)
        return response
    except Exception as e:
        st.error(f"Generation Error: {e}")
        return None

def show_ai_assistant():
    """AI Assistant page"""
    st.title("🤖 IPL AI Assistant")
    st.markdown("### Ask questions in natural language - No setup required!")
    
    if not GEMINI_AVAILABLE:
        st.error("❌ Install: `pip install google-generativeai python-dotenv`")
        return
    
    if not GEMINI_API_KEY:
        st.error("❌ API key not found in .env file")
        st.info("Add `GEMINI_API_KEY=your_key` to .env file in project root")
        return
    
    if not initialize_gemini():
        st.error("❌ Failed to initialize Gemini")
        return
    
    st.success("✅ AI Ready - Ask me anything!")
    
    # Tabs
    tab1, tab2 = st.tabs(["💬 Ask Questions", "🎨 Generate Images"])
    
    with tab1:
        st.markdown("### 💬 Chat with AI")
        
        with st.expander("💡 Example Questions"):
            st.markdown("""
            - Which team won the most matches?
            - Show me Mumbai Indians' win rate
            - Compare CSK and MI head to head
            - What's the toss impact?
            - Who won IPL 2024?
            """)
        
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()
        
        # Display messages
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                if "data" in msg and msg["data"] is not None:
                    st.dataframe(msg["data"], use_container_width=True, hide_index=True)
                if "sql" in msg:
                    with st.expander("🔍 SQL"):
                        st.code(msg["sql"], language="sql")
        
        # Input
        if prompt := st.chat_input("Ask about IPL..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.chat_message("assistant"):
                with st.spinner("🤔 Thinking..."):
                    sql = generate_sql_from_question(prompt)
                    
                    with st.expander("🔍 SQL Query"):
                        st.code(sql, language="sql")
                    
                    try:
                        conn = get_database_connection()
                        data = pd.read_sql_query(sql, conn)
                        
                        if len(data) > 0:
                            st.dataframe(data, use_container_width=True, hide_index=True)
                            insight = generate_insight_from_data(prompt, data)
                            st.info(f"💡 {insight}")
                            
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": insight,
                                "data": data,
                                "sql": sql
                            })
                        else:
                            msg = "No results found. Try rephrasing."
                            st.warning(msg)
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": msg,
                                "sql": sql
                            })
                    except Exception as e:
                        error = f"❌ Error: {e}"
                        st.error(error)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": error,
                            "sql": sql
                        })
    
    with tab2:
        st.markdown("### 🎨 AI Image Generation")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("#### 📊 Database Data (Optional)")
            use_data = st.checkbox("Use IPL data from database")
            
            data_context = None
            if use_data:
                # OPTION: Pre-defined OR Custom
                data_mode = st.radio("Data Source:", ["Quick Select", "Custom Query"], horizontal=True)
                
                if data_mode == "Quick Select":
                    # Original dropdown with examples
                    data_opts = load_database_data_options()
                    selected = st.selectbox("Select Data", list(data_opts.keys()), help="Pre-configured data queries")
                    
                    if selected:
                        info = data_opts[selected]
                        st.info(f"📝 {info['description']}")
                        st.caption(f"💡 Recommended: {info['recommended_theme']} theme")
                        
                        if st.button("📊 Load Data", key="load_quick"):
                            try:
                                conn = get_database_connection()
                                data = pd.read_sql_query(info['query'], conn)
                                st.session_state['data'] = data
                                st.session_state['data_name'] = selected
                                st.session_state['rec_theme'] = info['recommended_theme']
                            except Exception as e:
                                st.error(f"Error: {e}")
                
                else:  # Custom Query
                    st.markdown("##### 💬 Ask for data in natural language:")
                    custom_query = st.text_input(
                        "Data Query",
                        placeholder="Example: Show me top 5 teams by win rate in last 3 seasons",
                        help="Describe what data you want - AI will generate SQL"
                    )
                    
                    if st.button("🔍 Get Data", key="load_custom") and custom_query:
                        with st.spinner("🤔 Generating query..."):
                            try:
                                # Generate SQL from natural language
                                sql = generate_sql_from_question(custom_query)
                                
                                st.code(sql, language="sql")
                                
                                # Execute query
                                conn = get_database_connection()
                                data = pd.read_sql_query(sql, conn)
                                
                                st.session_state['data'] = data
                                st.session_state['data_name'] = "Custom Query"
                                st.session_state['custom_sql'] = sql
                                st.success(f"✅ Got {len(data)} rows!")
                                
                            except Exception as e:
                                st.error(f"❌ Error: {e}")
                                st.info("💡 Try rephrasing your question")
                
                # Show loaded data (for both modes)
                if 'data' in st.session_state:
                    st.markdown("##### 📋 Data Preview:")
                    st.dataframe(st.session_state['data'], use_container_width=True, hide_index=True)
                    
                    # Prepare context for AI
                    data_context = f"""Dataset: {st.session_state.get('data_name', 'Custom')}
Rows: {len(st.session_state['data'])}
Columns: {', '.join(st.session_state['data'].columns.tolist())}

Data:
{st.session_state['data'].to_string()}"""
        
        with col2:
            st.markdown("#### 🎨 Configuration")
            
            # OPTION: Pre-defined Theme OR Custom Style
            theme_mode = st.radio("Theme:", ["Pre-defined", "Custom Style"], horizontal=True)
            
            if theme_mode == "Pre-defined":
                # Original dropdown themes
                themes = get_image_themes()
                theme_list = list(themes.keys())
                
                if use_data and 'rec_theme' in st.session_state:
                    rec = st.session_state['rec_theme']
                    default_idx = theme_list.index(rec) if rec in theme_list else 0
                else:
                    default_idx = 0
                
                selected_theme = st.selectbox("Select Theme", theme_list, index=default_idx)
                
                if selected_theme:
                    t = themes[selected_theme]
                    with st.expander(f"🎨 {selected_theme} Details"):
                        st.markdown(f"""
                        **Colors:** {t['primary_color']}, {t['secondary_color']}, {t['accent_color']}  
                        **Style:** {t['style']}  
                        **Best for:** {t['best_for']}
                        """)
                    
                    # Use pre-defined theme
                    theme_config = {
                        "name": selected_theme,
                        "colors": f"{t['primary_color']}, {t['secondary_color']}, {t['accent_color']}",
                        "background": t['background'],
                        "style": t['style']
                    }
            
            else:  # Custom Style
                st.markdown("##### 🎨 Describe your custom style:")
                
                custom_colors = st.text_input(
                    "Colors",
                    placeholder="blue, gold, white",
                    help="Describe colors you want"
                )
                
                custom_style = st.text_area(
                    "Visual Style",
                    placeholder="modern, minimalist, professional with gradients",
                    height=80,
                    help="Describe the visual style, mood, aesthetic"
                )
                
                custom_background = st.text_input(
                    "Background",
                    placeholder="gradient from blue to purple",
                    help="Describe background style"
                )
                
                # Use custom theme
                theme_config = {
                    "name": "Custom Style",
                    "colors": custom_colors or "default IPL colors",
                    "background": custom_background or "clean background",
                    "style": custom_style or "modern professional"
                }
            
            # Image prompt
            st.markdown("---")
            prompt = st.text_area(
                "Describe image:",
                placeholder="Example: Create a bar chart comparing top 5 teams by wins with team logos and colors",
                height=100,
                help="Be specific about chart type, elements, layout"
            )
        
        # Generate button (full width)
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            generate_btn = st.button("🎨 Generate Image", use_container_width=True, type="primary")
        
        if generate_btn and prompt:
            if use_data and 'data' not in st.session_state:
                st.warning("⚠️ Please load data first!")
            else:
                with st.spinner("🎨 Generating your image... (10-20 seconds)"):
                    # Prepare data context
                    final_data = data_context if use_data else None
                    
                    # Generate image with custom or pre-defined theme
                    response = generate_image_custom(prompt, theme_config, final_data)
                    
                    if response:
                        try:
                            image_found = False
                            if hasattr(response, 'parts'):
                                for part in response.parts:
                                    if hasattr(part, 'inline_data') and part.inline_data:
                                        st.success("✅ Image generated successfully!")
                                        st.image(part.inline_data.data, 
                                                caption=f"Theme: {theme_config['name']}", 
                                                use_container_width=True)
                                        image_found = True
                                        
                                        # Download button
                                        st.download_button(
                                            label="📥 Download Image",
                                            data=part.inline_data.data,
                                            file_name=f"ipl_{theme_config['name'].lower().replace(' ', '_')}.png",
                                            mime="image/png"
                                        )
                            
                            if not image_found:
                                st.warning("No image in response")
                                if hasattr(response, 'text'):
                                    st.write(response.text)
                        except Exception as e:
                            st.error(f"Error: {e}")
        
        # Tips
        with st.expander("💡 Tips & Examples"):
            st.markdown("""
            ### 📊 Data Options:
            
            **Quick Select:** Choose from pre-configured queries
            - Team Statistics, Season Winners, Toss Impact, etc.
            
            **Custom Query:** Ask in natural language
            - "Show me Mumbai Indians' performance by season"
            - "Compare CSK and MI win rates"
            - "Top 5 bowlers by wickets in 2024"
            
            ### 🎨 Theme Options:
            
            **Pre-defined:** Choose from 8 professional themes
            - IPL Official, Statistical Analysis, Team Victory, etc.
            
            **Custom Style:** Describe your own
            - Colors: "red, yellow, black"
            - Style: "retro 90s aesthetic with neon"
            - Background: "gradient sunset colors"
            
            ### ✍️ Image Prompts:
            
            **Be Specific:**
            - Chart type: bar, pie, line, scatter
            - Elements: team logos, player photos, statistics
            - Layout: horizontal, vertical, grid
            - Labels: show values, percentages, legends
            
            **Examples:**
            - "Create horizontal bar chart showing win percentages with team colors"
            - "Make a pie chart of venue distribution with stadium images"
            - "Design a comparison infographic for MI vs CSK with head-to-head stats"
            """)

if __name__ == "__main__":
    main()
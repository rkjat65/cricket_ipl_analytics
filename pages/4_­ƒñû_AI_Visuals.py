"""
AI-Powered Visualizations Page
Experimental feature using Google Gemini for chart generation
"""

import streamlit as st
import sys
from pathlib import Path
from io import BytesIO

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from utils.ai_generator import get_chart_generator
    GEMINI_AVAILABLE = True
except Exception as e:
    GEMINI_AVAILABLE = False
    st.error(f"Gemini AI not configured: {e}")

# Page config
st.set_page_config(
    page_title="AI Visuals - Cricket Analytics",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .ai-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .experimental-badge {
        background-color: #fbbf24;
        color: #1f2937;
        padding: 0.25rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.875rem;
    }
    
    .comparison-box {
        border: 2px solid #e5e7eb;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="ai-header">
    <h1>🤖 AI-Powered Visualizations</h1>
    <span class="experimental-badge">EXPERIMENTAL FEATURE</span>
    <p style="margin-top: 1rem; font-size: 1.1rem;">
        Generate cricket analytics charts using Google Gemini AI
    </p>
</div>
""", unsafe_allow_html=True)

# Information section
with st.expander("ℹ️ About This Feature", expanded=False):
    st.markdown("""
    ### What is this?
    
    This is an experimental feature that uses **Google Gemini's image generation** capabilities 
    to create data visualizations based on cricket analytics.
    
    ### How it works:
    
    1. **You provide** the data summary and chart specifications
    2. **AI generates** a professional visualization
    3. **Compare** with traditional Plotly charts
    
    ### Why use AI for charts?
    
    - 🎨 **Creative designs** beyond template limitations
    - ⚡ **Quick prototyping** for presentation ideas
    - 🔍 **Unique perspectives** on data visualization
    - 🚀 **Experimental** - exploring cutting-edge tech
    
    ### Important Notes:
    
    - ⚠️ AI-generated charts are **not as precise** as traditional charts
    - 🔢 Data accuracy may vary - always verify numbers
    - 💡 Best used for **creative presentations**, not technical analysis
    - 🌟 This demonstrates **innovation** and **AI integration** skills
    """)

# Main content
if not GEMINI_AVAILABLE:
    st.error("""
    ### ⚠️ Gemini API Not Configured
    
    To use this feature, you need to:
    1. Get a Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
    2. Add it to your `.env` file as `GEMINI_API_KEY=your_key_here`
    3. Restart the application
    """)
    st.stop()

# Chart generation interface
st.subheader("🎨 Generate AI Chart")

col1, col2 = st.columns(2)

with col1:
    chart_type = st.selectbox(
        "Chart Type",
        ["Bar Chart", "Line Chart", "Pie Chart", "Scatter Plot", "Grouped Bar Chart", "Stacked Bar Chart"],
        help="Select the type of visualization you want to generate"
    )
    
    title = st.text_input(
        "Chart Title",
        value="IPL 2024 - Team Performance",
        help="Enter a descriptive title for your chart"
    )

with col2:
    preset = st.selectbox(
        "Use Preset Example",
        ["Custom", "Team Comparison", "Player Stats", "Match Analysis", "Venue Performance"],
        help="Select a preset or choose 'Custom' for your own data"
    )

# Preset data
preset_data = {
    "Team Comparison": {
        "data": """
Team Comparison: Mumbai Indians vs Chennai Super Kings

- Matches Played: MI = 14, CSK = 14
- Matches Won: MI = 8, CSK = 7
- Average Score: MI = 175, CSK = 168
- Powerplay Strike Rate: MI = 145, CSK = 138
- Death Over Economy: MI = 9.2, CSK = 8.8
""",
        "context": "Show side-by-side comparison bars for both teams"
    },
    "Player Stats": {
        "data": """
Top 5 Run Scorers - IPL 2024

1. Virat Kohli: 741 runs
2. Ruturaj Gaikwad: 683 runs
3. Faf du Plessis: 654 runs
4. Shubman Gill: 643 runs
5. KL Rahul: 616 runs

Strike Rates: Kohli (145), Gaikwad (141), Faf (152), Gill (147), Rahul (138)
""",
        "context": "Use vibrant colors for each player, include strike rate as secondary metric"
    },
    "Match Analysis": {
        "data": """
Toss Impact Analysis - IPL 2024

Total Matches: 70
- Toss Winner Won Match: 42 (60%)
- Toss Winner Lost Match: 28 (40%)

Batting First:
- Wins: 32 (46%)
- Average Score: 168

Chasing:
- Wins: 38 (54%)
- Average Chase: 175
""",
        "context": "Show clear distinction between toss outcomes and match results"
    },
    "Venue Performance": {
        "data": """
Top Scoring Venues - IPL 2024

1. Wankhede Stadium (Mumbai): Avg 185
2. Chinnaswamy Stadium (Bangalore): Avg 178
3. Eden Gardens (Kolkata): Avg 172
4. MA Chidambaram (Chennai): Avg 165
5. Arun Jaitley (Delhi): Avg 168

Highest Score: Wankhede - 235/4
Lowest Score: Chepauk - 112 all out
""",
        "context": "Horizontal bar chart with stadium images or colors representing each venue"
    }
}

# Data input
if preset != "Custom":
    data_summary = st.text_area(
        "Data Summary",
        value=preset_data[preset]["data"],
        height=200,
        help="This data will be used to generate the chart"
    )
    additional_context = st.text_area(
        "Additional Styling Instructions",
        value=preset_data[preset]["context"],
        height=100,
        help="Provide any additional context or styling preferences"
    )
else:
    data_summary = st.text_area(
        "Data Summary",
        value="Enter your cricket statistics here...\nExample:\nTeam A: 180 runs\nTeam B: 165 runs",
        height=200,
        help="Describe your data in natural language"
    )
    additional_context = st.text_area(
        "Additional Styling Instructions (Optional)",
        value="",
        height=100,
        help="Any specific styling or layout preferences"
    )

# Generate button
if st.button("🎨 Generate AI Chart", type="primary", use_container_width=True):
    if not data_summary or data_summary.strip() == "":
        st.error("Please provide data summary")
    else:
        with st.spinner("🤖 AI is creating your visualization... This may take 10-30 seconds"):
            try:
                # Initialize generator
                generator = get_chart_generator()
                
                # Generate chart
                ai_image = generator.generate_chart(
                    chart_type=chart_type.lower(),
                    data_summary=data_summary,
                    title=title,
                    additional_context=additional_context if additional_context else None
                )
                
                # Display result
                st.success("✅ Chart generated successfully!")
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.image(ai_image, caption=f"AI-Generated: {title}", use_column_width=True)
                
                with col2:
                    st.markdown("### 📊 Chart Info")
                    st.markdown(f"""
                    - **Type**: {chart_type}
                    - **Title**: {title}
                    - **Generated**: Just now
                    - **Model**: Google Gemini
                    """)
                    
                    # Download button
                    buf = BytesIO()
                    ai_image.save(buf, format='PNG')
                    byte_im = buf.getvalue()
                    
                    st.download_button(
                        label="⬇️ Download Chart",
                        data=byte_im,
                        file_name=f"cricket_ai_chart_{title.replace(' ', '_').lower()}.png",
                        mime="image/png",
                        use_container_width=True
                    )
                
                # Disclaimer
                st.info("""
                ⚠️ **Experimental Feature Disclaimer**: AI-generated charts may not be 100% accurate. 
                Always verify data points and use traditional visualization tools for critical analysis.
                """)
                
            except Exception as e:
                st.error(f"❌ Chart generation failed: {e}")
                st.info("💡 **Troubleshooting:**\n- Check if your API key is valid\n- Ensure your data summary is clear\n- Try simplifying your request")

# Comparison Section
st.markdown("---")
st.subheader("📊 Traditional vs AI Visualization")

st.markdown("""
### Why Both Approaches Matter

In this project, we use **both traditional and AI-powered visualizations**:
""")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="comparison-box">
    <h4>📈 Traditional Charts (Plotly)</h4>
    <ul>
        <li>✅ Precise and accurate</li>
        <li>✅ Interactive (zoom, filter, hover)</li>
        <li>✅ Industry standard</li>
        <li>✅ Easy to update with new data</li>
        <li>✅ Consistent styling</li>
        <li>⚠️ Limited to templates</li>
    </ul>
    <p><strong>Best for:</strong> Technical analysis, reports, data exploration</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="comparison-box">
    <h4>🤖 AI-Generated Charts (Gemini)</h4>
    <ul>
        <li>✅ Creative and unique designs</li>
        <li>✅ Natural language input</li>
        <li>✅ Quick concept visualization</li>
        <li>✅ Shows innovation</li>
        <li>⚠️ May have inaccuracies</li>
        <li>⚠️ Not interactive</li>
    </ul>
    <p><strong>Best for:</strong> Presentations, social media, creative projects</p>
    </div>
    """, unsafe_allow_html=True)

# Example gallery
st.markdown("---")
st.subheader("🎨 Example AI-Generated Charts")

st.info("""
💡 **Coming Soon**: Gallery of AI-generated cricket analytics visualizations will be displayed here once generated.
For now, try generating your own using the tool above!
""")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #64748b; padding: 1rem 0;'>
    <p>🚀 This experimental feature demonstrates <strong>AI integration skills</strong> and <strong>innovation</strong></p>
    <p>Built with Google Gemini AI by <a href='https://rkjat.in' target='_blank'>RK Jat</a></p>
</div>
""", unsafe_allow_html=True)

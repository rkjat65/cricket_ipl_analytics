"""
AI Chart Generation utility
Uses Google Gemini to analyze data and create chart code, then executes with matplotlib
"""

import os
from typing import Optional, Dict, Any
import logging
from pathlib import Path
import io
import re

try:
    import PIL.Image
    import google.generativeai as genai
    from dotenv import load_dotenv
    import matplotlib
    import matplotlib.pyplot as plt
    matplotlib.use('Agg')  # Non-interactive backend
except ImportError as e:
    logging.error(f"Required packages not installed: {e}")
    raise

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GeminiChartGenerator:
    """
    Generate AI-powered chart visualizations using Google Gemini + matplotlib
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini client
        
        Args:
            api_key: Google Gemini API key (reads from env if not provided)
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-3-pro-image-preview')
            logger.info("Gemini client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            raise
    
    def create_chart_prompt(
        self,
        chart_type: str,
        data_summary: str,
        title: str,
        additional_context: Optional[str] = None
    ) -> str:
        """
        Create detailed prompt for AI chart generation
        
        Args:
            chart_type: Type of chart (bar, line, pie, scatter, etc.)
            data_summary: Summary of data to visualize
            title: Chart title
            additional_context: Any additional styling/context requirements
        
        Returns:
            Formatted prompt string
        """
        
        base_prompt = f"""
Create Python matplotlib code to generate a professional cricket analytics {chart_type}.

TITLE: {title}

DATA TO VISUALIZE:
{data_summary}

REQUIREMENTS:
1. Use cricket-themed colors: green (#00a67e), blue (#1e3a8a), orange (#f97316)
2. Figure size: (12, 7)
3. Include proper labels, title, legend
4. Professional styling with grid
5. Clear data labels on bars/points
6. Save to BytesIO buffer

CODE STRUCTURE (use exactly this):
```python
import matplotlib.pyplot as plt
import numpy as np
import io

fig, ax = plt.subplots(figsize=(12, 7))

# Your chart creation code here
# Example data arrays and plotting

ax.set_title('{title}', fontsize=16, fontweight='bold', pad=20)
ax.set_xlabel('X Label', fontsize=12)
ax.set_ylabel('Y Label', fontsize=12)
ax.grid(True, alpha=0.3)
ax.legend()

plt.tight_layout()
buf = io.BytesIO()
plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='white')
buf.seek(0)
plt.close()
```
"""
        
        if additional_context:
            base_prompt += f"\n\nADDITIONAL CONTEXT:\n{additional_context}"
        
        base_prompt += "\n\nGenerate ONLY the Python code, no explanations. Start with ```python"
        
        return base_prompt
    
    def generate_chart(
        self,
        chart_type: str,
        data_summary: str,
        title: str,
        additional_context: Optional[str] = None,
        model: str = "gemini-3-pro-image-preview"
    ) -> PIL.Image.Image:
        """
        Generate AI chart visualization
        
        Args:
            chart_type: Type of chart to generate
            data_summary: Data description
            title: Chart title
            additional_context: Additional requirements
            model: Gemini model to use (not used, kept for compatibility)
        
        Returns:
            PIL Image object
        """
        
        try:
            # Create prompt
            prompt = self.create_chart_prompt(
                chart_type=chart_type,
                data_summary=data_summary,
                title=title,
                additional_context=additional_context
            )
            
            logger.info(f"Generating {chart_type} chart: {title}")
            
            # Call Gemini API
            response = self.model.generate_content(prompt)
            code = response.text
            
            # Extract code from markdown
            if "```python" in code:
                code = code.split("```python")[1].split("```")[0]
            elif "```" in code:
                code = code.split("```")[1].split("```")[0]
            
            code = code.strip()
            
            logger.info("Executing generated code...")
            
            # Execute the code safely
            namespace = {
                'plt': plt,
                'io': io,
                'np': __import__('numpy')
            }
            
            exec(code, namespace)
            
            # Get the buffer from namespace
            if 'buf' in namespace:
                buf = namespace['buf']
                image = PIL.Image.open(buf)
                logger.info("Chart generated successfully!")
                return image
            else:
                raise ValueError("Code didn't create 'buf' variable")
            
        except Exception as e:
            logger.error(f"Chart generation failed: {e}")
            logger.info("Falling back to simple chart...")
            # Return fallback chart
            return self._create_fallback_chart(title, str(e))
    
    def _create_fallback_chart(self, title: str, error: str = "") -> PIL.Image.Image:
        """
        Create a simple fallback chart when AI generation fails
        
        Args:
            title: Chart title
            error: Error message to display
        
        Returns:
            PIL Image object
        """
        logger.info("Creating fallback chart")
        
        fig, ax = plt.subplots(figsize=(12, 7))
        
        # Create a simple placeholder
        ax.text(0.5, 0.6, f'🏏 {title}',
                ha='center', va='center', fontsize=20, fontweight='bold')
        
        ax.text(0.5, 0.4, 'AI Chart Generation',
                ha='center', va='center', fontsize=16, color='#00a67e')
        
        if error:
            error_short = error[:100] + "..." if len(error) > 100 else error
            ax.text(0.5, 0.2, f'Note: {error_short}',
                    ha='center', va='center', fontsize=10, color='#dc2626', wrap=True)
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='white')
        buf.seek(0)
        plt.close()
        
        return PIL.Image.open(buf)
    
    def generate_comparison_chart(
        self,
        team1: str,
        team2: str,
        metrics: Dict[str, tuple],
        title: str
    ) -> PIL.Image.Image:
        """
        Generate team comparison chart
        
        Args:
            team1: First team name
            team2: Second team name
            metrics: Dict of {metric_name: (team1_value, team2_value)}
            title: Chart title
        
        Returns:
            PIL Image object
        """
        
        data_summary = f"Team Comparison: {team1} vs {team2}\n\n"
        for metric, (val1, val2) in metrics.items():
            data_summary += f"- {metric}: {team1} = {val1}, {team2} = {val2}\n"
        
        return self.generate_chart(
            chart_type="grouped bar chart",
            data_summary=data_summary,
            title=title,
            additional_context=f"Show side-by-side bars for {team1} and {team2}"
        )
    
    def generate_player_performance_chart(
        self,
        player_name: str,
        performance_data: Dict[str, Any],
        chart_type: str = "line chart"
    ) -> PIL.Image.Image:
        """
        Generate player performance trend chart
        
        Args:
            player_name: Player name
            performance_data: Performance metrics over time
            chart_type: Type of chart
        
        Returns:
            PIL Image object
        """
        
        data_summary = f"Player: {player_name}\n\n"
        for metric, values in performance_data.items():
            data_summary += f"{metric}: {values}\n"
        
        return self.generate_chart(
            chart_type=chart_type,
            data_summary=data_summary,
            title=f"{player_name} - Performance Trend",
            additional_context="Show progression over matches/time"
        )
    
    def save_chart(self, image: PIL.Image.Image, filename: str, output_dir: Optional[Path] = None):
        """
        Save generated chart to file
        
        Args:
            image: PIL Image object
            filename: Output filename
            output_dir: Output directory (defaults to data/ai_charts/)
        """
        
        if output_dir is None:
            output_dir = Path(__file__).parent.parent / "data" / "ai_charts"
        
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / filename
        
        try:
            image.save(output_path, format='PNG', quality=95)
            logger.info(f"Chart saved to {output_path}")
        except Exception as e:
            logger.error(f"Failed to save chart: {e}")
            raise


# Convenience function
def get_chart_generator() -> GeminiChartGenerator:
    """Get initialized chart generator"""
    return GeminiChartGenerator()


# Example usage
if __name__ == "__main__":
    # Test chart generation
    try:
        generator = get_chart_generator()
        
        # Example: Team comparison
        test_chart = generator.generate_comparison_chart(
            team1="Mumbai Indians",
            team2="Chennai Super Kings",
            metrics={
                "Matches Won": (8, 7),
                "Average Score": (175, 168),
                "Win Rate": (53, 47)
            },
            title="MI vs CSK - IPL 2024 Comparison"
        )
        
        generator.save_chart(test_chart, "test_comparison.png")
        print("✅ Test chart generated successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
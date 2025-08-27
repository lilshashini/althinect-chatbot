import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from typing import Optional, Tuple, List, Any
from src.logger import setup_logger

logger = setup_logger(__name__)

class ChartBuilder:
    def __init__(self):
        self.chart_config = {
            'height': 600,
            'margin': dict(l=60, r=50, t=80, b=100)
        }
    
    def create_chart(self, data: List[List[Any]], columns: List[str], 
                    chart_type: str, user_query: str) -> Optional[go.Figure]:
        """Create appropriate chart based on data and user request"""
        try:
            df = pd.DataFrame(data, columns=columns)
            
            if df.empty:
                st.warning("No data available for visualization")
                return None
            
            # Detect column types and create appropriate chart
            if chart_type == 'bar':
                return self._create_bar_chart(df, user_query)
            elif chart_type == 'line':
                return self._create_line_chart(df, user_query)
            elif chart_type == 'pie':
                return self._create_pie_chart(df, user_query)
            
        except Exception as e:
            logger.error(f"Chart creation failed: {e}")
            st.error(f"Visualization error: {e}")
            return None
    
    def _create_bar_chart(self, df: pd.DataFrame, user_query: str) -> go.Figure:
        """Create bar chart with smart column detection"""
        # Your existing bar chart logic
        pass
    
    def _create_line_chart(self, df: pd.DataFrame, user_query: str) -> go.Figure:
        """Create line chart for time series data"""
        # Your existing line chart logic
        pass
    
    def _create_pie_chart(self, df: pd.DataFrame, user_query: str) -> go.Figure:
        """Create pie chart for categorical data"""
        # Your existing pie chart logic
        pass
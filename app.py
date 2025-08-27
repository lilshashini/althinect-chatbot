import streamlit as st
from src.session_manager import SessionManager
from src.db_client import ClickHouseClient
from src.parsers import QueryParser
from src.sql_builder import SQLBuilder
from src.llm_client import LLMClient
from src.visualizer import ChartBuilder
from src.logger import setup_logger

logger = setup_logger(__name__)

class ProductionAnalyticsBot:
    def __init__(self):
        self.db_client = ClickHouseClient()
        self.query_parser = QueryParser()
        self.sql_builder = SQLBuilder()
        self.llm_client = LLMClient()
        self.chart_builder = ChartBuilder()
        
    def process_query(self, user_query: str) -> str:
        """Main query processing pipeline"""
        try:
            # Parse query
            if self.query_parser.is_casual_query(user_query):
                return self._handle_casual_query(user_query)
            
            # Generate and execute SQL
            sql_query = self.llm_client.generate_sql(user_query, self.db_client.get_schema_info())
            data, columns = self.db_client.execute_query(sql_query)
            
            # Create visualization if needed
            needs_viz, chart_type = self.query_parser.detect_visualization_needs(user_query)
            if needs_viz:
                chart = self.chart_builder.create_chart(data, columns, chart_type, user_query)
                if chart:
                    st.plotly_chart(chart, use_container_width=True)
            
            # Generate response
            return self.llm_client.generate_response(user_query, data)
            
        except Exception as e:
            logger.error(f"Query processing failed: {e}")
            return f"An error occurred: {e}"

def main():
    st.set_page_config(page_title="Althinect Intelligence Bot", page_icon="📊")
    st.title("Althinect Intelligence Bot")
    
    # Initialize session management
    SessionManager.initialize_sessions()
    
    # Initialize bot
    if "bot" not in st.session_state:
        st.session_state.bot = ProductionAnalyticsBot()
    
    # UI components
    with st.sidebar:

        if "client" in st.session_state:
            st.success("🟢 Database Connected")
        else:
            st.warning("🔴 Database Not Connected")    



        st.header("Chat Sessions")
        if st.button("New Chat"):
            SessionManager.create_new_session()
    
    # Chat interface
    # ... rest of your UI logic
    
if __name__ == "__main__":
    main()
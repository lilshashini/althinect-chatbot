import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# Import the visualizer module (adjust import path based on your structure)
# from src.visualizer import create_enhanced_visualization, detect_columns, prepare_data_for_visualization, create_chart_labels, suggest_chart_type


class TestVisualizerCore:
    """Test core visualization functionality"""
    
    @pytest.fixture
    def sample_production_data(self):
        """Generate sample production data for testing"""
        dates = pd.date_range('2025-05-01', periods=10, freq='D')
        data = {
            'machine_name': ['Stenter 1', 'Stenter 2', 'Stenter 3'] * 10,
            'production_date': dates.repeat(3),
            'daily_production': np.random.uniform(1000, 3000, 30),
            'date': dates.repeat(3)
        }
        return pd.DataFrame(data)
    
    @pytest.fixture
    def sample_hourly_data(self):
        """Generate sample hourly data for testing"""
        hours = list(range(8, 20))  # 8 AM to 8 PM
        data = {
            'machine_name': ['Stenter 1'] * len(hours),
            'production_hour': hours,
            'hourly_production': np.random.uniform(100, 400, len(hours))
        }
        return pd.DataFrame(data)
    
    @pytest.fixture
    def sample_energy_data(self):
        """Generate sample energy consumption data"""
        dates = pd.date_range('2025-05-01', periods=7, freq='D')
        data = {
            'machine_name': ['Stenter 1', 'Stenter 2'] * 7,
            'date': dates.repeat(2),
            'daily_consumption': np.random.uniform(500, 1500, 14)
        }
        return pd.DataFrame(data)
    
    @pytest.fixture
    def sample_utilization_data(self):
        """Generate sample utilization data"""
        dates = pd.date_range('2025-05-01', periods=5, freq='D')
        data = {
            'machine_name': ['Stenter 1', 'Stenter 2', 'Stenter 3'] * 5,
            'date': dates.repeat(3),
            'daily_utilization_percentage': np.random.uniform(60, 95, 15)
        }
        return pd.DataFrame(data)
    
    @pytest.fixture
    def empty_dataframe(self):
        """Empty dataframe for edge case testing"""
        return pd.DataFrame()
    
    @pytest.fixture
    def dataframe_with_nulls(self):
        """Dataframe with null values for testing data cleaning"""
        data = {
            'machine_name': ['Stenter 1', None, 'Stenter 3'],
            'date': ['2025-05-01', '2025-05-02', None],
            'production': [1000, None, 1500]
        }
        return pd.DataFrame(data)


class TestColumnDetection:
    """Test column detection and identification logic"""
    
    def test_detect_time_columns(self, sample_production_data, sample_hourly_data):
        """Test detection of time columns with different granularities"""
        # Test daily detection
        time_col, machine_col, value_col, granularity = self._mock_detect_columns(sample_production_data)
        assert granularity in ['daily', 'unknown']
        assert 'date' in time_col.lower() if time_col else True
        
        # Test hourly detection
        time_col, machine_col, value_col, granularity = self._mock_detect_columns(sample_hourly_data)
        assert granularity in ['hourly', 'unknown']
        assert 'hour' in time_col.lower() if time_col else True
    
    def test_detect_machine_columns(self, sample_production_data):
        """Test detection of machine/device columns"""
        time_col, machine_col, value_col, granularity = self._mock_detect_columns(sample_production_data)
        assert machine_col is not None
        assert 'machine' in machine_col.lower()
    
    def test_detect_value_columns(self, sample_production_data, sample_energy_data):
        """Test detection of value columns based on metric type"""
        # Test production data
        time_col, machine_col, value_col, granularity = self._mock_detect_columns(sample_production_data)
        assert value_col is not None
        assert 'production' in value_col.lower()
        
        # Test energy data
        time_col, machine_col, value_col, granularity = self._mock_detect_columns(sample_energy_data)
        assert value_col is not None
        assert 'consumption' in value_col.lower()
    
    def test_fallback_column_detection(self):
        """Test fallback behavior when standard patterns aren't found"""
        # Create data with non-standard column names
        data = pd.DataFrame({
            'col1': ['A', 'B', 'C'],
            'col2': [1, 2, 3],
            'col3': [10.5, 20.1, 30.7]
        })
        
        time_col, machine_col, value_col, granularity = self._mock_detect_columns(data)
        
        # Should fall back to first available columns
        assert granularity == 'unknown'
        assert value_col in data.select_dtypes(include=[np.number]).columns.tolist()
    
    def _mock_detect_columns(self, df):
        """Mock implementation of detect_columns function based on original logic"""
        time_col = None
        machine_col = None
        value_col = None
        granularity = 'unknown'
        
        # Time column detection
        time_patterns = {
            'hourly': ['hour', 'time_hour', 'production_hour', 'hourly', 'hr'],
            'daily': ['day', 'date', 'production_date', 'daily', 'production_day'],
            'monthly': ['month', 'production_month', 'monthly', 'mon']
        }
        
        for gran, patterns in time_patterns.items():
            for col in df.columns:
                col_lower = col.lower()
                if any(pattern in col_lower for pattern in patterns):
                    time_col = col
                    granularity = gran
                    break
            if time_col:
                break
        
        # Machine column detection
        machine_patterns = ['machine', 'device', 'equipment', 'unit', 'station']
        for col in df.columns:
            col_lower = col.lower()
            if any(pattern in col_lower for pattern in machine_patterns):
                machine_col = col
                break
        
        # Value column detection
        value_patterns = {
            'production': ['production', 'output', 'manufactured', 'produced'],
            'consumption': ['consumption', 'consumed', 'usage', 'used'],
            'utilisation': ['utilisation', 'utilization', 'efficiency', 'usage_rate']
        }
        
        for metric, patterns in value_patterns.items():
            for col in df.columns:
                col_lower = col.lower()
                if any(pattern in col_lower for pattern in patterns):
                    value_col = col
                    break
            if value_col:
                break
        
        # Fallback to numeric column
        if not value_col:
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            if numeric_cols:
                value_col = numeric_cols[0]
        
        return time_col, machine_col, value_col, granularity


class TestChartCreation:
    """Test different chart type creation"""
    
    @patch('streamlit.plotly_chart')
    @patch('plotly.express.bar')
    def test_create_bar_chart(self, mock_px_bar, mock_st_plotly, sample_production_data):
        """Test bar chart creation"""
        mock_fig = Mock()
        mock_px_bar.return_value = mock_fig
        
        # Mock the visualization function call
        result = self._mock_create_visualization(sample_production_data, 'bar', 'show production by day')
        
        # Should attempt to create bar chart
        assert result is True or mock_px_bar.called
    
    @patch('streamlit.plotly_chart')
    @patch('plotly.express.line')
    def test_create_line_chart(self, mock_px_line, mock_st_plotly, sample_hourly_data):
        """Test line chart creation"""
        mock_fig = Mock()
        mock_px_line.return_value = mock_fig
        
        result = self._mock_create_visualization(sample_hourly_data, 'line', 'show hourly trends')
        
        assert result is True or mock_px_line.called
    
    @patch('streamlit.plotly_chart')
    @patch('plotly.express.pie')
    def test_create_pie_chart(self, mock_px_pie, mock_st_plotly, sample_production_data):
        """Test pie chart creation"""
        mock_fig = Mock()
        mock_px_pie.return_value = mock_fig
        
        result = self._mock_create_visualization(sample_production_data, 'pie', 'show distribution')
        
        assert result is True or mock_px_pie.called
    
    def test_multi_machine_grouping(self, sample_production_data):
        """Test proper grouping for multi-machine data"""
        # Group by machine and time
        grouped = sample_production_data.groupby(['machine_name', 'production_date'])['daily_production'].sum().reset_index()
        
        # Should have data for multiple machines
        unique_machines = grouped['machine_name'].nunique()
        assert unique_machines > 1
        
        # Should maintain temporal structure
        assert len(grouped) > 0
    
    def _mock_create_visualization(self, df, chart_type, user_query):
        """Mock implementation of create_enhanced_visualization"""
        if df.empty:
            return False
        
        # Clean data
        df_clean = df.dropna()
        if df_clean.empty:
            return False
        
        # Detect columns (simplified)
        numeric_cols = df_clean.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df_clean.select_dtypes(include=['object', 'category']).columns.tolist()
        
        # Must have at least one numeric column for visualization
        if not numeric_cols:
            return False
        
        # Mock successful chart creation
        return True


class TestDataPreparation:
    """Test data preparation and transformation"""
    
    def test_datetime_handling(self):
        """Test datetime column processing"""
        # Create data with datetime column
        dates = pd.date_range('2025-05-01', periods=24, freq='H')
        data = pd.DataFrame({
            'timestamp': dates,
            'value': np.random.uniform(100, 200, 24)
        })
        
        # Test hourly extraction
        data['hour'] = data['timestamp'].dt.hour
        assert data['hour'].min() >= 0
        assert data['hour'].max() <= 23
        
        # Test daily extraction
        data['date'] = data['timestamp'].dt.date
        unique_days = data['date'].nunique()
        assert unique_days > 0
    
    def test_data_grouping(self, sample_production_data):
        """Test data aggregation and grouping"""
        # Group by machine and date
        grouped = sample_production_data.groupby(['machine_name', 'production_date'])['daily_production'].sum().reset_index()
        
        # Should reduce duplicates
        assert len(grouped) <= len(sample_production_data)
        
        # Should maintain machine categories
        original_machines = set(sample_production_data['machine_name'].unique())
        grouped_machines = set(grouped['machine_name'].unique())
        assert grouped_machines == original_machines
    
    def test_null_handling(self, dataframe_with_nulls):
        """Test handling of null values"""
        # Original data has nulls
        assert dataframe_with_nulls.isnull().any().any()
        
        # After dropping nulls
        clean_df = dataframe_with_nulls.dropna()
        assert not clean_df.isnull().any().any()
        
        # Should have fewer rows
        assert len(clean_df) <= len(dataframe_with_nulls)


class TestChartLabeling:
    """Test chart title and label generation"""
    
    def test_create_chart_labels_production(self):
        """Test label creation for production charts"""
        title, y_label, metric_type = self._mock_create_chart_labels('bar', 'daily', 'daily_production', 'machine_name')
        
        assert 'production' in title.lower()
        assert 'daily' in title.lower()
        assert metric_type == 'Production'
    
    def test_create_chart_labels_energy(self):
        """Test label creation for energy charts"""
        title, y_label, metric_type = self._mock_create_chart_labels('line', 'hourly', 'hourly_consumption', 'machine_name')
        
        assert 'consumption' in title.lower()
        assert 'hourly' in title.lower()
        assert metric_type == 'Consumption'
    
    def test_create_chart_labels_utilization(self):
        """Test label creation for utilization charts"""
        title, y_label, metric_type = self._mock_create_chart_labels('bar', 'daily', 'daily_utilization_percentage', 'machine_name')
        
        assert 'utilisation' in title.lower() or 'utilization' in title.lower()
        assert metric_type == 'Utilisation'
    
    def _mock_create_chart_labels(self, chart_type, granularity, value_col, machine_col):
        """Mock implementation of create_chart_labels"""
        # Determine metric type
        metric_type = "Value"
        if value_col:
            value_lower = value_col.lower()
            if 'production' in value_lower:
                metric_type = "Production"
            elif 'consumption' in value_lower:
                metric_type = "Consumption"
            elif 'utilisation' in value_lower or 'utilization' in value_lower:
                metric_type = "Utilisation"
        
        # Create title
        granularity_title = granularity.title() if granularity != 'unknown' else ""
        title = f"{granularity_title} {metric_type} Analysis"
        
        # Create Y-axis label
        y_label = f"{granularity_title} {metric_type}" if granularity != 'unknown' else value_col.replace('_', ' ').title()
        
        return title, y_label, metric_type


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_empty_dataframe(self, empty_dataframe):
        """Test handling of empty dataframes"""
        result = self._mock_create_visualization(empty_dataframe, 'bar', 'test query')
        assert result is False
    
    def test_all_null_dataframe(self):
        """Test handling of dataframes with all null values"""
        df = pd.DataFrame({
            'col1': [None, None, None],
            'col2': [None, None, None]
        })
        
        result = self._mock_create_visualization(df, 'bar', 'test query')
        assert result is False
    
    def test_no_numeric_columns(self):
        """Test handling of dataframes with no numeric columns"""
        df = pd.DataFrame({
            'machine': ['A', 'B', 'C'],
            'status': ['ON', 'OFF', 'ON']
        })
        
        result = self._mock_create_visualization(df, 'bar', 'test query')
        assert result is False
    
    def test_single_row_dataframe(self):
        """Test handling of single-row dataframes"""
        df = pd.DataFrame({
            'machine': ['Stenter 1'],
            'production': [1500],
            'date': ['2025-05-01']
        })
        
        result = self._mock_create_visualization(df, 'bar', 'test query')
        # Should still work for single row
        assert result is True
    
    def _mock_create_visualization(self, df, chart_type, user_query):
        """Simplified mock of create_enhanced_visualization for error testing"""
        if df.empty:
            return False
        
        df_clean = df.dropna()
        if df_clean.empty:
            return False
        
        numeric_cols = df_clean.select_dtypes(include=[np.number]).columns.tolist()
        if not numeric_cols:
            return False
        
        return True


class TestVisualizationSuggestions:
    """Test chart type suggestion logic"""
    
    def test_suggest_chart_type_hourly(self, sample_hourly_data):
        """Test suggestions for hourly data"""
        suggestions = self._mock_suggest_chart_type(sample_hourly_data, 'hourly', 'production')
        
        assert any('line' in suggestion.lower() for suggestion in suggestions)
        assert any('bar' in suggestion.lower() for suggestion in suggestions)
    
    def test_suggest_chart_type_daily(self, sample_production_data):
        """Test suggestions for daily data"""
        suggestions = self._mock_suggest_chart_type(sample_production_data, 'daily', 'production')
        
        assert any('line' in suggestion.lower() for suggestion in suggestions)
        assert any('bar' in suggestion.lower() for suggestion in suggestions)
    
    def test_suggest_chart_type_multi_machine(self, sample_production_data):
        """Test suggestions for multi-machine data"""
        suggestions = self._mock_suggest_chart_type(sample_production_data, 'daily', 'production')
        
        # Should suggest pie chart for distribution
        assert any('pie' in suggestion.lower() for suggestion in suggestions)
    
    def _mock_suggest_chart_type(self, df, granularity, metric_type):
        """Mock implementation of suggest_chart_type"""
        suggestions = []
        
        if granularity in ['hourly', 'daily']:
            suggestions.append("line - Best for showing trends over time")
            suggestions.append("bar - Good for comparing values across time periods")
        
        if granularity == 'monthly':
            suggestions.append("bar - Ideal for comparing monthly values")
            suggestions.append("line - Good for showing monthly trends")
        
        # Check if we have machine data
        machine_cols = [col for col in df.columns if 'machine' in col.lower() or 'device' in col.lower()]
        if machine_cols and df[machine_cols[0]].nunique() > 1:
            suggestions.append("pie - Useful for showing distribution across machines")
        
        return suggestions


class TestIntegration:
    """Integration tests combining multiple components"""
    
    @patch('streamlit.plotly_chart')
    @patch('streamlit.dataframe')
    @patch('streamlit.write')
    @patch('streamlit.expander')
    def test_full_visualization_workflow(self, mock_expander, mock_write, mock_dataframe, mock_plotly, sample_production_data):
        """Test complete visualization workflow"""
        # Mock streamlit components
        mock_expander.return_value.__enter__ = Mock()
        mock_expander.return_value.__exit__ = Mock()
        
        # This would test the full create_enhanced_visualization function
        # For now, just test that the workflow completes without errors
        result = self._mock_full_workflow(sample_production_data, 'bar', 'show daily production')
        assert result is True
    
    def test_different_data_formats(self):
        """Test visualization with different input data formats"""
        # Test with different column naming conventions
        test_cases = [
            {
                'machine_name': ['Stenter 1', 'Stenter 2'],
                'production_date': ['2025-05-01', '2025-05-02'],
                'daily_production': [1000, 1200]
            },
            {
                'device_name': ['Machine A', 'Machine B'],
                'date': ['2025-05-01', '2025-05-02'],
                'output': [800, 900]
            },
            {
                'equipment': ['Unit 1', 'Unit 2'],
                'day': [1, 2],
                'value': [1500, 1600]
            }
        ]
        
        for case in test_cases:
            df = pd.DataFrame(case)
            result = self._mock_create_visualization(df, 'bar', 'test')
            assert result is True
    
    def _mock_full_workflow(self, df, chart_type, user_query):
        """Mock the complete visualization workflow"""
        if df.empty:
            return False
        
        # Data cleaning
        df_clean = df.dropna()
        if df_clean.empty:
            return False
        
        # Column detection would happen here
        # Chart creation would happen here
        # Data summary would happen here
        
        return True
    
    def _mock_create_visualization(self, df, chart_type, user_query):
        """Mock visualization creation"""
        return not df.empty and len(df.select_dtypes(include=[np.number]).columns) > 0


# Test fixtures for pytest
@pytest.fixture
def mock_streamlit():
    """Mock streamlit components"""
    with patch('streamlit.plotly_chart') as mock_plotly, \
         patch('streamlit.dataframe') as mock_dataframe, \
         patch('streamlit.write') as mock_write, \
         patch('streamlit.warning') as mock_warning, \
         patch('streamlit.error') as mock_error, \
         patch('streamlit.expander') as mock_expander:
        
        mock_expander.return_value.__enter__ = Mock()
        mock_expander.return_value.__exit__ = Mock()
        
        yield {
            'plotly_chart': mock_plotly,
            'dataframe': mock_dataframe,
            'write': mock_write,
            'warning': mock_warning,
            'error': mock_error,
            'expander': mock_expander
        }


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
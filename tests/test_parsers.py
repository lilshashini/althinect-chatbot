import pytest
import sys
import os
from datetime import datetime, timedelta

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from parsers import (
    detect_query_type,
    extract_machine_numbers,
    detect_multi_metric_query,
    extract_date_range,
    detect_query_intent,
    is_greeting_or_casual
)


class TestQueryTypeDetection:
    """Test query type classification"""
    
    def test_production_query_detection(self):
        """Test detection of production-related queries"""
        test_cases = [
            ("show me daily production", "production"),
            ("what's the fabric length output", "production"),
            ("how much did we produce yesterday", "production"),
            ("production report for stenter 1", "production"),
        ]
        
        for query, expected in test_cases:
            assert detect_query_type(query) == expected
    
    def test_energy_query_detection(self):
        """Test detection of energy-related queries"""
        test_cases = [
            ("show energy consumption", "energy"),
            ("power usage for all machines", "energy"),
            ("total energy consumed", "energy"),
        ]
        
        for query, expected in test_cases:
            assert detect_query_type(query) == expected
    
    def test_utilization_query_detection(self):
        """Test detection of utilization-related queries"""
        test_cases = [
            ("machine utilization report", "utilization"),
            ("efficiency of stenter 5", "utilization"),
            ("uptime analysis", "utilization"),
            ("status and downtime", "utilization"),
        ]
        
        for query, expected in test_cases:
            assert detect_query_type(query) == expected
    
    def test_default_fallback(self):
        """Test default fallback to production"""
        unclear_queries = [
            "show me data",
            "generate report",
            "machine performance"
        ]
        
        for query in unclear_queries:
            assert detect_query_type(query) == "production"


class TestMachineExtraction:
    """Test machine number extraction from queries"""
    
    def test_specific_machine_extraction(self):
        """Test extraction of specific machine numbers"""
        test_cases = [
            ("show stenter 1 data", ["stenter1"]),
            ("stenter 3 and stenter 5 production", ["stenter3", "stenter5"]),
            ("performance of stenter 09", ["stenter09"]),
            ("stenter1 vs stenter2", ["stenter1", "stenter2"]),
        ]
        
        for query, expected in test_cases:
            result = extract_machine_numbers(query)
            assert result == expected
    
    def test_all_machines_detection(self):
        """Test detection of 'all machines' requests"""
        test_cases = [
            "show all machines production",
            "all stenters performance", 
            "every machine utilization",
            "each machine data"
        ]
        
        for query in test_cases:
            result = extract_machine_numbers(query)
            # Should return all available machines
            assert len(result) > 1
            assert "stenter1" in result
            assert "stenter9" in result
    
    def test_no_machines_specified(self):
        """Test queries with no specific machines mentioned"""
        test_cases = [
            "show production data",
            "energy consumption report",
            "daily performance"
        ]
        
        for query in test_cases:
            result = extract_machine_numbers(query)
            assert result == []


class TestMultiMetricDetection:
    """Test multi-metric query detection"""
    
    def test_multi_metric_detection(self):
        """Test detection of queries asking for multiple metrics"""
        test_cases = [
            ("production and energy consumption", True, ["production", "energy"]),
            ("show utilization and production", True, ["production", "utilization"]),
            ("energy, production, and efficiency", True, ["production", "energy", "utilization"]),
        ]
        
        for query, expected_multi, expected_metrics in test_cases:
            is_multi, metrics = detect_multi_metric_query(query)
            assert is_multi == expected_multi
            for metric in expected_metrics:
                assert metric in metrics
    
    def test_single_metric_detection(self):
        """Test detection of single metric queries"""
        test_cases = [
            "show production data",
            "energy consumption report",
            "machine utilization only"
        ]
        
        for query in test_cases:
            is_multi, metrics = detect_multi_metric_query(query)
            assert is_multi == False
            assert len(metrics) <= 1


class TestDateRangeExtraction:
    """Test date range extraction from queries"""
    
    def test_month_detection(self):
        """Test month name detection"""
        test_cases = [
            ("production in april", ("2025-04-01", "2025-04-30")),
            ("march data", ("2025-03-01", "2025-03-31")),
            ("may report", ("2025-05-01", "2025-05-31")),
        ]
        
        for query, expected in test_cases:
            result = extract_date_range(query)
            assert result == expected
    
    def test_relative_date_detection(self):
        """Test relative date expressions"""
        query = "last 7 days production"
        start_date, end_date = extract_date_range(query)
        
        # Parse the returned dates
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
        
        # Check if it's approximately 7 days range
        diff = (end - start).days
        assert diff == 7
    
    def test_default_current_month(self):
        """Test default to current month"""
        query = "show production"
        start_date, end_date = extract_date_range(query)
        
        # Should default to current month
        now = datetime.now()
        expected_start = now.replace(day=1).strftime('%Y-%m-%d')
        
        assert start_date == expected_start


class TestQueryIntentDetection:
    """Test overall query intent detection"""
    
    def test_daily_production_intent(self):
        """Test daily production query intent"""
        queries = [
            "daily production for stenter 1",
            "production by day",
            "show production each day"
        ]
        
        for query in queries:
            intent, date_range, query_type = detect_query_intent(query)
            assert intent == "daily_production"
            assert query_type == "production"
            assert date_range is not None
    
    def test_hourly_production_intent(self):
        """Test hourly production query intent"""
        queries = [
            "hourly production data",
            "production by hour",
            "hour production analysis"
        ]
        
        for query in queries:
            intent, date_range, query_type = detect_query_intent(query)
            assert intent == "hourly_production"
            assert query_type == "production"
    
    def test_multi_metric_intent(self):
        """Test multi-metric query intent"""
        query = "show production and energy consumption daily"
        intent, date_range, query_type = detect_query_intent(query)
        assert intent == "multi_metric_daily"
        assert query_type == "multi_metric"


class TestGreetingDetection:
    """Test greeting and casual conversation detection"""
    
    def test_greeting_detection(self):
        """Test detection of greetings"""
        greetings = [
            "hello",
            "hi there",
            "good morning",
            "hey",
            "good afternoon"
        ]
        
        for greeting in greetings:
            assert is_greeting_or_casual(greeting) == True
    
    def test_casual_phrases(self):
        """Test detection of casual phrases"""
        casual = [
            "thank you",
            "thanks",
            "ok",
            "cool",
            "help"
        ]
        
        for phrase in casual:
            assert is_greeting_or_casual(phrase) == True
    
    def test_data_queries_not_casual(self):
        """Test that data queries are not classified as casual"""
        data_queries = [
            "show production data",
            "machine performance in april",
            "energy consumption chart",
            "daily output report"
        ]
        
        for query in data_queries:
            assert is_greeting_or_casual(query) == False


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_empty_query(self):
        """Test handling of empty queries"""
        assert detect_query_type("") == "production"
        assert extract_machine_numbers("") == []
        assert is_greeting_or_casual("") == True
    
    def test_very_long_query(self):
        """Test handling of very long queries"""
        long_query = "show me the daily production output for stenter machine number 1 " * 10
        result = detect_query_type(long_query)
        assert result == "production"
        
        machines = extract_machine_numbers(long_query)
        assert "stenter1" in machines
    
    def test_mixed_case_queries(self):
        """Test case insensitive parsing"""
        queries = [
            "SHOW PRODUCTION DATA",
            "Show Energy Consumption", 
            "sHoW uTiLiZaTiOn"
        ]
        
        expected_types = ["production", "energy", "utilization"]
        
        for query, expected in zip(queries, expected_types):
            assert detect_query_type(query) == expected
    
    def test_special_characters(self):
        """Test handling of special characters and numbers"""
        query = "show stenter-1 & stenter_2 production: 2025/04/01 - 2025/04/30"
        machines = extract_machine_numbers(query)
        # Should still detect machines despite special formatting
        assert len(machines) >= 1
        
        query_type = detect_query_type(query)
        assert query_type == "production"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
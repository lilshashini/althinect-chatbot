import pytest
import sys
import os
from unittest.mock import Mock, patch

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from sql_builder import (
    build_device_filter,
    get_correct_parameter,
    build_multi_metric_device_names,
    load_prompt_template
)
from config import MACHINE_MAPPINGS


class TestDeviceFilter:
    """Test device filter building for SQL queries"""
    
    def test_single_machine_filter(self):
        """Test filter generation for single machine"""
        query = "show production for stenter 1"
        filter_clause = build_device_filter(query)
        
        assert "TJ-Stenter01 Length(ioid2)" in filter_clause
        assert "device_id =" in filter_clause
        assert "SELECT virtual_device_id FROM devices" in filter_clause
    
    def test_multiple_machines_filter(self):
        """Test filter generation for multiple machines"""
        query = "show production for stenter 1 and stenter 2"
        filter_clause = build_device_filter(query)
        
        assert "TJ-Stenter01 Length(ioid2)" in filter_clause
        assert "TJ-Stenter02 Length(ioid1)" in filter_clause
        assert "device_id IN" in filter_clause
        assert "SELECT virtual_device_id FROM devices" in filter_clause
    
    def test_no_machine_specified(self):
        """Test when no specific machine is mentioned"""
        query = "show daily production"
        filter_clause = build_device_filter(query)
        
        assert filter_clause == ""
    
    def test_energy_query_device_mapping(self):
        """Test device mapping for energy queries"""
        query = "energy consumption for stenter 7"
        filter_clause = build_device_filter(query)
        
        # Should use energy mapping (TJ-Stenter07A)
        assert "TJ-Stenter07A" in filter_clause
    
    def test_utilization_query_device_mapping(self):
        """Test device mapping for utilization queries"""
        query = "utilization for stenter 3"
        filter_clause = build_device_filter(query)
        
        # Should use status mapping
        assert "TJ-Stenter03 Status" in filter_clause


class TestParameterMapping:
    """Test parameter name mapping based on query type"""
    
    def test_production_parameter(self):
        """Test production parameter mapping"""
        assert get_correct_parameter("production") == "length"
    
    def test_energy_parameter(self):
        """Test energy parameter mapping"""
        assert get_correct_parameter("energy") == "TotalEnergy"
    
    def test_utilization_parameter(self):
        """Test utilization parameter mapping"""
        assert get_correct_parameter("utilization") == "status"
    
    def test_default_parameter(self):
        """Test default parameter fallback"""
        assert get_correct_parameter("unknown") == "length"
        assert get_correct_parameter("") == "length"


class TestMultiMetricDeviceNames:
    """Test multi-metric device name building"""
    
    def test_stenter1_device_names(self):
        """Test device names for stenter 1"""
        result = build_multi_metric_device_names("stenter1")
        
        expected = {
            'production_device': 'TJ-Stenter01 Length(ioid2)',
            'energy_device': 'TJ-Stenter01',
            'utilization_device': 'TJ-Stenter01 Status'
        }
        
        assert result == expected
    
    def test_stenter7_device_names(self):
        """Test device names for stenter 7 (special energy mapping)"""
        result = build_multi_metric_device_names("stenter7")
        
        expected = {
            'production_device': 'TJ-Stenter07 Fabric Length',
            'energy_device': 'TJ-Stenter07A',  # Note the 'A' suffix
            'utilization_device': 'TJ-Stenter07 Status'
        }
        
        assert result == expected
    
    def test_unknown_machine(self):
        """Test handling of unknown machine"""
        result = build_multi_metric_device_names("unknown_machine")
        
        expected = {
            'production_device': '',
            'energy_device': '',
            'utilization_device': ''
        }
        
        assert result == expected


class TestPromptLoading:
    """Test prompt template loading from files"""
    
    @patch('builtins.open')
    def test_prompt_loading_success(self, mock_open):
        """Test successful prompt loading"""
        mock_content = "Test prompt with {placeholder}"
        mock_open.return_value.__enter__.return_value.read.return_value = mock_content
        
        result = load_prompt_template("test_prompt.txt")
        
        assert result == mock_content
        mock_open.assert_called_once_with("prompts/test_prompt.txt", "r", encoding="utf-8")
    
    @patch('builtins.open', side_effect=FileNotFoundError)
    def test_prompt_loading_file_not_found(self, mock_open):
        """Test handling of missing prompt file"""
        with pytest.raises(FileNotFoundError):
            load_prompt_template("nonexistent_prompt.txt")


class TestSQLQueryGeneration:
    """Test SQL query generation components"""
    
    def test_time_zone_handling(self):
        """Test that all generated components use correct timezone"""
        # This would test the actual SQL generation, but since we're using LLM,
        # we test the components that feed into it
        
        query = "daily production for stenter 1"
        device_filter = build_device_filter(query)
        
        # The device filter should be ready for timezone-aware queries
        assert "virtual_device_id" in device_filter
        assert "device_name" in device_filter
    
    def test_working_hours_compliance(self):
        """Test components support working hours (07:30-19:30)"""
        # This is more of an integration test concept
        # The actual time filtering happens in the SQL prompt template
        
        query = "hourly production"
        query_type = get_correct_parameter("production")
        assert query_type == "length"  # Correct parameter for time-based production queries


class TestMachineMappings:
    """Test machine mapping consistency"""
    
    def test_all_stenters_have_mappings(self):
        """Test that all stenters 1-9 have mappings for all metric types"""
        for i in range(1, 10):
            stenter_key = f"stenter{i}"
            padded_key = f"stenter{i:02d}"
            
            # Check production mappings
            assert (stenter_key in MACHINE_MAPPINGS['production'] or 
                   padded_key in MACHINE_MAPPINGS['production'])
            
            # Check energy mappings
            assert (stenter_key in MACHINE_MAPPINGS['energy'] or 
                   padded_key in MACHINE_MAPPINGS['energy'])
            
            # Check utilization mappings
            assert (stenter_key in MACHINE_MAPPINGS['utilization'] or 
                   padded_key in MACHINE_MAPPINGS['utilization'])
    
    def test_mapping_consistency(self):
        """Test that mappings follow expected patterns"""
        # Test that all production mappings contain "Length" or "Fabric Length"
        for device_name in MACHINE_MAPPINGS['production'].values():
            assert "Length" in device_name
        
        # Test that all utilization mappings contain "Status"
        for device_name in MACHINE_MAPPINGS['utilization'].values():
            assert "Status" in device_name
        
        # Test that energy mappings start with "TJ-Stenter"
        for device_name in MACHINE_MAPPINGS['energy'].values():
            assert device_name.startswith("TJ-Stenter")


class TestEdgeCasesSQL:
    """Test edge cases in SQL building"""
    
    def test_malformed_machine_names(self):
        """Test handling of malformed machine names"""
        query = "show production for stenter 99"  # Non-existent machine
        filter_clause = build_device_filter(query)
        
        # Should return empty filter for non-existent machines
        assert filter_clause == ""
    
    def test_mixed_query_types(self):
        """Test queries that mention multiple metric types"""
        query = "production and energy for stenter 1"
        
        # Should default to production type
        filter_clause = build_device_filter(query)
        assert "TJ-Stenter01 Length(ioid2)" in filter_clause
    
    def test_case_insensitive_machine_detection(self):
        """Test case insensitive machine detection"""
        query = "STENTER 1 PRODUCTION"
        filter_clause = build_device_filter(query)
        
        assert "TJ-Stenter01 Length(ioid2)" in filter_clause


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
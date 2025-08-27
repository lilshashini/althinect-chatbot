import re
from typing import Tuple, List, Optional
from datetime import datetime, timedelta
from src.config import MACHINE_MAPPINGS
from src.logger import setup_logger

logger = setup_logger(__name__)

class QueryParser:
    def __init__(self):
        self.casual_patterns = [
            'hello', 'hi', 'hey', 'thank you', 'thanks', 'bye'
        ]
    
    def is_casual_query(self, query: str) -> bool:
        """Detect if query is casual conversation"""
        query_lower = query.lower().strip()
        return any(pattern in query_lower for pattern in self.casual_patterns)
    
    def detect_query_type(self, query: str) -> str:
        """Detect if query is about production, energy, or utilization"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['production', 'length', 'fabric length', 'output']):
            return 'production'
        elif any(word in query_lower for word in ['energy', 'consumption', 'power']):
            return 'energy'
        elif any(word in query_lower for word in ['utilization', 'efficiency', 'uptime', 'status']):
            return 'utilization'
        
        return 'production'  # default
    
    def extract_machine_numbers(self, query: str) -> List[str]:
        """Extract specific machine numbers from query"""
        query_lower = query.lower()
        stenter_matches = re.findall(r'stenter\s*(\d+)', query_lower)
        
        if stenter_matches:
            return [f'stenter{num}' for num in stenter_matches]
        
        if any(phrase in query_lower for phrase in ['all machines', 'all stenters']):
            return list(MACHINE_MAPPINGS['production'].keys())
        
        return []
    
    def extract_date_range(self, query: str) -> Tuple[str, str]:
        """Extract date range from query"""
        query_lower = query.lower()
        
        # Month mappings
        month_mappings = {
            'january': ('2025-01-01', '2025-01-31'),
            'february': ('2025-02-01', '2025-02-28'),
            'march': ('2025-03-01', '2025-03-31'),
            'april': ('2025-04-01', '2025-04-30'),
            'may': ('2025-05-01', '2025-05-31'),
        }
        
        for month, (start, end) in month_mappings.items():
            if month in query_lower:
                return start, end
        
        # Relative dates
        if any(phrase in query_lower for phrase in ['last 7 days', 'past week']):
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=7)
            return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')
        
        # Default to current month
        now = datetime.now()
        start_date = now.replace(day=1).strftime('%Y-%m-%d')
        end_date = now.strftime('%Y-%m-%d')
        return start_date, end_date
    
    def detect_visualization_needs(self, query: str) -> Tuple[bool, str]:
        """Detect if visualization is requested and what type"""
        query_lower = query.lower()
        
        viz_keywords = ['plot', 'chart', 'graph', 'visualize', 'show']
        needs_viz = any(keyword in query_lower for keyword in viz_keywords)
        
        # Chart type detection
        if 'line' in query_lower:
            chart_type = 'line'
        elif 'pie' in query_lower:
            chart_type = 'pie'
        elif 'bar' in query_lower:
            chart_type = 'bar'
        else:
            chart_type = 'bar'  # default
        
        return needs_viz, chart_type
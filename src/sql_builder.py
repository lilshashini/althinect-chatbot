from typing import Dict, List, Optional
from src.config import MACHINE_MAPPINGS, Config
from src.logger import setup_logger

logger = setup_logger(__name__)

class SQLBuilder:
    def __init__(self):
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, str]:
        """Load SQL templates"""
        # Move your METABASE_QUERY_TEMPLATES here
        return {
            'daily_production': """
            WITH device_lookup AS (
                SELECT virtual_device_id, device_name FROM devices
            ),
            production_calculation AS (
                -- Your existing template logic
            )
            SELECT * FROM production_calculation;
            """,
            # ... other templates
        }
    
    def build_device_filter(self, machines: List[str], query_type: str) -> str:
        """Build device filter clause"""
        if not machines:
            return ""
        
        machine_names = []
        for machine in machines:
            if machine in MACHINE_MAPPINGS[query_type]:
                machine_names.append(MACHINE_MAPPINGS[query_type][machine])
        
        if len(machine_names) == 1:
            return f"AND device_id = (SELECT virtual_device_id FROM devices WHERE device_name = '{machine_names[0]}')"
        else:
            machine_list = "', '".join(machine_names)
            return f"AND device_id IN (SELECT virtual_device_id FROM devices WHERE device_name IN ('{machine_list}'))"
    
    def build_query(self, template_name: str, **params) -> str:
        """Build SQL query from template"""
        if template_name not in self.templates:
            raise ValueError(f"Template {template_name} not found")
        
        try:
            return self.templates[template_name].format(**params)
        except KeyError as e:
            logger.error(f"Missing parameter for template {template_name}: {e}")
            raise
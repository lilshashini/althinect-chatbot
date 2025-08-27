from typing import List, Dict, Any, Optional
import clickhouse_connect
from src.config import Config
from src.logger import setup_logger

logger = setup_logger(__name__)

class ClickHouseClient:
    def __init__(self):
        self._client = None
    
    @property
    def client(self):
        if self._client is None:
            self._client = self._create_connection()
        return self._client
    
    def _create_connection(self):
        try:
            client = clickhouse_connect.get_client(
                host=Config.CLICKHOUSE_HOST,
                user=Config.CLICKHOUSE_USER,
                password=Config.CLICKHOUSE_PASSWORD,
                database=Config.CLICKHOUSE_DATABASE,
                secure=True
            )
            # Test connection
            client.query('SELECT 1')
            logger.info("ClickHouse connection established")
            return client
        except Exception as e:
            logger.error(f"Failed to connect to ClickHouse: {e}")
            raise
    
    def execute_query(self, query: str) -> List[List[Any]]:
        try:
            logger.info(f"Executing query: {query[:100]}...")
            result = self.client.query(query)
            logger.info(f"Query returned {len(result.result_set)} rows")
            return result.result_set, result.column_names
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
    
    def get_schema_info(self) -> Dict[str, Any]:
        """Get database schema information"""
        schema_query = """
        SELECT 
            table,
            name as column_name,
            type as column_type
        FROM system.columns 
        WHERE database = 'default'
        ORDER BY table, position
        """
        try:
            result, columns = self.execute_query(schema_query)
            return {"tables": result, "columns": columns}
        except Exception as e:
            logger.error(f"Failed to get schema info: {e}")
            return {"tables": [], "columns": []}
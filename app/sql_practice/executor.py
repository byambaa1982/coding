"""
SQL Query Executor
Handles SQL query execution with validation and result processing
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime
import hashlib
import json

from app.sql_practice.sandbox import SQLSandbox
from app.sql_practice.validators import SQLValidator

logger = logging.getLogger(__name__)


class SQLExecutor:
    """Executes SQL queries with validation and safety checks"""
    
    def __init__(self, user_id: int, session_id: str):
        """
        Initialize SQL executor
        
        Args:
            user_id: User ID
            session_id: Session identifier
        """
        self.user_id = user_id
        self.session_id = session_id
        self.sandbox = SQLSandbox(user_id, session_id)
        self.validator = SQLValidator()
    
    def execute(self, query: str, read_only: bool = False, 
                allow_delete: bool = False, timeout: int = 30) -> Dict:
        """
        Execute SQL query with validation
        
        Args:
            query: SQL query to execute
            read_only: If True, only SELECT queries allowed
            allow_delete: If True, DELETE queries allowed
            timeout: Execution timeout in seconds
        
        Returns:
            dict with execution results and metadata
        """
        execution_id = self._generate_execution_id(query)
        start_time = datetime.utcnow()
        
        # Validate query
        validation = self.validator.validate_query(
            query, 
            read_only=read_only,
            allow_delete=allow_delete
        )
        
        if not validation['valid']:
            return {
                'success': False,
                'execution_id': execution_id,
                'errors': validation['errors'],
                'warnings': validation.get('warnings', []),
                'timestamp': start_time.isoformat()
            }
        
        # Ensure sandbox is created
        sandbox_result = self.sandbox.create_sandbox()
        if not sandbox_result['success']:
            return {
                'success': False,
                'execution_id': execution_id,
                'errors': ['Failed to create sandbox: ' + sandbox_result.get('error', 'Unknown error')],
                'timestamp': start_time.isoformat()
            }
        
        # Execute query in sandbox
        result = self.sandbox.execute_query(query)
        
        # Add metadata
        result['execution_id'] = execution_id
        result['timestamp'] = start_time.isoformat()
        result['warnings'] = validation.get('warnings', [])
        result['query'] = query
        
        # Log execution
        logger.info(
            f"SQL execution {execution_id} - User: {self.user_id}, "
            f"Success: {result['success']}, Time: {result.get('execution_time', 0)}s"
        )
        
        return result
    
    def validate_exercise_solution(self, query: str, expected_result: Dict) -> Dict:
        """
        Validate exercise solution against expected result
        
        Args:
            query: User's SQL query
            expected_result: Expected query result
        
        Returns:
            dict with validation result and feedback
        """
        # Execute user's query
        execution_result = self.execute(query, read_only=True)
        
        if not execution_result['success']:
            return {
                'passed': False,
                'feedback': 'Query execution failed: ' + execution_result.get('error', 'Unknown error'),
                'execution_result': execution_result
            }
        
        # Compare results
        comparison = self._compare_results(
            execution_result.get('results', []),
            execution_result.get('columns', []),
            expected_result.get('results', []),
            expected_result.get('columns', [])
        )
        
        return {
            'passed': comparison['matches'],
            'feedback': comparison['feedback'],
            'execution_result': execution_result,
            'comparison': comparison
        }
    
    def _compare_results(self, user_results: List[Dict], user_columns: List[str],
                        expected_results: List[Dict], expected_columns: List[str]) -> Dict:
        """Compare user results with expected results"""
        
        # Check column count
        if len(user_columns) != len(expected_columns):
            return {
                'matches': False,
                'feedback': f'Column count mismatch. Expected {len(expected_columns)} columns, got {len(user_columns)}.'
            }
        
        # Check column names (case-insensitive)
        user_cols_lower = [c.lower() for c in user_columns]
        expected_cols_lower = [c.lower() for c in expected_columns]
        
        if sorted(user_cols_lower) != sorted(expected_cols_lower):
            return {
                'matches': False,
                'feedback': f'Column names mismatch. Expected: {expected_columns}, Got: {user_columns}'
            }
        
        # Check row count
        if len(user_results) != len(expected_results):
            return {
                'matches': False,
                'feedback': f'Row count mismatch. Expected {len(expected_results)} rows, got {len(user_results)}.'
            }
        
        # Compare data (order-insensitive for some cases)
        user_results_sorted = sorted([json.dumps(r, sort_keys=True, default=str) for r in user_results])
        expected_results_sorted = sorted([json.dumps(r, sort_keys=True, default=str) for r in expected_results])
        
        if user_results_sorted != expected_results_sorted:
            return {
                'matches': False,
                'feedback': 'Query results do not match expected output. Check your WHERE clauses and calculations.'
            }
        
        return {
            'matches': True,
            'feedback': 'Excellent! Your query returns the correct results.'
        }
    
    def get_schema_info(self) -> Dict:
        """Get database schema information"""
        # Ensure sandbox exists
        self.sandbox.create_sandbox()
        return self.sandbox.get_schema_info()
    
    def preview_table(self, table_name: str, limit: int = 10) -> Dict:
        """Preview table data"""
        # Ensure sandbox exists
        self.sandbox.create_sandbox()
        return self.sandbox.preview_table(table_name, limit)
    
    def reset_database(self) -> Dict:
        """Reset database to initial state"""
        return self.sandbox.reset_database()
    
    def cleanup(self) -> Dict:
        """Clean up sandbox"""
        return self.sandbox.cleanup()
    
    def _generate_execution_id(self, query: str) -> str:
        """Generate unique execution ID"""
        data = f"{self.user_id}_{self.session_id}_{query}_{datetime.utcnow().isoformat()}"
        return hashlib.md5(data.encode()).hexdigest()[:16]

"""
SQL query validation and security checks
"""
import re
from typing import Dict, List, Tuple


class SQLValidator:
    """Validates SQL queries for security and complexity"""
    
    # Dangerous SQL keywords that should be blocked in certain contexts
    DANGEROUS_KEYWORDS = [
        'DROP', 'TRUNCATE', 'ALTER', 'CREATE', 'GRANT', 'REVOKE',
        'LOCK', 'UNLOCK', 'RENAME', 'FLUSH', 'SHUTDOWN'
    ]
    
    # Allowed keywords for read-only mode
    READ_ONLY_KEYWORDS = ['SELECT', 'SHOW', 'DESCRIBE', 'EXPLAIN', 'DESC']
    
    # DML keywords for exercises that allow modifications
    DML_KEYWORDS = ['INSERT', 'UPDATE', 'DELETE']
    
    @staticmethod
    def normalize_query(query: str) -> str:
        """Normalize SQL query by removing comments and extra whitespace"""
        # Remove single-line comments (-- )
        query = re.sub(r'--[^\n]*', '', query)
        # Remove multi-line comments (/* */)
        query = re.sub(r'/\*.*?\*/', '', query, flags=re.DOTALL)
        # Normalize whitespace
        query = ' '.join(query.split())
        return query.strip()
    
    @staticmethod
    def is_read_only(query: str) -> bool:
        """Check if query is read-only (SELECT, SHOW, DESCRIBE, EXPLAIN)"""
        normalized = SQLValidator.normalize_query(query).upper()
        
        if not normalized:
            return False
        
        # Get first keyword
        first_keyword = normalized.split()[0] if normalized.split() else ''
        
        return first_keyword in SQLValidator.READ_ONLY_KEYWORDS
    
    @staticmethod
    def contains_dangerous_keywords(query: str) -> Tuple[bool, List[str]]:
        """Check if query contains dangerous keywords"""
        normalized = SQLValidator.normalize_query(query).upper()
        found_keywords = []
        
        for keyword in SQLValidator.DANGEROUS_KEYWORDS:
            pattern = r'\b' + keyword + r'\b'
            if re.search(pattern, normalized):
                found_keywords.append(keyword)
        
        return len(found_keywords) > 0, found_keywords
    
    @staticmethod
    def validate_query(query: str, read_only: bool = False, 
                      allow_delete: bool = False) -> Dict[str, any]:
        """
        Validate SQL query based on execution mode
        
        Args:
            query: SQL query string
            read_only: If True, only SELECT queries are allowed
            allow_delete: If True, DELETE queries are allowed (requires read_only=False)
        
        Returns:
            dict with 'valid' (bool), 'errors' (list), 'warnings' (list)
        """
        result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        if not query or not query.strip():
            result['valid'] = False
            result['errors'].append('Query cannot be empty')
            return result
        
        normalized = SQLValidator.normalize_query(query)
        
        if len(normalized) > 10000:
            result['valid'] = False
            result['errors'].append('Query is too long (max 10000 characters)')
            return result
        
        # Check for dangerous keywords
        has_dangerous, dangerous_keywords = SQLValidator.contains_dangerous_keywords(query)
        if has_dangerous:
            result['valid'] = False
            result['errors'].append(
                f'Query contains forbidden keywords: {", ".join(dangerous_keywords)}'
            )
            return result
        
        # Check read-only mode
        if read_only:
            if not SQLValidator.is_read_only(query):
                result['valid'] = False
                result['errors'].append(
                    'Only SELECT, SHOW, DESCRIBE, and EXPLAIN queries are allowed'
                )
                return result
        
        # Check DELETE restriction
        if not allow_delete and 'DELETE' in normalized.upper():
            result['valid'] = False
            result['errors'].append('DELETE queries are not allowed for this exercise')
            return result
        
        # Check for multiple statements (basic check)
        if ';' in normalized[:-1]:  # Allow semicolon at the end
            result['warnings'].append(
                'Multiple statements detected. Only the first statement will be executed.'
            )
        
        # Check query complexity (basic heuristics)
        if normalized.upper().count('JOIN') > 5:
            result['warnings'].append(
                'Query has many JOINs. This might be slow.'
            )
        
        if normalized.upper().count('UNION') > 3:
            result['warnings'].append(
                'Query has multiple UNIONs. This might be slow.'
            )
        
        return result
    
    @staticmethod
    def extract_tables(query: str) -> List[str]:
        """Extract table names from SQL query (basic implementation)"""
        normalized = SQLValidator.normalize_query(query).upper()
        tables = []
        
        # Pattern to match table names after FROM, JOIN, INTO, UPDATE
        patterns = [
            r'FROM\s+([a-zA-Z_][a-zA-Z0-9_]*)',
            r'JOIN\s+([a-zA-Z_][a-zA-Z0-9_]*)',
            r'INTO\s+([a-zA-Z_][a-zA-Z0-9_]*)',
            r'UPDATE\s+([a-zA-Z_][a-zA-Z0-9_]*)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, normalized)
            tables.extend(matches)
        
        return list(set([t.lower() for t in tables]))

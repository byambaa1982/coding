"""
SQL Sandbox Manager
Manages isolated MySQL database instances for SQL practice
"""
try:
    import docker
    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False
    docker = None

import mysql.connector
import time
import logging
from typing import Dict, Optional, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class SQLSandbox:
    """Manages Docker-based MySQL sandbox for SQL execution"""
    
    def __init__(self, user_id: int, session_id: str):
        """
        Initialize SQL sandbox for a user session
        
        Args:
            user_id: User ID
            session_id: Unique session identifier
        """
        self.user_id = user_id
        self.session_id = session_id
        self.container_name = f"sql_sandbox_{user_id}_{session_id}"
        self.docker_client = docker.from_env()
        self.container = None
        self.db_config = {
            'host': 'localhost',
            'port': None,  # Will be assigned dynamically
            'user': 'sandbox_user',
            'password': 'sandbox_pass',
            'database': 'sandbox_db'
        }
    
    def create_sandbox(self, schema_id: Optional[str] = None) -> Dict:
        """
        Create a new sandboxed MySQL container
        
        Args:
            schema_id: Optional schema to load
        
        Returns:
            dict with connection details
        """
        try:
            # Check if container already exists
            existing = self._get_existing_container()
            if existing:
                logger.info(f"Reusing existing container: {self.container_name}")
                self.container = existing
                self.db_config['port'] = self._get_container_port()
                return {
                    'success': True,
                    'container_id': self.container.id,
                    'port': self.db_config['port']
                }
            
            # Create new container
            logger.info(f"Creating new SQL sandbox: {self.container_name}")
            
            logger.info(f"Creating new SQL sandbox container: {self.container_name}")
            
            self.container = self.docker_client.containers.run(
                image='sql_sandbox:latest',
                name=self.container_name,
                detach=True,
                remove=False,  # Don't auto-remove so we can reuse containers
                mem_limit='512m',
                cpu_quota=50000,  # 50% of one CPU
                publish_all_ports=True,  # Auto-publish all exposed ports
                environment={
                    'MYSQL_ROOT_PASSWORD': 'sandbox_root_pass',
                    'MYSQL_DATABASE': 'sandbox_db',
                    'MYSQL_USER': 'sandbox_user',
                    'MYSQL_PASSWORD': 'sandbox_pass'
                },
                labels={
                    'user_id': str(self.user_id),
                    'session_id': self.session_id,
                    'created_at': datetime.utcnow().isoformat(),
                    'type': 'sql_sandbox'
                }
            )
            
            logger.info(f"Container created with ID: {self.container.id[:12]}")
            
            # Wait for MySQL to be ready
            self._wait_for_mysql()
            
            # Get assigned port
            self.db_config['port'] = self._get_container_port()
            
            # Load custom schema if specified
            if schema_id:
                self._load_schema(schema_id)
            
            return {
                'success': True,
                'container_id': self.container.id,
                'port': self.db_config['port']
            }
            
        except Exception as e:
            logger.error(f"Failed to create sandbox: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_existing_container(self):
        """Check if container already exists for this user session"""
        try:
            return self.docker_client.containers.get(self.container_name)
        except docker.errors.NotFound:
            return None
    
    def _get_container_port(self) -> int:
        """Get the host port mapped to MySQL container port 3306"""
        self.container.reload()
        port_bindings = self.container.attrs['NetworkSettings']['Ports']
        
        if '3306/tcp' not in port_bindings or port_bindings['3306/tcp'] is None:
            logger.error(f"Port 3306 not bound. Port bindings: {port_bindings}")
            raise Exception("MySQL port 3306 is not properly exposed")
        
        host_port = port_bindings['3306/tcp'][0]['HostPort']
        logger.info(f"Container {self.container_name} port 3306 mapped to host port {host_port}")
        return int(host_port)
    
    def _wait_for_mysql(self, timeout: int = 60):
        """Wait for MySQL to be ready to accept connections"""
        start_time = time.time()
        attempt = 0
        
        logger.info(f"Waiting for MySQL to start in {self.container_name}...")
        
        # First, wait a few seconds for MySQL to begin initialization
        time.sleep(3)
        
        while time.time() - start_time < timeout:
            attempt += 1
            try:
                # Check if container is still running
                self.container.reload()
                if self.container.status != 'running':
                    logger.error(f"Container stopped with status: {self.container.status}")
                    raise Exception(f"Container failed to start: {self.container.status}")
                
                self.db_config['port'] = self._get_container_port()
                conn = mysql.connector.connect(**self.db_config, connection_timeout=5)
                conn.close()
                elapsed = time.time() - start_time
                logger.info(f"✅ MySQL ready in container {self.container_name} after {elapsed:.1f}s ({attempt} attempts)")
                return True
            except mysql.connector.Error as e:
                if attempt % 3 == 0:  # Log every 3 attempts
                    elapsed = time.time() - start_time
                    logger.info(f"⏳ Waiting for MySQL... attempt {attempt}, elapsed: {elapsed:.1f}s")
                time.sleep(3)
            except Exception as e:
                logger.error(f"Error waiting for MySQL: {str(e)}")
                raise
        
        raise TimeoutError(f"MySQL did not start within {timeout} seconds after {attempt} attempts")
    
    def _load_schema(self, schema_id: str):
        """Load a custom database schema"""
        # TODO: Implement schema loading from predefined schemas
        pass
    
    def execute_query(self, query: str, fetch_results: bool = True) -> Dict:
        """
        Execute SQL query in the sandbox
        
        Args:
            query: SQL query to execute
            fetch_results: Whether to fetch and return results
        
        Returns:
            dict with results, columns, row_count, execution_time
        """
        start_time = time.time()
        
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Execute query
            cursor.execute(query)
            
            # Fetch results if SELECT query
            results = []
            columns = []
            
            if fetch_results and cursor.description:
                columns = [desc[0] for desc in cursor.description]
                results = cursor.fetchall()
                # Convert to list of dicts
                results = [dict(zip(columns, row)) for row in results]
            
            # Commit if DML query
            if query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE')):
                conn.commit()
            
            row_count = cursor.rowcount
            execution_time = time.time() - start_time
            
            cursor.close()
            conn.close()
            
            return {
                'success': True,
                'results': results,
                'columns': columns,
                'row_count': row_count,
                'execution_time': round(execution_time, 3)
            }
            
        except mysql.connector.Error as e:
            execution_time = time.time() - start_time
            logger.error(f"Query execution error: {str(e)}")
            
            return {
                'success': False,
                'error': str(e),
                'error_code': e.errno if hasattr(e, 'errno') else None,
                'execution_time': round(execution_time, 3)
            }
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Unexpected error: {str(e)}")
            
            return {
                'success': False,
                'error': str(e),
                'execution_time': round(execution_time, 3)
            }
    
    def get_schema_info(self) -> Dict:
        """Get information about database schema (tables, columns)"""
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("SHOW TABLES")
            tables = [row[0] for row in cursor.fetchall()]
            
            schema_info = {}
            
            for table in tables:
                # Get columns for each table
                cursor.execute(f"DESCRIBE {table}")
                columns = []
                
                for col in cursor.fetchall():
                    columns.append({
                        'name': col[0],
                        'type': col[1],
                        'null': col[2],
                        'key': col[3],
                        'default': col[4],
                        'extra': col[5]
                    })
                
                # Get row count
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                row_count = cursor.fetchone()[0]
                
                schema_info[table] = {
                    'columns': columns,
                    'row_count': row_count
                }
            
            cursor.close()
            conn.close()
            
            return {
                'success': True,
                'tables': schema_info
            }
            
        except Exception as e:
            logger.error(f"Failed to get schema info: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def preview_table(self, table_name: str, limit: int = 10) -> Dict:
        """Preview data from a table"""
        query = f"SELECT * FROM {table_name} LIMIT {limit}"
        return self.execute_query(query)
    
    def reset_database(self):
        """Reset database to initial state"""
        try:
            if self.container:
                # Restart container to reset database
                self.container.restart()
                self._wait_for_mysql()
                return {'success': True}
        except Exception as e:
            logger.error(f"Failed to reset database: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def cleanup(self):
        """Clean up sandbox container"""
        try:
            if self.container:
                logger.info(f"Cleaning up sandbox: {self.container_name}")
                self.container.stop()
                self.container.remove()
                return {'success': True}
        except Exception as e:
            logger.error(f"Failed to cleanup sandbox: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def cleanup_old_containers(hours: int = 2):
        """Clean up containers older than specified hours"""
        try:
            client = docker.from_env()
            containers = client.containers.list(
                filters={'label': 'type=sql_sandbox'}
            )
            
            cleaned = 0
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            for container in containers:
                created_at_str = container.labels.get('created_at')
                if created_at_str:
                    created_at = datetime.fromisoformat(created_at_str)
                    if created_at < cutoff_time:
                        logger.info(f"Cleaning up old container: {container.name}")
                        container.stop()
                        container.remove()
                        cleaned += 1
            
            return {'success': True, 'cleaned': cleaned}
            
        except Exception as e:
            logger.error(f"Failed to cleanup old containers: {str(e)}")
            return {'success': False, 'error': str(e)}

# app/python_practice/sandbox.py
"""Docker sandbox configuration for Python code execution."""

import docker
from typing import Dict, Any


class PythonSandbox:
    """
    Python code execution sandbox using Docker.
    TODO: Implement full Docker sandboxing for production.
    """
    
    def __init__(self):
        """Initialize Docker client."""
        self.client = None
        self.container_image = 'python:3.11-alpine'
        self.max_memory = '128m'
        self.max_cpu_period = 100000
        self.max_cpu_quota = 50000  # 50% of one core
        self.network_disabled = True
        
    def connect(self):
        """Connect to Docker daemon."""
        try:
            self.client = docker.from_env()
            return True
        except Exception as e:
            print(f'Failed to connect to Docker: {e}')
            return False
    
    def execute(self, code: str, timeout: int = 30) -> Dict[str, Any]:
        """
        Execute Python code in Docker container.
        
        Args:
            code: Python code to execute
            timeout: Execution timeout in seconds
            
        Returns:
            Dictionary with execution results
        """
        if not self.client:
            if not self.connect():
                return {
                    'status': 'error',
                    'error': 'Docker is not available',
                    'output': ''
                }
        
        result = {
            'status': 'error',
            'output': '',
            'error': '',
            'exit_code': -1
        }
        
        try:
            # Run code in container
            container = self.client.containers.run(
                image=self.container_image,
                command=['python', '-c', code],
                mem_limit=self.max_memory,
                cpu_period=self.max_cpu_period,
                cpu_quota=self.max_cpu_quota,
                network_disabled=self.network_disabled,
                remove=True,
                detach=False,
                stdout=True,
                stderr=True,
                timeout=timeout
            )
            
            result['status'] = 'success'
            result['output'] = container.decode('utf-8')
            result['exit_code'] = 0
            
        except docker.errors.ContainerError as e:
            result['status'] = 'error'
            result['error'] = e.stderr.decode('utf-8') if e.stderr else str(e)
            result['exit_code'] = e.exit_status
            
        except docker.errors.ImageNotFound:
            result['status'] = 'error'
            result['error'] = f'Docker image {self.container_image} not found'
            
        except docker.errors.APIError as e:
            result['status'] = 'error'
            result['error'] = f'Docker API error: {str(e)}'
            
        except Exception as e:
            result['status'] = 'error'
            result['error'] = f'Unexpected error: {str(e)}'
        
        return result
    
    def build_custom_image(self, requirements: list = None):
        """
        Build custom Docker image with allowed packages.
        TODO: Implement for production use.
        """
        pass
    
    def cleanup_containers(self):
        """Clean up stopped containers."""
        if self.client:
            try:
                # Remove stopped containers
                for container in self.client.containers.list(all=True, filters={'status': 'exited'}):
                    container.remove()
            except Exception as e:
                print(f'Error cleaning up containers: {e}')


# Singleton instance
sandbox = PythonSandbox()

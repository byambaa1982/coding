# security_config.py
"""Security configuration for Python sandbox."""

# Restricted built-ins - only allow safe functions
ALLOWED_BUILTINS = {
    'abs', 'all', 'any', 'ascii', 'bin', 'bool', 'bytearray', 'bytes',
    'chr', 'complex', 'dict', 'divmod', 'enumerate', 'filter', 'float',
    'format', 'frozenset', 'getattr', 'hasattr', 'hash', 'hex', 'id',
    'int', 'isinstance', 'issubclass', 'iter', 'len', 'list', 'map',
    'max', 'min', 'next', 'object', 'oct', 'ord', 'pow', 'print',
    'range', 'repr', 'reversed', 'round', 'set', 'setattr', 'slice',
    'sorted', 'str', 'sum', 'tuple', 'type', 'zip'
}

# Banned imports
BANNED_IMPORTS = [
    'os', 'sys', 'subprocess', 'socket', 'urllib', 'requests',
    'pickle', 'shelve', 'marshal', 'ctypes', 'multiprocessing',
    'threading', '__import__', 'importlib', 'imp',
    'eval', 'exec', 'compile', 'execfile', 'input', 'raw_input',
    'open', 'file'
]

# Allowed imports (whitelist)
ALLOWED_IMPORTS = [
    'math', 'random', 'datetime', 'collections', 'itertools',
    'functools', 're', 'json', 'statistics', 'decimal',
    'fractions', 'string', 'copy', 'heapq', 'bisect',
    'numpy', 'pandas'
]

# Resource limits
MAX_EXECUTION_TIME = 30  # seconds
MAX_MEMORY = 128  # MB
MAX_OUTPUT_LENGTH = 5000  # characters
MAX_CODE_LENGTH = 10000  # characters

# Security settings
NETWORK_DISABLED = True
READ_ONLY_FILESYSTEM = False  # Set to True in production
ALLOW_FILE_IO = False

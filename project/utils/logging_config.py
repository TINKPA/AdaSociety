import logging
import os

# Create logs directory if it doesn't exist
log_dir = 'project/logs'
os.makedirs(log_dir, exist_ok=True)

# Create a custom logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

# Create handlers
file_handler = logging.FileHandler(f'{log_dir}/app.log', encoding='utf-8')
console_handler = logging.StreamHandler()

# Create formatters and add them to handlers
formatter = logging.Formatter("{asctime} - {levelname} - {message}", style="{", datefmt="%Y-%m-%dT%H:%M:%S")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

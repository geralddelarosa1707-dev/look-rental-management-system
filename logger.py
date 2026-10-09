import logging
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(base_dir, "app.log")

logger = logging.getLogger("flask_app")
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(log_path)
file_handler.setLevel(logging.INFO)

file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s")
file_handler.setFormatter(file_formatter)

if not logger.handlers:
  logger.addHandler(file_handler)
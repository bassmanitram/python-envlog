#!/usr/bin/env python3
"""
Example usage of envlog package.

Run with:
    PTHN_LOG=info python example.py
    PTHN_LOG=debug,myapp.database=trace python example.py
    PTHN_LOG=warn,myapp=info python example.py
"""

import logging

import envlog

# Initialize logging from PTHN_LOG environment variable
envlog.init()

# Create loggers for different modules
app_logger = logging.getLogger("myapp")
db_logger = logging.getLogger("myapp.database")
api_logger = logging.getLogger("myapp.api")
lib_logger = logging.getLogger("somelib")

# Log at different levels
app_logger.debug("Application starting (debug)")
app_logger.info("Application initialized (info)")

db_logger.debug("Database connection pool created (debug)")
db_logger.info("Database connected (info)")

api_logger.debug("API server starting (debug)")
api_logger.info("API server listening on port 8080 (info)")

lib_logger.debug("Library function called (debug)")
lib_logger.info("Library initialized (info)")
lib_logger.warning("Library warning (warning)")

print("\n" + "=" * 70)
print("Try running with different PTHN_LOG values:")
print("  PTHN_LOG=info python example.py")
print("  PTHN_LOG=debug python example.py")
print("  PTHN_LOG=warn,myapp=debug python example.py")
print("  PTHN_LOG=warn,myapp.database=debug python example.py")
print("=" * 70)

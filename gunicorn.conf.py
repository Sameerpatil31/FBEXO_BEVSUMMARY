import multiprocessing
import os

# Bind to the dynamic port provided by Render
bind = f"0.0.0.0:{os.getenv('PORT', '8080')}"

# Number of workers (adjust for CPU cores)
workers = multiprocessing.cpu_count() * 2 + 1

# Threads per worker for handling requests
threads = 2

# Enable access logs
accesslog = '-'

# Enable error logs
errorlog = '-'

# Set log level
loglevel = 'info'

# Graceful timeout for long-running requests
timeout = 120
worker_class = 'gevent'  # Use async worker class for long requests
graceful_timeout = 300
keepalive = 5  # Keep connections alive for reuse

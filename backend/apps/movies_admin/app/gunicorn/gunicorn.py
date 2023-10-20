"""Gunicorn *development* config file"""

# Django WSGI application path in pattern MODULE_NAME:VARIABLE_NAME
wsgi_app = "config.wsgi:application"
# The granularity of Error log outputs
loglevel = "INFO"
# The number of worker processes for handling requests
core_number = 2
# The number of worker processes for handling requests.
workers = 4 * core_number
# The number of worker threads for handling requests.
threads = 4 * core_number
# The socket to bind
bind = "0.0.0.0:8000"

# Restart workers when code changes (development only!)
reload = False

# Redirect stdout/stderr to log file
capture_output = True

# Daemonize the Gunicorn process (detach & enter background)
daemon = False

# The maximum number of requests a worker will process before restarting.
max_requests = 500

# Limit the allowed size of an HTTP request header field.
limit_request_field_size = 65535

# The number of seconds to wait for requests on a Keep-Alive connection.
keepalive = 5

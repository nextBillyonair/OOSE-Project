#!usr/local/bin/python
from app import app
import os

if __name__ == "__main__":
    config = os.getenv('CONFIG', 'development')
    if config == "development":
        app.run(host='10.161.159.82', port=80, debug=True, threaded=True)
    elif config == "testing":
        app.run(host='0.0.0.0', port=8080, debug=True, threaded=True)
    else:
    	raise ValueError("Invalid configuration for server, use testing or development")
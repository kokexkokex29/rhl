"""
Flask Web Server for Keep-Alive Functionality
Simple status page to keep the bot running on hosting platforms
"""

from flask import Flask, render_template
import logging
import datetime

app = Flask(__name__)
logger = logging.getLogger(__name__)

@app.route('/')
def status():
    """Main status page"""
    return render_template('status.html', 
                         status="Bot is running",
                         timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

@app.route('/health')
def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.datetime.now().isoformat(),
        "service": "Football Club Management Bot"
    }

@app.route('/ping')
def ping():
    """Simple ping endpoint for uptime monitoring"""
    return "pong"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)

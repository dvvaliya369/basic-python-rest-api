import logging
from logging.handlers import RotatingFileHandler
from flask import Flask

app = Flask(__name__)
app.config.from_object('api.config')
#app.config.from_envvar('API_CONFIG')

# Configuration for file uploads
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# ref: https://gist.github.com/ibeex/3257877
formatter = logging.Formatter(
    "[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")
handler = RotatingFileHandler(app.config['LOG_FILENAME'],
                              maxBytes=10000000,
                              backupCount=5)
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)
app.logger.addHandler(handler)

# Output the access logs to the same file
log = logging.getLogger('werkzeug')
log.setLevel(logging.DEBUG)
log.addHandler(handler)

@app.errorhandler(404)
def page_not_found(e):
    return "404 not found", 404

# Register Swagger API blueprint
try:
    from api.swagger_config import api_blueprint
    app.register_blueprint(api_blueprint)
    
    # Import Swagger routes to register them with the API
    import api.swagger_routes
    
    app.logger.info("Swagger documentation enabled at /api/v1/docs/")
except ImportError as e:
    app.logger.warning(f"Could not enable Swagger documentation: {e}")
    app.logger.info("Falling back to basic routes without Swagger")
    
    # Import the basic routes as fallback
    from api.examples import get_example
    from api.posts import create_post
    from api.comments import comment_routes

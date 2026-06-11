from flask import Flask
from dotenv import load_dotenv
import os
import logging
from backend.db_connection import init_app as init_db
from backend.housing.housing import housing_bp
from backend.housing.listing import listing_bp
from backend.housing.reviews import reviews_bp
from backend.housing.funding import funding_bp
from backend.housing.stats import stats_bp
from backend.housing.prediction import prediction_bp

def create_app():
    app = Flask(__name__)

    app.logger.setLevel(logging.DEBUG)
    app.logger.info('API startup')

    # Load environment variables from the .env file so they are
    # accessible via os.getenv() below.
    load_dotenv()

    # Secret key used by Flask for securely signing session cookies.
    # .strip() removes accidental leading/trailing whitespace from .env values.
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY").strip()

    # Database connection settings — values come from the .env file.
    app.config["MYSQL_DATABASE_USER"] = os.getenv("DB_USER").strip()
    app.config["MYSQL_DATABASE_PASSWORD"] = os.getenv("MYSQL_ROOT_PASSWORD").strip()
    app.config["MYSQL_DATABASE_HOST"] = os.getenv("DB_HOST").strip()
    app.config["MYSQL_DATABASE_PORT"] = int(os.getenv("DB_PORT").strip())
    app.config["MYSQL_DATABASE_DB"] = os.getenv("DB_NAME").strip()

    # Register the cleanup hook for the database connection.
    app.logger.info("create_app(): initializing database connection")
    init_db(app)

    # Register the routes from each Blueprint with the app object
    # and give a url prefix to each.
    app.logger.info("create_app(): registering blueprints")
    app.register_blueprint(housing_bp, url_prefix = "/housing")
    app.register_blueprint(listing_bp, url_prefix = "/housing")
    app.register_blueprint(reviews_bp, url_prefix = "/housing")
    app.register_blueprint(funding_bp, url_prefix = "/housing")
    app.register_blueprint(stats_bp, url_prefix = "/housing")
    app.register_blueprint(prediction_bp, url_prefix = "/housing")

    return app

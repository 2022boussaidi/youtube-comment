from flask import Flask
from routes.analysis import analysis_bp
from config.settings import Config

def create_app():
    app = Flask(__name__)
    app.register_blueprint(analysis_bp, url_prefix='/api')
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
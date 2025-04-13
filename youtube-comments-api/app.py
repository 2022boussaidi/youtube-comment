from flask import Flask
from routes.comments import comments_bp
from config.settings import Config

def create_app():
    app = Flask(__name__)
    
    # Register blueprints
    app.register_blueprint(comments_bp)
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
    
from flask import Blueprint, request, jsonify
from services.youtube_service import YouTubeService
from config.settings import Config
from utils.exceptions import YouTubeAPIError

# Create the Blueprint instance
comments_bp = Blueprint('comments', __name__)

@comments_bp.route('/get_comments', methods=['GET'])
def fetch_comments():
    video_id = request.args.get('video_id')
    if not video_id:
        return jsonify({"error": "video_id is required"}), 400

    if not Config.API_KEY:
        return jsonify({"error": "API_KEY not configured"}), 500

    try:
        youtube_service = YouTubeService(Config.API_KEY)
        comments_df = youtube_service.get_comments(video_id)
        
        return jsonify({
            "message": f"Comments fetched and saved to {video_id}_user_comments.csv",
            "comments": comments_df.to_json(orient='records', force_ascii=False)
        }), 200
        
    except YouTubeAPIError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred"}), 500

# Make sure the Blueprint is exported
__all__ = ['comments_bp']
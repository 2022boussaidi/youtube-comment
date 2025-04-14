from flask import Blueprint, request, jsonify
import pandas as pd
from services.toxicity_service import ToxicityService
from services.mongo_service import MongoService
from utils.text_cleaner import clean_text
from utils.exceptions import InvalidCSVError
from models.comment import CommentAnalysis

analysis_bp = Blueprint('analysis', __name__)

def read_comments_from_csv(file_path):
    try:
        df = pd.read_csv(file_path)
        if 'comment' not in df.columns:
            raise InvalidCSVError("CSV must contain a 'comment' column.")
        return df['comment'].dropna().tolist()
    except Exception as e:
        raise InvalidCSVError(str(e))

@analysis_bp.route('/process_comments', methods=['POST'])
def process_comments():
    data = request.get_json()
    
    if not data or 'file_path' not in data:
        return jsonify({"error": "No file path provided"}), 400
    
    try:
        comments = read_comments_from_csv(data['file_path'])
        if not comments:
            return jsonify({"error": "No comments found in the file"}), 400

        toxicity_service = ToxicityService()
        mongo_service = MongoService()
        processed_data = []

        for comment in comments:
            cleaned_comment = clean_text(comment)
            toxicity_result = toxicity_service.analyze(cleaned_comment)
            
            comment_data = CommentAnalysis(
                original_comment=comment,
                cleaned_comment=cleaned_comment,
                toxicity_score=toxicity_result
            )
            
            inserted_id = mongo_service.insert_comment(comment_data.__dict__).inserted_id
            processed_data.append({**comment_data.__dict__, '_id': str(inserted_id)})
        
        mongo_service.close_connection()
        return jsonify(processed_data), 200
    
    except InvalidCSVError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Processing failed: {str(e)}"}), 500 
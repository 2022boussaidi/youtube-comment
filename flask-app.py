import json
import pandas as pd
from flask import Flask, request, jsonify
from detoxify import Detoxify
from pymongo import MongoClient
import re
import numpy as np

class ToxicityAnalyzer:
    def __init__(self, db_uri, db_name, collection_name, detoxify_model_name):
        # Initialize Flask and MongoDB
        self.app = Flask(__name__)
        self.client = MongoClient(db_uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
        
        # Initialize Detoxify model
        self.detoxify_model = Detoxify(detoxify_model_name)
        self.app.add_url_rule('/process_comments', 'process_comments', self.process_comments, methods=['POST'])

    def clean_text(self, text):
        """Clean text (remove special characters and extra spaces)."""
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text)  # Remove non-alphanumeric characters
        text = re.sub(r'\s+', ' ', text)  # Remove extra spaces
        return text.strip()

    def analyze_toxicity(self, comment):
        """Analyze toxicity of a comment using Detoxify."""
        result = self.detoxify_model.predict(comment)
        # Convert result to a serializable format
        return {key: float(value) if isinstance(value, np.float32) else value for key, value in result.items()}

    def read_comments_from_csv(self, file_path):
        """Read comments from a CSV file."""
        try:
            df = pd.read_csv(file_path)
            if 'comment' not in df.columns:
                raise ValueError("CSV must contain a 'comment' column.")
            return df['comment'].dropna().tolist()  # Return list of non-NaN comments
        except Exception as e:
            print(f"Error reading CSV: {e}")
            return []

    def process_comments(self):
        # Get the CSV file path from the request
        data = request.get_json()
        
        if not data or 'file_path' not in data:
            return jsonify({"error": "No file path provided"}), 400
        
        file_path = data['file_path']
        comments = self.read_comments_from_csv(file_path)
        if not comments:
            return jsonify({"error": "No comments found in the file"}), 400

        processed_data = []

        for comment in comments:
            # Clean the comment
            cleaned_comment = self.clean_text(comment)
            
            # Analyze the toxicity of the comment
            toxicity_result = self.analyze_toxicity(cleaned_comment)
            
            # Save to MongoDB
            comment_data = {
                'original_comment': comment,
                'cleaned_comment': cleaned_comment,
                'toxicity_score': toxicity_result
            }
            
            # Insert into MongoDB
            self.collection.insert_one(comment_data)
           
            processed_data.append(comment_data)
        
        # Convert ObjectId to string before returning results
        for item in processed_data:
            item['_id'] = str(item['_id'])  # Convert ObjectId to string
        
        return jsonify(processed_data), 200

    def run(self):
        """Start the Flask application."""
        self.app.run(debug=True)

if __name__ == "__main__":
    # MongoDB and Detoxify settings
    db_uri = "mongodb://localhost:27017/"
    db_name = "youtube-comments"
    collection_name = "posts"
    detoxify_model_name = 'original'  # Select Detoxify model

    # Create an instance of ToxicityAnalyzer and start the app
    analyzer = ToxicityAnalyzer(db_uri, db_name, collection_name, detoxify_model_name)
    analyzer.run()

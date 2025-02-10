from flask import Flask, request, jsonify
from googleapiclient.discovery import build
import pandas as pd
from time import sleep
import traceback
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

def get_comments(api_key, video_id):
    youtube = build('youtube', 'v3', developerKey=api_key)

    request = youtube.commentThreads().list(
        part="snippet,replies",
        videoId=video_id,
        textFormat="plainText"
    )

    df = pd.DataFrame(columns=['comment', 'replies', 'date', 'user_name'])
    iteration_count = 0  # Counter to track iterations

    while request and iteration_count < 10:  # Limit to 10 iterations
        replies = []
        comments = []
        dates = []
        user_names = []

        try:
            response = request.execute()

            for item in response['items']:
                # Extracting comments
                comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
                comments.append(comment)

                user_name = item['snippet']['topLevelComment']['snippet']['authorDisplayName']
                user_names.append(user_name)

                date = item['snippet']['topLevelComment']['snippet']['publishedAt']
                dates.append(date)

                # counting number of reply of comment
                replycount = item['snippet']['totalReplyCount']

                # if reply is there
                if replycount > 0:
                    # append empty list to replies
                    replies.append([])
                    # iterate through all reply
                    for reply in item['replies']['comments']:
                        # Extract reply
                        reply = reply['snippet']['textDisplay']
                        # append reply to last element of replies
                        replies[-1].append(reply)
                else:
                    replies.append([])

            # create new dataframe
            df2 = pd.DataFrame({"comment": comments, "replies": replies, "user_name": user_names, "date": dates})
            df = pd.concat([df, df2], ignore_index=True)
            df.to_csv(f"{video_id}_user_comments.csv", index=False, encoding='utf-8')
            sleep(2)
            request = youtube.commentThreads().list_next(request, response)
            iteration_count += 1  # Increment the counter
            print(f"Iteration {iteration_count} completed")
        except Exception as e:
            print(str(e))
            print(traceback.format_exc())
            print("Sleeping for 10 seconds")
            sleep(10)
            df.to_csv(f"{video_id}_user_comments.csv", index=False, encoding='utf-8')
            break

    return df

@app.route('/get_comments', methods=['GET'])
def fetch_comments():
    video_id = request.args.get('video_id')
    if not video_id:
        return jsonify({"error": "video_id is required"}), 400

    api_key = os.getenv("API_KEY")
    if not api_key:
        return jsonify({"error": "API_KEY not found in environment variables"}), 500

    try:
        comments_df = get_comments(api_key, video_id)
        # Convert DataFrame to JSON
        comments_json = comments_df.to_json(orient='records', force_ascii=False)
        return jsonify({
            "message": f"Comments fetched and saved to {video_id}_user_comments.csv",
            "comments": comments_json
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
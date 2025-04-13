from googleapiclient.discovery import build
import pandas as pd
from time import sleep
from config.settings import Config
from utils.exceptions import YouTubeAPIError

class YouTubeService:
    def __init__(self, api_key):
        self.api_key = api_key
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)

    def get_comments(self, video_id):
        request = self.youtube.commentThreads().list(
            part="snippet,replies",
            videoId=video_id,
            textFormat="plainText"
        )

        df = pd.DataFrame(columns=['comment', 'replies', 'date', 'user_name'])
        
        for iteration in range(Config.MAX_ITERATIONS):
            try:
                response = request.execute()
                comments_data = self._process_response(response)
                df = pd.concat([df, pd.DataFrame(comments_data)], ignore_index=True)
                df.to_csv(f"{video_id}_user_comments.csv", index=False, encoding='utf-8')
                
                sleep(Config.REQUEST_DELAY)
                request = self.youtube.commentThreads().list_next(request, response)
                print(f"Iteration {iteration + 1} completed")
                
            except Exception as e:
                print(f"Error: {str(e)}")
                sleep(Config.ERROR_DELAY)
                df.to_csv(f"{video_id}_user_comments.csv", index=False, encoding='utf-8')
                raise YouTubeAPIError(f"Failed to fetch comments: {str(e)}")

        return df

    def _process_response(self, response):
        comments_data = {
            'comment': [],
            'replies': [],
            'user_name': [],
            'date': []
        }

        for item in response['items']:
            top_comment = item['snippet']['topLevelComment']['snippet']
            
            comments_data['comment'].append(top_comment['textDisplay'])
            comments_data['user_name'].append(top_comment['authorDisplayName'])
            comments_data['date'].append(top_comment['publishedAt'])
            
            # Process replies
            replycount = item['snippet']['totalReplyCount']
            if replycount > 0:
                replies = [reply['snippet']['textDisplay'] 
                          for reply in item['replies']['comments']]
                comments_data['replies'].append(replies)
            else:
                comments_data['replies'].append([])

        return comments_data

__all__ = ['YouTubeService']
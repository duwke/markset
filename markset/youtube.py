import cv2
import datetime
import time
import os
import google.auth
from googleapiclient.discovery import build
import google_auth_oauthlib.flow
from googleapiclient.http import MediaFileUpload

# Set up YouTube API credentials
client_secrets_file = "client_secret.json"

# Get credentials and create an API client
scopes = ["https://www.googleapis.com/auth/youtube.upload"]
flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
    client_secrets_file, scopes)
credentials = flow.run_local_server()
youtube = build('youtube', 'v3', credentials=credentials)

# Video recording settings
output_dir = 'recordings'
video_filename = 'output.mp4'
video_duration = 10

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Initialize video recording
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
video_writer = cv2.VideoWriter(os.path.join(output_dir, video_filename), fourcc, 30.0, (640, 480))

# Start recording
start_time = time.time()
vid = cv2.VideoCapture(0)
while (time.time() - start_time) < video_duration:
    ret, frame = vid.read()
    if ret:
        video_writer.write(frame)
        cv2.imshow('Recording', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release video recording resources
video_writer.release()
cv2.destroyAllWindows()

# Upload video to YouTube
request_body = {
    'snippet': {
        'title': f'Recorded Video - {datetime.datetime.now()}',
        'description': 'My recorded video',
        'tags': ['recorded', 'video'],
        'categoryId': '22'  # See https://developers.google.com/youtube/v3/docs/videoCategories/list
    },
    'status': {
        'privacyStatus': 'public'
    }
}

media = MediaFileUpload(os.path.join(output_dir, video_filename), chunksize=-1, resumable=True)

upload_response = youtube.videos().insert(
    part='snippet,status',
    body=request_body,
    media_body=media
).execute()

# Print the video upload response
print('Video upload response:', upload_response)

import cv2
import requests
import json
import os
import datetime
import time

# Set your Google Drive API key and video file name
API_KEY = "YOUR_API_KEY"
VIDEO_FILENAME = "video.mp4"
VIDEO_DURATION = 10  # 3 minutes (in seconds)




# Function to upload video to Google Drive
def upload_to_drive(api_key, video_file):
    url = "https://www.googleapis.com/upload/drive/v3/files?uploadType=media"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/octet-stream"}
    data = open(video_file, 'rb').read()

    response = requests.post(url, headers=headers, data=data)
    response_json = json.loads(response.text)

    if 'id' in response_json:
        file_id = response_json['id']
        print(f"Video uploaded successfully. File ID: {file_id}")
    else:
        print("Failed to upload video.")

def upload_file_to_google_script(file_path, script_url):
    file_name = file_path.split('/')[-1]  # Extract the filename from the file path
    
    files = {'file': open(file_path, 'rb')}
    data = {'filename': file_name}  
    
    response = requests.post(script_url, files=files, data=data)
    
    if response.status_code == 200:
        print("File uploaded successfully." + response.text)
    else:
        print("File upload failed.")

# Usage example
file_path = 'recordings/output.mp4'  # Replace with the actual file path
script_url = 'https://script.google.com/macros/s/AKfycbzlrQdzlsfxErVLMS_ZlMPlKcDywif7dEgv6eQpLEc7kKtzYvnXT9ec3wcSCSahcVtH/exec'  # Replace with the actual script URL




# Record the video
print("Recording video...")
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
print("Video recording complete.")

upload_file_to_google_script(file_path, script_url)



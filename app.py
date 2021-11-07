from flask import Flask, render_template, Response
import cv2
from zaptube import VideoStream
from time import sleep
import sys


app = Flask(__name__)

# urls = [
#     'https://www.youtube.com/watch?v=BioHqHT9pp8',
#     'https://www.youtube.com/watch?v=OhhB7wVFKqQ',
#     'https://www.youtube.com/watch?v=vYR4lCk468U',
#     'https://www.youtube.com/watch?v=C_SIra_9_7k'
# ]
urls = []
with open('videolist.txt', 'r') as filehandle:
    for line in filehandle:
        url_suffix = line[:-1]
        urls.append('https://www.youtube.com/watch?v=' + url_suffix)

transition_url = 'https://www.youtube.com/watch?v=S2bCTPk5Zqg'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    return Response(VideoStream(urls, transition_url).play_video(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    app.run(debug=True)

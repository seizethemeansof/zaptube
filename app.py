from flask import Flask, render_template, Response
import cv2
from zaptube import VideoStream


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


video_stream = VideoStream(urls, transition_url)
video_stream.start_url_buffering()
video_stream.start_video_buffering()


@app.route('/video_feed')
def video_feed():
    return Response(video_stream.play_video_thread(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    app.run(debug=True)

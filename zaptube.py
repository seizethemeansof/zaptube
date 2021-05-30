import pafy
import cv2
from queue import Queue
from datetime import datetime
from time import time, sleep
import random
from threading import Thread
from multiprocessing import Process
import traceback


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


class VideoStream():

    def __init__(self, urls, transition_url):
        self.urls = urls
        self.transition_url = transition_url
        self.url_to_buffer = Queue(maxsize=0)
        self.zaptube = Queue(maxsize=0)
        self.BUFFERING_NOW = 0
        # Met le brouillage initial
        self.transition_frames_list = self.extract_transition_frames(1)
        self.zaptube.put(self.create_transition_frames_queue())

    def extract_transition_frames(self, seconds):
        video_frames = []
        video = pafy.new(self.transition_url)
        best = video.getbest(preftype="mp4")
        capture = cv2.VideoCapture(best.url)
        # capture.set(cv2.CAP_PROP_BUFFERSIZE, 2)
        fps = capture.get(cv2.CAP_PROP_FPS)
        nb_frames = 0
        while capture.isOpened():
            grabbed, frame = capture.read()
            if grabbed == True:
                video_frames.append([frame, fps])
                nb_frames += 1
                if (nb_frames / fps > seconds):
                    break
            else:
                break
            cv2.waitKey(1)
        capture.release()
        return video_frames

    def create_transition_frames_queue(self):
        transition_frames_queue = Queue(maxsize=0)
        for elm in self.transition_frames_list:
            transition_frames_queue.put(elm)
        return transition_frames_queue

    def extract_frames(self, url, seconds):
        video_frames = Queue(maxsize=0)
        video = pafy.new(url)
        best = video.getbest(preftype="mp4")
        capture = cv2.VideoCapture(best.url)
        fps = capture.get(cv2.CAP_PROP_FPS)
        length = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        index = random.randint(0, int(length - fps * seconds))
        capture.set(cv2.CAP_PROP_POS_FRAMES, index)
        nb_frames = 0
        while capture.isOpened():
            grabbed, frame = capture.read()
            if grabbed == True:
                video_frames.put([frame, fps])
                nb_frames += 1
                if (nb_frames / fps > seconds):
                    break
            else:
                break
            # cv2.waitKey(1)
        capture.release()
        return video_frames

    def process_url(self, url):
        duration = random.randint(2, 5)
        print('Extracting {}'.format(duration))
        vf = self.extract_frames(url, duration)
        self.zaptube.put(vf)
        self.zaptube.put(self.create_transition_frames_queue())
        self.BUFFERING_NOW -= 1
        print('Done extracting')

    def url_buffering_thread(self):
        print('Starting video buffering')
        while True:
            print('Buffering: {}, Zaptube; {}'.format(
                self.BUFFERING_NOW, self.zaptube.qsize()))
            if (self.BUFFERING_NOW < 3) & (self.zaptube.qsize() < 8):
                self.BUFFERING_NOW += 1
                url = random.choice(self.urls)
                self.url_to_buffer.put(url)
            else:
                sleep(3)

    def start_url_buffering(self):
        u_thread = Thread(target=self.url_buffering_thread)
        u_thread.start()

    def video_buffering_thread(self):
        while True:
            url = self.url_to_buffer.get()
            self.process_url(url)

    def start_video_buffering(self):
        vb_thread = Thread(target=self.video_buffering_thread)
        vb_thread.start()

    def play_video_thread(self):
        play = True
        while self.zaptube.qsize() < 8:
            sleep(5)
        try:
            while play:
                video = self.zaptube.get()
                prev = 0
                frame, fps = video.get()
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                     b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result
                while video.qsize() > 0:
                    time_elapsed = time() - prev
                    if time_elapsed > 1/fps * 0.5:
                        frame, fps = video.get()
                        ret, buffer = cv2.imencode('.jpg', frame)
                        frame = buffer.tobytes()
                        yield (b'--frame\r\n'
                            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result
                        prev = time()
                if self.zaptube.qsize() == 0:
                    sleep(10)
        except Exception:
            print(traceback.format_exc())

    def start_play_video(self):
        play_video_thread = Thread(target=self.play_video_thread)
        play_video_thread.start()


def main():

    video_stream = VideoStream(urls, transition_url)
    video_stream.start_url_buffering()
    video_stream.start_video_buffering()
    while video_stream.zaptube.qsize() < 8:
        sleep(5)
    print('Play the video')
    video_stream.start_play_video()

    while True:
        sleep(10)


if __name__ == '__main__':
    main()

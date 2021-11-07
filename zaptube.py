import pafy
import cv2
from queue import Queue
from datetime import datetime
from time import time, sleep
import random
from threading import Thread
from multiprocessing import Process
import traceback
import sys


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


class VideoStream:

    def __init__(self, urls, transition_url):
        self.urls = urls
        self.transition_url = transition_url
        self.zaptube = Queue(maxsize=0)
        self.BUFFERING = 0
        # Met le brouillage initial
        self.transition_frames_list = self.extract_transition_frames(1)
        self.zaptube.put(self.create_transition_frames_queue())
        self.play = True
        self.video_buffering_thread = Thread(target=self.buffer_videos, daemon=True)
        self.monitoring_thread = Thread(target=self.monitor_process, daemon=True)
        self.video_buffering_thread.start()
        self.monitoring_thread.start()

    def extract_transition_frames(self, seconds):
        video_frames = []
        video = pafy.new(self.transition_url)
        # best = video.getbest(preftype="mp4")
        best = video.streams[0]
        capture = cv2.VideoCapture(best.url)
        # capture.set(cv2.CAP_PROP_BUFFERSIZE, 2)
        fps = capture.get(cv2.CAP_PROP_FPS)
        nb_frames = 0
        while capture.isOpened():
            grabbed, frame = capture.read()
            if grabbed is True:
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                video_frames.append([frame, fps])
                nb_frames += 1
                if nb_frames / fps > seconds:
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
        try:
            video_frames = Queue(maxsize=0)
            video = pafy.new(url)
            # best = video.getbest(preftype="mp4")
            best = video.streams[0]
            capture = cv2.VideoCapture(best.url)
            fps = capture.get(cv2.CAP_PROP_FPS)
            length = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
            index = random.randint(0, int(length - fps * seconds))
            capture.set(cv2.CAP_PROP_POS_FRAMES, index)
            nb_frames = 0
            while capture.isOpened():
                grabbed, frame = capture.read()
                if grabbed is True:
                    ret, buffer = cv2.imencode('.jpg', frame)
                    frame = buffer.tobytes()
                    video_frames.put([frame, fps])
                    nb_frames += 1
                    if nb_frames / fps > seconds:
                        break
                else:
                    break
                # cv2.waitKey(1)
            self.zaptube.put(video_frames)
            self.zaptube.put(self.create_transition_frames_queue())
            print('Done extracting')
            capture.release()
        except Exception as e:
            sys.stderr.write(
                "Encountered an exception while extracting a video. Exception was {e}\n".format(e=e))
        # cv2.destroyAllWindows()
        self.BUFFERING -= 1

    def monitor_process(self):
        while self.play is True:
            print('Buffering: {}, Zaptube; {}'.format(self.BUFFERING, self.zaptube.qsize()))
            sleep(1)

    def buffer_videos(self):
        while self.play is True:
            try:
                if (self.BUFFERING < 10) & (self.zaptube.qsize() < 20):
                    url = random.choice(self.urls)
                    duration = random.randint(2, 5)
                    print('Extracting {}'.format(duration))
                    Thread(target=self.extract_frames, args=(url, duration)).start()
                    self.BUFFERING += 1
            except Exception as e:
                sys.stderr.write(
                    "Encountered an exception while buffering a video. Exception was {e}\n".format(e=e))
            sleep(1)
        print('Stopping video buffering thread')

    def play_video(self):
        while self.zaptube.qsize() < 10:
            sleep(1)
        while self.play is True:
            try:
                print("Playing a video")
                video = self.zaptube.get_nowait()
                prev = 0
                frame, fps = video.get_nowait()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
                while video.qsize() > 0:
                    try:
                        time_elapsed = time() - prev
                        if time_elapsed > 1/fps:
                            frame, fps = video.get_nowait()
                            yield (b'--frame\r\n'
                                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
                            prev = time()
                    except Exception as e:
                        sys.stderr.write(
                            "Encountered an exception while sending the frame. Exception was {e}\n".format(e=e))
            except Exception as e:
                sys.stderr.write(
                    "Encountered an exception while sending the frame. Exception was {e}\n".format(e=e))
            # if self.zaptube.qsize() == 0:
            #     sleep(10)
        print('Stopping video playing')

    def shutdown(self):
        print('Shutting down')
        self.play = False
        cv2.destroyAllWindows()


def main():
    print('Cool cool cool.')


if __name__ == '__main__':
    main()

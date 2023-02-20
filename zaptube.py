import pafy
import cv2
from queue import Queue
from time import time, sleep
import random
from threading import Thread
import sys


urls = []
with open('videolist.txt', 'r') as filehandle:
    for line in filehandle:
        url_suffix = line[:-1]
        urls.append('https://www.youtube.com/watch?v=' + url_suffix)

transition_url = 'https://www.youtube.com/watch?v=S2bCTPk5Zqg'


def extract_video_frames(url, seconds=2, random_start=False):
    try:
        print(f'Starting the extraction of the frames for {url}.')
        video_frames = Queue(maxsize=0)
        video = pafy.new(url)
        best = video.streams[0]
        capture = cv2.VideoCapture(best.url)
        fps = capture.get(cv2.CAP_PROP_FPS)
        length = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        # Define a random starting point of the video.
        if random_start:
            index = random.randint(0, int(length - fps * seconds))
        else:
            index = 0
        capture.set(cv2.CAP_PROP_POS_FRAMES, index)
        nb_frames = 0
        while capture.isOpened():
            grabbed, frame = capture.read()
            if grabbed is True:
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                video_frames.put(frame, fps)
                nb_frames += 1
                # Stop when there are enough frames.
                if nb_frames / fps > seconds:
                    break
            else:
                break
        print('The extraction is done!')
        capture.release()
        return {
            'frames': video_frames,
            'fps': fps,
        }
        
    except Exception as e:
        sys.stderr.write(
            "Encountered an exception while extracting the frame of a video. \
                Exception was {e}\n".format(e=e))
        return None


class VideoStream:

    def __init__(self, urls, transition_url):
        self.urls = urls
        self.transition_url = transition_url
        self.videos = Queue(maxsize=0)
        self.buffering_count = 0
        # Create the transition frames and store them.
        self.transition_frames = extract_video_frames(self.transition_url, 1)
        self.play = True
        self.video_buffering_thread = Thread(target=self.video_buffering,
                                             daemon=True)
        self.video_buffering_thread.start()
        # self.monitoring_thread = Thread(target=self.monitor_process, 
        #                                 daemon=True)
        # self.monitoring_thread.start()

    def add_transition_frames(self):
        transition_frames_queue = Queue(maxsize=0)
        for elm in self.transition_frames['frames'].queue:
            transition_frames_queue.put(elm)
        return {
            'frames': transition_frames_queue,
            'fps': self.transition_frames['fps'],
        }

    def buffer_video(self, url, duration, random_start):
        try:
            video_frames = extract_video_frames(url, duration, random_start)
            self.videos.put(self.add_transition_frames())
            self.videos.put(video_frames)
        except Exception as e:
            sys.stderr.write(
                "Encountered an exception while extracting a video. \
                    Exception was {e}\n".format(e=e))
        self.buffering_count -= 1

    def video_buffering(self):
        while self.play is True:
            if (self.buffering_count < 10) & (self.videos.qsize() < 20):
                try:
                    url = random.choice(self.urls)
                    duration = random.randint(2, 5)
                    Thread(target=self.buffer_video, 
                           args=(url, duration, True)).start()
                    self.buffering_count += 1
                except Exception as e:
                    sys.stderr.write(
                        "Encountered an exception while buffering a video. \
                            Exception was {e}\n".format(e=e))
            else:
                sleep(1)
        print('Stopping video buffering thread')
        
    def monitor_process(self):
        while self.play is True:
            print('Buffering: {}, Zaptube; {}'.format(self.BUFFERING, self.zaptube.qsize()))
            sleep(1)

    def play_video(self):
        while self.videos.qsize() < 20:
            sleep(1)
        while self.play is True:
            try:
                print("Playing a video")
                video = self.videos.get_nowait()
                fps = video['fps']
                frame = video['frames'].get_nowait()
                prev = 0
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
                while video['frames'].qsize() > 0:
                    try:
                        time_elapsed = time() - prev
                        if time_elapsed > 1/fps:
                            frame = video['frames'].get_nowait()
                            yield (b'--frame\r\n'
                                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
                            prev = time()
                    except Exception as e:
                        sys.stderr.write(
                            "Encountered an exception while sending the frame. \
                                Exception was {e}\n".format(e=e))
            except Exception as e:
                sys.stderr.write(
                    "Encountered an exception while sending the frame. \
                        Exception was {e}\n".format(e=e))
        print('Stopping video playing')

    def shutdown(self):
        print('Shutting down')
        self.play = False
        cv2.destroyAllWindows()


def main():
    print('Cool cool cool.')


if __name__ == '__main__':
    main()

import signal
import subprocess

import prctl

from picamera2.outputs import Output

YOUTUBE="rtmp://a.rtmp.youtube.com/live2/" 

class FfmpegYoutubeOutput(Output):
    """
    """

    def __init__(self, youtube_key, pts=None):
        super().__init__(pts=pts)
        self.ffmpeg = None
        self.output_url = YOUTUBE + youtube_key

    def start(self):
        general_options = ['-loglevel', 'debug']  
        # We have to get FFmpeg to timestamp the video frames as it gets them. This isn't
        # ideal because we're likely to pick up some jitter, but works passably, and I
        # don't have a better alternative right now.
        video_input = ['-use_wallclock_as_timestamps', '1',
                       '-thread_queue_size', '32',  # necessary to prevent warnings
                       '-i', '-']
        video_codec = ['-c:v', 'copy', '-f', 'flv', self.output_url]
        no_audio = ['-re', '-f', 'lavfi', '-i', 'anullsrc']

        command = ['ffmpeg'] + general_options + video_input + no_audio + video_codec 
        # The preexec_fn is a slightly nasty way of ensuring FFmpeg gets stopped if we quit
        # without calling stop() (which is otherwise not guaranteed).
        self.ffmpeg = subprocess.Popen(command, stdin=subprocess.PIPE, preexec_fn=lambda: prctl.set_pdeathsig(signal.SIGKILL))
        super().start()

    def stop(self):
        super().stop()
        if self.ffmpeg is not None:
            self.ffmpeg.stdin.close()  # FFmpeg needs this to shut down tidily
            self.ffmpeg.terminate()
            self.ffmpeg = None

    def outputframe(self, frame, keyframe=True, timestamp=None):
        if self.recording:
            self.ffmpeg.stdin.write(frame)
            self.ffmpeg.stdin.flush()  # forces every frame to get timestamped individually
            self.outputtimestamp(timestamp)

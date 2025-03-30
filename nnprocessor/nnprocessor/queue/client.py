import os
import shutil
import time

import cv2
from moviepy import VideoFileClip
import numpy as np
import torch

from nnprocessor.interp.model import Interpolator

class QueueClient():
    MAX_CONSECUTIVE_EXCEPTIONS = 50
    MAX_PIXEL_COUNT = 1024 * 1024

    def __init__(self, root_dir:str, model:Interpolator, state_dict, device):
        self.model = model.to(device)
        self.model.load_state_dict(state_dict)
        self.model.eval()
        self.device = device

        if len(root_dir) > 0 and root_dir[-1] != "/":
            root_dir += "/"

        self.root_dir = root_dir
        self.enqueue_directory = root_dir + "queue/"
        self.error_directory = root_dir + "error/"
        self.processing_directory = root_dir + "processing/"
        self.processed_directory = root_dir + "processed/"
        self.buffer_directory = root_dir + "buffer/"
        self.buffer_video = self.buffer_directory + "buf.mp4"

        self.toprocess = []
        self.running = False

        self.cap = None
        self.writer = None

    def run(self) -> None:
        self.running = True
        self._initialize_queuedir()
        self._populate_toprocess()
        self._consecutive_exceptions = 0
        self._recover_from_exception = False
        print("Queue client started!")
        while self.running:
            if self._consecutive_exceptions >= QueueClient.MAX_CONSECUTIVE_EXCEPTIONS:
                print(f"Maximum number of consecutive exceptions ({QueueClient.MAX_CONSECUTIVE_EXCEPTIONS}) reached. Removing current video.")
                self._consecutive_exceptions = 0
                self._recover_from_exception = True

            try:
                # Await videos to process 
                if len(self.toprocess) <= 0:
                    self._populate_toprocess()
                    time.sleep(0.01)
                    continue

                # Get current video to be processed
                cur_video_str = self._pop_file()
                if self._recover_from_exception:
                    self._push_err(cur_video_str)
                    self._recover_from_exception = False
                    continue
                if "." not in cur_video_str:
                    self._push_err(cur_video_str)
                    continue
                self._try_make_videoreader(cur_video_str)
                if self.cap is None:
                    self._push_err(cur_video_str)
                    continue
                    
                # Make output video name
                video_proper_name = (".".join(cur_video_str.split(".")[:-1]) + ".mp4").split("/")[-1]
                final_video_str = self.processed_directory + video_proper_name
                final_video_buf_str = self.buffer_directory + video_proper_name
                
                # Get video properties
                try:
                    frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
                    frame_rate = self.cap.get(cv2.CAP_PROP_FPS)
                    duration = frame_count / frame_rate
                    new_frame_rate = int(1000.0 * ((frame_count * 2 - 1) / duration)) / 1000.0
                    frame_size = (int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
                    if frame_size[0] * frame_size[1] > QueueClient.MAX_PIXEL_COUNT:
                        self._push_err(cur_video_str)
                        self._release_cap()
                        continue
                except:
                    self._push_err(cur_video_str)
                    self._release_cap()
                    continue

                # Open buffer video
                self._try_make_videowriter(self.buffer_video, new_frame_rate, frame_size)
                if self.writer is None:
                    raise Exception("Could not open buffer video!")

                # Interpolate the video
                thisframe = None
                nextframe = None
                while True:
                    if nextframe is None:
                        ret1, thisframe = self.cap.read()
                        if not ret1:
                            self._release_cap()
                            self._release_writer()
                            break
                        ret2, nextframe = self.cap.read()
                        if not ret2:
                            self._release_cap()
                            self._release_writer()
                            break
                    else:
                        thisframe = nextframe
                        ret2, nextframe = self.cap.read()
                        if not ret2:
                            self.writer.write(thisframe)
                            self._release_cap()
                            self._release_writer()
                            break

                    # Generate frame
                    t_frame1 = ((torch.from_numpy(thisframe).float() * 2.0 / 255.0) - 1.0).permute(2, 1, 0).unsqueeze(0)
                    t_frame2 = ((torch.from_numpy(nextframe).float() * 2.0 / 255.0) - 1.0).permute(2, 1, 0).unsqueeze(0)
                    t_framegen = self._gen_frame(t_frame1, t_frame2)
                    framegen = ((t_framegen + 1.0) * 255.0 / 2.0).byte().detach().squeeze(0).permute(2, 1, 0).cpu().numpy()

                    self.writer.write(thisframe)
                    self.writer.write(framegen)
                
                self._release_cap()
                self._release_writer()

                # Add audio to the video and output to buffer dir with proper name
                orig_vid = VideoFileClip(cur_video_str)
                interp_vid = VideoFileClip(self.buffer_video)
                
                audio = orig_vid.audio
                final_vid:VideoFileClip = interp_vid.with_audio(audio)

                final_vid.write_videofile(final_video_buf_str, codec="libx264", audio_codec="aac")

                orig_vid.close()
                interp_vid.close()

                # Move final video to processed dir and remove intermediate files
                os.remove(self.buffer_video)
                os.remove(cur_video_str)
                shutil.move(final_video_buf_str, final_video_str)

                self._consecutive_exceptions = 0
            
            except Exception as e:
                print(e)
                self._consecutive_exceptions += 1
                time.sleep(0.001)
    
    def stop(self) -> None:
        self.running = False

    def _gen_frame(self, frame1:torch.Tensor, frame2:torch.Tensor) -> torch.Tensor:
        self.model.eval()

        frame1 = frame1.to(self.device)
        frame2 = frame2.to(self.device)

        out = self.model(frame1, frame2)
        return out

    def _try_make_videoreader(self, video_path:str):
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return None

        self.cap = cap
    
    def _try_make_videowriter(self, video_path:str, framerate:float, size:cv2.typing.Size):
        with open(video_path, "wb") as video_file:
            video_file.write(b'')
        os.remove(video_path)

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')

        writer = cv2.VideoWriter(video_path, fourcc, framerate, size)
        if not writer.isOpened():
            return None

        self.writer = writer

    def _initialize_queuedir(self) -> None:
        os.makedirs(self.enqueue_directory, exist_ok=True)
        os.makedirs(self.error_directory, exist_ok=True)
        os.makedirs(self.processing_directory, exist_ok=True)
        os.makedirs(self.processed_directory, exist_ok=True)
        os.makedirs(self.buffer_directory, exist_ok=True)

    def _populate_toprocess(self) -> None:
        for file in os.listdir(self.processing_directory):
            file = self.processing_directory + file
            if file not in self.toprocess:
                self.toprocess.append(file)

        for file in os.listdir(self.enqueue_directory):
            file = self.enqueue_directory + file
            if file not in self.toprocess:
                self.toprocess.append(file)
    
    def _pop_file(self) -> str:
        cur_video_str = self.toprocess[0]
        self.toprocess = self.toprocess[1:]

        if self.processing_directory not in cur_video_str:
            cur_video_str = shutil.move(cur_video_str, self.processing_directory)

        return cur_video_str
    
    def _push_err(self, video:str):
        err_file = shutil.move(video, self.error_directory)
        with open(err_file, "wb") as err_stream:
            err_stream.write(b'')

    def _release_cap(self):
        if self.cap != None:
            self.cap.release()
            self.cap = None

    def _release_writer(self):
        if self.writer != None:
            self.writer.release()
            self.writer = None

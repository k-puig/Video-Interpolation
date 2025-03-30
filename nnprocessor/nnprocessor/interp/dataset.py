import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torchvision.io as io

import os
import threading

class SingleVideoDataset(torch.utils.data.Dataset):
    MAX_CACHED_VIDEOS = 50
    cached_videos = {}
    video_cache_order = []
    cache_lock = threading.Lock()
    cache_hits = 0
    cache_misses = 0

    def __init__(self, path:str, cached_len:int = None):
        super(SingleVideoDataset, self).__init__()
        self.path = path
        self.len = cached_len
        if cached_len == None:
            # Determine length (reads entire video!)
            video_frames, audio_frames, metadata = io.read_video(path, output_format="TCHW", pts_unit="sec")
            self.len = video_frames.size(0) - 2

    def __getitem__(self, index):
        with SingleVideoDataset.cache_lock:
            if self.path in SingleVideoDataset.cached_videos:
                SingleVideoDataset.cache_hits += 1
                video_frames = SingleVideoDataset.cached_videos[self.path]
                left_frame = video_frames[index] * 2.0 / 255.0 - 1.0
                interp_frame = video_frames[index + 1] * 2.0 / 255.0 - 1.0
                right_frame = video_frames[index + 2] * 2.0 / 255.0 - 1.0
                return left_frame, interp_frame, right_frame
        
        # Not found in cache!
        video_frames, _, _ = io.read_video(self.path, output_format="TCHW", pts_unit="sec")
        with SingleVideoDataset.cache_lock:
            SingleVideoDataset.cache_misses += 1
            SingleVideoDataset.cached_videos[self.path] = video_frames
            SingleVideoDataset.video_cache_order.append(self.path)
            if len(SingleVideoDataset.video_cache_order) > SingleVideoDataset.MAX_CACHED_VIDEOS:
                SingleVideoDataset.cached_videos.pop(SingleVideoDataset.video_cache_order[0])
                SingleVideoDataset.video_cache_order = SingleVideoDataset.video_cache_order[1:]
        left_frame = video_frames[index] * 2.0 / 255.0 - 1.0
        interp_frame = video_frames[index + 1] * 2.0 / 255.0 - 1.0
        right_frame = video_frames[index + 2] * 2.0 / 255.0 - 1.0
        return left_frame, interp_frame, right_frame

    def __len__(self):
        return max(0, self.len)

class VideoFolderDataset(torch.utils.data.Dataset):
    def __init__(self, path:str, csv_cache:str = None):
        super(VideoFolderDataset, self).__init__()
        self.path = path
        self.svd_list = []
        self.len = 0
        
        files = [os.path.relpath(os.path.join(path, f)) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        csv_buf = None
        if csv_cache == None:
            self._build_cache(path, None)
        else:
            if os.path.exists(csv_cache):
                with open(csv_cache, "r") as csv_buf:
                    line = csv_buf.readline().strip()
                    if line == "name,frames":
                        line = csv_buf.readline().strip()
                        while line != "":
                            vals = line.split(",")
                            svd = SingleVideoDataset(vals[0], int(vals[1]))
                            self.svd_list.append((len(svd) + self.len, svd))
                            self.len += len(svd)

                            line = csv_buf.readline().strip()
            else:
                self._build_cache(path, csv_cache)
    
    def __getitem__(self, index):
        prev_c = 0
        for svd_c, svd_ds in self.svd_list:
            if index < svd_c:
                return svd_ds[index - prev_c]
            prev_c = svd_c
    
    def __len__(self):
        return self.len
    
    def _build_cache(self, path:str, csv_cache:str = None):
        files = [os.path.relpath(os.path.join(path, f)) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        if csv_cache != None:
            with open(csv_cache, "w") as csv_buf:
                csv_buf.write("name,frames\n")
                for f in files:
                    svd = SingleVideoDataset(f)
                    if len(svd) > 0:
                        self.svd_list.append((len(svd) + self.len, svd))
                        self.len += len(svd)
                        csv_buf.write(f"{f},{len(svd)}\n")
                        csv_buf.flush()
        else:
            for f in files:
                svd = SingleVideoDataset(f)
                if len(svd) > 0:
                    self.svd_list.append((len(svd) + self.len, svd))
                    self.len += len(svd)

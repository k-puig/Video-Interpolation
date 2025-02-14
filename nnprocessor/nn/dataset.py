import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torchvision.io as io

import os

class SingleVideoDataset(torch.utils.data.Dataset):
    def __init__(self, path:str):
        super(SingleVideoDataset, self).__init__()
        self.path = path
        
        # Determine length (reads entire video!)
        video_frames, audio_frames, metadata = io.read_video(path, output_format="TCHW", pts_unit="sec")
        self.len = video_frames.size(0)

    def __getitem__(self, index):
        video_frames, audio_frames, metadata = io.read_video(self.path, output_format="TCHW", pts_unit="sec")
        video_frames = video_frames / 255.0
        input_frames = video_frames[index : index + 3 : 2].permute(1, 0, 2, 3)
        output_frames = video_frames[index + 1 : index + 2].permute(1, 0, 2, 3)
        return input_frames, output_frames

    def __len__(self):
        return max(0, self.len - 2)

class VideoFolderDataset(torch.utils.data.Dataset):
    def __init__(self, path:str):
        super(VideoFolderDataset, self).__init__()
        self.path = path
        self.svd_list = []
        
        files = [os.path.relpath(os.path.join(path, f)) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

        self.len = 0
        for f in files:
            svd = SingleVideoDataset(f)
            if len(svd) > 0:
                self.svd_list.append((len(svd) + self.len, svd))
                self.len += len(svd)
    
    def __getitem__(self, index):
        for svd in self.svd_list:
            if index >= svd[0]:
                return svd[1][index - svd[0]]
    
    def __len__(self):
        return self.len

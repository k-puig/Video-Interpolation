import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torchvision.io as io

import os

import numpy
import requests

class SingleVideoDataset(torch.utils.data.Dataset):
    def __init__(self, path:str):
        super(SingleVideoDataset, self).__init__()
        self.path = path
        
        # Determine length (reads entire video!)
        video_frames, audio_frames, metadata = io.read_video(path, output_format="TCHW", pts_unit="sec")
        self.len = video_frames.size(0)

    def __getitem__(self, index):
        video_frames, audio_frames, metadata = io.read_video(self.path, output_format="TCHW", pts_unit="sec")
        video_frames = (2.0 * video_frames / 255.0) - 1.0
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

class TensorServerDataset(torch.utils.data.Dataset):
    def __init__(self, domain:str, train_type:str):
        super(TensorServerDataset, self).__init__()
        self.domain = domain
        
        if train_type != "train" and train_type != "validate" and train_type != "test":
            raise Exception(f"Bad train_type value \"{train_type}\"")
        self.train_type = train_type
    
    def __getitem__(self, index):
        left_tensor = self._get_tensor(index)
        interp_tensor = self._get_tensor(index + 1)
        right_tensor = self._get_tensor(index + 2)
        
        input_tensor = torch.cat((left_tensor, right_tensor), dim=1)
        return input_tensor, interp_tensor
        
    def __len__(self):
        len_txt = requests.get(f"{self.domain}/{self.train_type}/total_frame_count").text
        return int(len_txt) - 2
        
    def _get_tensor(self, index):
        req = requests.get(f"{self.domain}/{self.train_type}/{index}/tensor")
        if req.status_code != 200:
            raise Exception(f"Error in requesting {self.train_type} tensor index {index}")
        tensorbytes = req.content
        width = 0x0
        width = width | (tensorbytes[0] << 24)
        width = width | (tensorbytes[1] << 16)
        width = width | (tensorbytes[2] << 8)
        width = width | tensorbytes[3]
        
        height = 0x0
        height = height | (tensorbytes[4] << 24)
        height = height | (tensorbytes[5] << 16)
        height = height | (tensorbytes[6] << 8)
        height = height | tensorbytes[7]
        
        tensorbytes = tensorbytes[8:]
        tensor = torch.Tensor(numpy.frombuffer(tensorbytes, dtype=numpy.uint8).copy())
        tensor = tensor / 255.0
        tensor = tensor.view(1, height, width, 3)
        
        return tensor.permute(3, 0, 1, 2)
    
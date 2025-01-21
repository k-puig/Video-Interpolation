from interp.nn.model import *

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torch.utils.data as data
import torchvision.transforms.v2 as tform

import matplotlib
matplotlib.use('QtAgg')
import matplotlib.pyplot as plt

import numpy as np

class Trainer():
    def __init__(self, model:Interpolator, device):
        self.model = model.to(device)
        self.device = device
        self._shown = None
    
    def train(self, dataset:data.Dataset, shuffle_subset:int=None, batch_size:int=1):
        self.model.train()

        random_sampler = torch.utils.data.RandomSampler(dataset, num_samples=shuffle_subset)
        dataloader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, sampler=random_sampler)
        
        optimizer = optim.Adadelta(self.model.parameters(), lr=1e-2)
        frame_loss = nn.MSELoss().to(self.device)
        total_loss = 0.0
        total_items = 0
        for batch in dataloader:
            # Load the input/output data
            input_frames, interp_frame = [x.to(self.device) for x in batch]
            batch_size = batch[0].size(0)
            
            # Forward pass
            predicted_frame = self.model(input_frames)
            self._show(input_frames, interp_frame, predicted_frame)
            
            # Loss calculation
            loss = frame_loss(predicted_frame, interp_frame)
            total_loss += loss.item() * batch_size
            total_items += batch_size
            
            # Backward pass/optimization
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
        
        if total_items == 0:
            return 0.0
        average_loss = total_loss / total_items
        return average_loss
    
    def validate(self, dataset:data.Dataset, shuffle_subset:int=None, batch_size:int=1):
        self.model.eval()
        dataloader = torch.utils.DataLoader(dataset, batch_size=batch_size, shuffle=False)
        return 0.0
    
    def test(self, dataset:data.Dataset, shuffle_subset:int=None, batch_size:int=1):
        self.model.eval()
        dataloader = torch.utils.DataLoader(dataset, batch_size=batch_size, shuffle=False)
        return 0.0
    
    def run(self, train_dataset:data.Dataset, test_dataset:data.Dataset, val_dataset:data.Dataset, shuffle_subset:int=None, epochs:int=20, batch_size:int=1):
        epoch_losses = []
        for epoch in range(epochs):
            train_loss = self.train(train_dataset, batch_size=batch_size, shuffle_subset=shuffle_subset)
            print(f"Training step {epoch+1}")
            validate_loss = self.validate(val_dataset, batch_size=batch_size, shuffle_subset=shuffle_subset)
            print(f"Validate step {epoch+1}")
            epoch_losses.append((train_loss, validate_loss))
        test_loss = self.test(test_dataset, batch_size=batch_size, shuffle_subset=shuffle_subset)
        print("Testing finished")
        return epoch_losses, test_loss

    def _show(self, input_frames, real_frames, generated_frames):
        input_frames = input_frames.detach().cpu()[0].permute(1, 0, 2, 3)[0].permute(1, 2, 0).data.numpy().copy()
        real_frames = real_frames.detach().cpu()[0].permute(1, 0, 2, 3)[0].permute(1, 2, 0).data.numpy().copy()
        generated_frames = generated_frames.detach().cpu()[0].permute(1, 0, 2, 3)[0].permute(1, 2, 0).data.numpy().copy()
        
        shown = np.vstack((real_frames, generated_frames))
        
        if self._shown == None:
            self._shown = plt.imshow(shown)
        else:
            self._shown.set_data(shown)
        
        plt.draw()
        plt.pause(0.1)
        #plt.show(block=False)

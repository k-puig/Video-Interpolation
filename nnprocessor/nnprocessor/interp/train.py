import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torch.utils.data as data
import torchvision.transforms.v2 as tform

from nnprocessor.interp.model import Interpolator

import numpy as np

import random

class Trainer():
    def __init__(self, weight_output_file:str, model:Interpolator, device):
        self.weight_output_file = weight_output_file
        self.model = model.to(device)
        self.device = device
    
    def train(self, dataset:data.Dataset, subset_size:int=None, batch_size:int=1):
        self.model.train()

        if subset_size == None:
            subset_size = len(dataset)
        subset_size = min(subset_size, len(dataset))

        start_index = random.randint(0, len(dataset) - subset_size)

        indices = list(range(start_index, start_index + subset_size))

        sampler = torch.utils.data.SequentialSampler(indices)
        dataloader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, sampler=sampler)
        
        optimizer = optim.Adadelta(self.model.parameters(), lr=1e-2)
        frame_loss = nn.MSELoss().to(self.device)
        total_loss = 0.0
        total_items = 0
        for batch in dataloader:
            # Load the input/output data
            left_frame, interp_frame, right_frame = [x.to(self.device) for x in batch]
            batch_size = batch[0].size(0)
            
            # Forward pass
            predicted_frame = self.model(left_frame, right_frame)
            
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
    
    def validate(self, dataset:data.Dataset, subset_size:int=None, batch_size:int=1):
        self.model.eval()
        if subset_size is None:
            subset_size = len(dataset)
        subset_size = min(subset_size, len(dataset))
        start_index = random.randint(0, len(dataset) - subset_size)
        indices = list(range(start_index, start_index + subset_size))
        sampler = torch.utils.data.SequentialSampler(indices)
        dataloader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, sampler=sampler)

        frame_loss = nn.MSELoss().to(self.device)
        total_loss = 0.0
        total_items = 0
        with torch.no_grad():
            for batch in dataloader:
                # Load the input/output data
                left_frame, interp_frame, right_frame = [x.to(self.device) for x in batch]
                batch_size = batch[0].size(0)

                # Forward pass
                predicted_frame = self.model(left_frame, right_frame)

                # Loss calculation
                loss = frame_loss(predicted_frame, interp_frame)
                total_loss += loss.item() * batch_size
                total_items += batch_size

        if total_items == 0:
            return 0.0
        average_loss = total_loss / total_items
        return average_loss

    def test(self, dataset:data.Dataset, subset_size:int=None, batch_size:int=1):
        self.model.eval()
        if subset_size is None:
            subset_size = len(dataset)
        subset_size = min(subset_size, len(dataset))
        start_index = random.randint(0, len(dataset) - subset_size)
        indices = list(range(start_index, start_index + subset_size))
        sampler = torch.utils.data.SequentialSampler(indices)
        dataloader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, sampler=sampler)

        frame_loss = nn.MSELoss().to(self.device)
        total_loss = 0.0
        total_items = 0
        with torch.no_grad():
            for batch in dataloader:
                # Load the input/output data
                left_frame, interp_frame, right_frame = [x.to(self.device) for x in batch]
                batch_size = batch[0].size(0)

                # Forward pass
                predicted_frame = self.model(left_frame, right_frame)

                # Loss calculation
                loss = frame_loss(predicted_frame, interp_frame)
                total_loss += loss.item() * batch_size
                total_items += batch_size

        if total_items == 0:
            return 0.0
        average_loss = total_loss / total_items
        return average_loss
    
    def run(self, train_dataset:data.Dataset, test_dataset:data.Dataset, val_dataset:data.Dataset, subset_size:int=None, epochs:int=20, batch_size:int=1, autosave:bool=True):
        print("Training started!")
        epoch_losses = []
        for epoch in range(epochs):
            train_loss = self.train(train_dataset, batch_size=batch_size, subset_size=subset_size)
            if autosave:
                self.save_weights()
            print(f"Training step {epoch+1}; loss={train_loss}")

            validate_loss = self.validate(val_dataset, batch_size=batch_size, subset_size=subset_size)
            print(f"Validate step {epoch+1}; loss={validate_loss}")
            
            epoch_losses.append((train_loss, validate_loss))
        test_loss = self.test(test_dataset, batch_size=batch_size, subset_size=subset_size)
        print(f"Testing finished; loss={validate_loss}")
        return epoch_losses, test_loss

    def save_weights(self):
        torch.save(self.model.state_dict(), self.weight_output_file)

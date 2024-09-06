import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torch.utils.data as data

from model import *

class Trainer():
    def __init__(self, model:Interpolator, device):
        self.model = model.to(device)
        self.device = device
    
    def train(self, dataset:data.Dataset, batch_size:int=1):
        self.model.train()
        dataloader = torch.utils.DataLoader(dataset, batch_size=batch_size, shuffle=False)
        optimizer = optim.Adadelta(self.model.parameters(), lr=1e-2)
        frame_loss = nn.MSELoss().to(self.device)
        total_loss = 0.0
        total_items = 0
        for batch in dataloader:
            # Load the input/output data
            left_frame, right_frame, interp_frame = [x.to(self.device) for x in batch]
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
        
        average_loss = total_loss / total_items
        return average_loss
    
    def test(self, dataset:data.Dataset, batch_size:int=1):
        self.model.eval()
        dataloader = torch.utils.DataLoader(dataset, batch_size=batch_size, shuffle=False)
        return 0.0
    
    def validate(self, dataset:data.Dataset, batch_size:int=1):
        self.model.eval()
        dataloader = torch.utils.DataLoader(dataset, batch_size=batch_size, shuffle=False)
        return 0.0
    
    def run(self, train_dataset:data.Dataset, test_dataset:data.Dataset, val_dataset:data.Dataset, epochs:int=20, batch_size:int=1):
        for epoch in range(epochs):
            train_loss = self.train(train_dataset, batch_size=batch_size)
            validate_loss = self.validate(val_dataset, batch_size=batch_size)
        test_loss = self.test(test_dataset, batch_size=batch_size)

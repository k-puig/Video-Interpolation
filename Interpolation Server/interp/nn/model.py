import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

class Interpolator(nn.Module):
    def __init__(self):
        super().__init__()
        
        self.conv1 = nn.Conv2d(3, 64, kernel_size=3, stride=1, padding=1)
        self.conv2 = nn.Conv3d(64, 64, kernel_size=(3, 3, 2), stride=1, padding=(1, 1, 0))
        self.tconv1 = nn.ConvTranspose2d(64, 3, kernel_size=3, stride=1, padding=1)
        self.relu = nn.ReLU()
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, x):
        out = self.conv1(x)
        out = self.relu(out)
        
        out = self.conv2(out)
        out = self.relu(out)
        
        out = self.tconv1(out)
        out = self.sigmoid(out)
        
        return out
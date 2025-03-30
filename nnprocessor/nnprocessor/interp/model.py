import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

class Interpolator(nn.Module):
    def __init__(self):
        super().__init__()
        
        self.conv1 = nn.Conv2d(3, 64, kernel_size=3, stride=1, padding=1)
        self.conv2 = nn.Conv2d(128, 64, kernel_size=3, stride=1, padding=1)
        self.tconv1 = nn.ConvTranspose2d(64, 3, kernel_size=3, stride=1, padding=1)
        self.relu = nn.ReLU()
        self.tanh = nn.Tanh()

    def forward(self, frame1, frame2):
        feat1 = self.relu(self.conv1(frame1))
        feat2 = self.relu(self.conv1(frame2))
        
        combined = torch.cat([feat1, feat2], dim=1)
        
        out = self.relu(self.conv2(combined))
        out = self.tconv1(out)
        out = self.tanh(out)
        
        return out
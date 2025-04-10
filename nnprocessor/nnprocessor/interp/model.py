import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

class Interpolator(nn.Module):
    def __init__(self):
        super().__init__()
        
        self.conv1 = nn.Conv2d(3, 64, kernel_size=3, stride=1, padding=1)
        self.conv2 = nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1)
        self.conv3 = nn.Conv2d(128, 256, kernel_size=3, stride=1, padding=1)

        self.conv_combine = nn.Conv2d(512, 256, kernel_size=3, stride=1, padding=1)

        self.tconv1 = nn.ConvTranspose2d(256, 128, kernel_size=3, stride=1, padding=1)
        self.tconv2 = nn.ConvTranspose2d(128, 64, kernel_size=3, stride=1, padding=1)
        self.tconv3 = nn.ConvTranspose2d(64, 3, kernel_size=3, stride=1, padding=1)

        self.finalconv = nn.Conv2d(3, 3, kernel_size=3, stride=1, padding=1)

        self.relu = nn.ReLU()
        self.tanh = nn.Tanh()

    def forward(self, frame1, frame2):
        feat1 = self.relu(self.conv1(frame1))
        feat1 = self.relu(self.conv2(feat1))
        feat1 = self.relu(self.conv3(feat1))
        
        feat2 = self.relu(self.conv1(frame2))
        feat2 = self.relu(self.conv2(feat2))
        feat2 = self.relu(self.conv3(feat2))
        
        combined = torch.cat([feat1, feat2], dim=1)
        
        out = self.relu(self.conv_combine(combined))
        out = self.relu(self.tconv1(out))
        out = self.relu(self.tconv2(out))
        out = self.relu(self.tconv3(out))
        out = self.finalconv(out)
        out = self.tanh(out)
        
        return out

class Discriminator(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 16, kernel_size=3, stride=1, padding=0)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, stride=1, padding=0)
        self.conv3 = nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=0)
        self.conv_combine = nn.Conv2d(192, 64, kernel_size=3, stride=1, padding=0)

        self.fc = nn.Linear(64, 1)

        self.relu = nn.ReLU()
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, left_frame, interp_frame, right_frame):
        feat_l = self.relu(self.conv1(left_frame))
        feat_l = self.relu(self.conv2(feat_l))
        feat_l = self.relu(self.conv3(feat_l))

        feat_i = self.relu(self.conv1(interp_frame))
        feat_i = self.relu(self.conv2(feat_i))
        feat_i = self.relu(self.conv3(feat_i))

        feat_r = self.relu(self.conv1(right_frame))
        feat_r = self.relu(self.conv2(feat_r))
        feat_r = self.relu(self.conv3(feat_r))

        combined = self.relu(self.conv_combine(torch.cat([feat_l, feat_i, feat_r], dim=1)))

        pooled = F.adaptive_avg_pool2d(combined, (1, 1))
        pooled = pooled.view(pooled.size(0), -1)

        out = self.fc(pooled)
        prob = self.sigmoid(out)

        return prob



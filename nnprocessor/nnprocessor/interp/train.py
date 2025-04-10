import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torch.utils.data as data
import torchvision.transforms.v2 as tform

from nnprocessor.interp.model import *

import numpy as np

import random

class Trainer():
    def __init__(self, weight_output_file:str, model:Interpolator, discriminator:Discriminator, device):
        self.weight_output_file = weight_output_file
        self.generator = model.to(device)
        self.discriminator = discriminator.to(device)
        self.device = device
    
    def train(self, dataset:data.Dataset, subset_size:int=None, batch_size:int=1):
        self.generator.train()

        if subset_size == None:
            subset_size = len(dataset)
        subset_size = min(subset_size, len(dataset))

        start_index = random.randint(0, len(dataset) - subset_size)

        indices = list(range(start_index, start_index + subset_size))

        sampler = torch.utils.data.SequentialSampler(indices)
        dataloader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, sampler=sampler)
        
        optimizer_gen = optim.Adadelta(self.generator.parameters(), lr=1e-2)
        optimizer_disc = optim.Adadelta(self.discriminator.parameters(), lr=1e-2)
        mse_loss = nn.MSELoss().to(self.device)
        bce_loss = nn.BCELoss().to(self.device)
        total_loss = 0.0
        total_items = 0
        print(f"{total_items}/{subset_size}", end="", flush=True)
        for batch in dataloader:
            # Load the input/output data
            left_frame, interp_frame, right_frame = [x.to(self.device).half() for x in batch]
            batch_size = batch[0].size(0)
            real_is_real = torch.ones((batch_size, 1), device=self.device).half()
            fake_is_real = torch.zeros((batch_size, 1), device=self.device).half()

            # Train the discriminator
            optimizer_disc.zero_grad()
            output_disc_real = self.discriminator(left_frame, interp_frame, right_frame)
            loss_disc_real = bce_loss(output_disc_real, real_is_real)

            fake_frame = self.generator(left_frame, right_frame).detach()
            output_disc_fake = self.discriminator(left_frame, fake_frame, right_frame)
            loss_disc_fake = bce_loss(output_disc_fake, fake_is_real)

            discriminator_loss = 0.5 * (loss_disc_real + loss_disc_fake)
            discriminator_loss.backward()
            optimizer_disc.step()

            # Train the interpolator
            optimizer_gen.zero_grad()
            fake_frame = self.generator(left_frame, right_frame)
            
            output_disc_for_gen = self.discriminator(left_frame, fake_frame, right_frame)
            
            adversarial_loss = bce_loss(output_disc_for_gen, real_is_real)
            pixel_loss = mse_loss(fake_frame, interp_frame)
            
            generator_loss = 0.8 * adversarial_loss + 0.2 * pixel_loss
            generator_loss.backward()
            optimizer_gen.step()

            total_loss += generator_loss.item() * batch_size
            total_items += batch_size
            print("\r                                                                ", end="\r")
            print(f"{total_items}/{subset_size}", end="", flush=True)
        print("\r                                                                ", end="\r", flush=True)
        if total_items == 0:
            return 0.0
        average_loss = total_loss / total_items
        return average_loss
    
    def validate(self, dataset:data.Dataset, subset_size:int=None, batch_size:int=1):
        self.generator.eval()
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
                predicted_frame = self.generator(left_frame, right_frame)

                # Loss calculation
                loss = frame_loss(predicted_frame, interp_frame)
                total_loss += loss.item() * batch_size
                total_items += batch_size

        if total_items == 0:
            return 0.0
        average_loss = total_loss / total_items
        return average_loss

    def test(self, dataset:data.Dataset, subset_size:int=None, batch_size:int=1):
        self.generator.eval()
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
                predicted_frame = self.generator(left_frame, right_frame)

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

            #validate_loss = self.validate(val_dataset, batch_size=batch_size, subset_size=subset_size)
            #print(f"Validate step {epoch+1}; loss={validate_loss}")
            
            #epoch_losses.append((train_loss, validate_loss))
            epoch_losses.append(train_loss)
        #test_loss = self.test(test_dataset, batch_size=batch_size, subset_size=subset_size)
        #print(f"Testing finished; loss={validate_loss}")
        return epoch_losses#, test_loss

    def save_weights(self):
        torch.save(self.generator.state_dict(), self.weight_output_file)

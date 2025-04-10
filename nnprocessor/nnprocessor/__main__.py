import sys

import nnprocessor.interp.dataset as ds
import nnprocessor.interp.model as md
import nnprocessor.interp.train as tr
import nnprocessor.queue.client as qc

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

#def test_train():
#    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
#    svd = ds.SingleVideoDataset("train_data/test.mp4")
#    model = md.Interpolator()
#    trainer = tr.Trainer(model, device=device)
#    trainer.train(svd)
#
def fulltrain(model, discriminator):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    trainer = tr.Trainer("interp-gan.pt", model, discriminator, device=device)
    
    trainset = ds.VideoFolderDataset("train_data/train", csv_cache="train_data/train.csv")
    validateset = ds.VideoFolderDataset("train_data/validate", csv_cache="train_data/validate.csv")
    testset = ds.VideoFolderDataset("train_data/test", csv_cache="train_data/test.csv")
    
    print(trainer.run(trainset, testset, validateset, subset_size=5000, epochs=100, batch_size=12, autosave=True))

def queueclient(model):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    client = qc.QueueClient("/smb/ssd/process_queue/", model, torch.load("interp-gan.pt"), device)
    client.run()

def main() -> int:
    model = md.Interpolator().half()
    discriminator = md.Discriminator().half()
    fulltrain(model, discriminator)
    queueclient(model)
    return 0

if __name__ == '__main__':
    sys.exit(main())

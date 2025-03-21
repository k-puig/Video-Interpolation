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
#def test_fulltrain():
#    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
#    model = md.Interpolator()
#    trainer = tr.Trainer(model, device=device)
#    
#    trainset = ds.VideoFolderDataset("train_data/train")
#    validateset = ds.VideoFolderDataset("train_data/validate")
#    testset = ds.VideoFolderDataset("train_data/test")
#    
#    trainer.run(trainset, testset, validateset)
#
#def test_servertrain():
#    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
#    model = md.Interpolator()
#    trainer = tr.Trainer(model, device=device)
#    
#    trainset = ds.TensorServerDataset("http://localhost:8080", "train")
#    validateset = ds.TensorServerDataset("http://localhost:8080", "validate")
#    testset = ds.TensorServerDataset("http://localhost:8080", "test")
#    
#    trainer.run(trainset, testset, validateset, batch_size=16, shuffle_subset=5000)

def test_queueclient():
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = md.Interpolator()
    client = qc.QueueClient("process_queue/", model, device)
    client.run()

def main() -> int:
    test_queueclient()
    return 0

if __name__ == '__main__':
    sys.exit(main())
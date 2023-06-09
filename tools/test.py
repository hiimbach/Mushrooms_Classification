# This file is used to test functions and classes
import torch
import os
import sys
import torchvision
import matplotlib.pyplot as plt

ROOT = os.getcwd()
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))
    
from torch import nn, optim
from torchvision import models, transforms

from model.vit import  ViT
from utils.train_loop import TrainingLoop
from torchvision.models import resnet50, ResNet50_Weights
from utils.data_loader import data_split
 
 
model = resnet50(pretrained=False)
newfc = torch.nn.Linear(in_features=model.fc.in_features, out_features=9, bias=True)
model.fc = newfc


train_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(20),
    transforms.ColorJitter(brightness=0.1, contrast=0.1, saturation=0.1, hue=0.1),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])


val_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

data_path = "data/mushrooms"
batch_size = 4
loss_fn = nn.CrossEntropyLoss()  
optim_fn = optim.Adam

train_task = TrainingLoop(model, data_path, batch_size, loss_fn, optim_fn, 0.001, train_transform, val_transform)
# import ipdb
# ipdb.set_trace()

train_task.train(10, "test", 1)


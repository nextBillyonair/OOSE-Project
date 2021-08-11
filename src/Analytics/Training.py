import sys
import os
sys.path.append(os.path.abspath("../Backend"))
from app.models import *
from app.views.helperFunctions.scorer import FeaturesEnum
from app import db
from sqlalchemy.orm import aliased
from sqlalchemy import and_, func
import json
import enum

import random
import numpy as np
import argparse
import torch
import torch.utils.data
import torch.nn as nn
import torch.optim as optim
from torch.autograd import Variable
import pickle

logs = aliased(Logs.Logs)
fv = aliased(FeatureVectors.FeatureVectors)

class DataEnum(enum.IntEnum):
    fv = 0
    label = 1
    weight = 2

# Number of requests and number of clicks that don't lead to requests
def bestActionSubquery():
    subquery = db.session.query(logs.sid, logs.otherUserID, func.max(logs.action).label('action'))
    subquery = subquery.group_by(logs.sid, logs.otherUserID)
    subquery = subquery.subquery('bestAction')
    return subquery

# JOIN WITH feature_vectors (on SID and USERID)
def removeBluetoothUsers(table):
    subquery = db.session.query(table.c.action,fv.featureVector)
    subquery = subquery.join(fv, and_(fv.sid == table.c.sid, fv.otherUserID == table.c.otherUserID))
    return subquery

def maxFeaturesEnumVal():
    maximum = 0
    for a in FeaturesEnum:
        if a.value > maximum:
            maximum = a.value
    return maximum

def createTrainingData(maximum):
    # subquery = noBluetoothSubquery()
    subquery1 = bestActionSubquery()
    query = removeBluetoothUsers(subquery1)
    results = query.all()
    data = [] # contains (featureVector, label, weight)
    numZeros = 0
    numOnes = 0
    for res in results:

        featureVectorDict = res.featureVector
        featureVector = []
        for i in range(maximum + 1):
            featureVector.append(featureVectorDict.get(unicode(i), 0))

        if 'action' not in dir(res):
            # no click and no request
            data.append([featureVector, 0, 0.25])
            numZeros += 0.25
        elif res.action == Logs.ActionEnum.clicked:
            # clicked but no request
            data.append([featureVector, 0, 1.])
            numZeros += 1
        else:
            # click and then request
            data.append([featureVector, 1, 1.])
            numOnes += 1

    if numOnes == 0 or numZeros == 0:
        return data, numZeros, numOnes

    for i in range(len(data)):
        if data[i][int(DataEnum.label)] == 0:
            data[i][int(DataEnum.weight)] *= float(numOnes) / numZeros

    return data, numZeros, numOnes

# split data, randomly sample for eval with rate eval ratio 
def splitData(data, ratio):
    training_data = []
    validation_data = []

    for i in range(len(data)):
        if random.random() <= data[i][DataEnum.weight.value] * ratio:
            validation_data.append(data[i])
        else:
            training_data.append(data[i])
    return training_data, validation_data

parser = argparse.ArgumentParser(description='PyTorch MNIST Example')
parser.add_argument('--batch_size', type=int, default=2, metavar='N',
                    help='input batch size for training (default: 64)')
parser.add_argument('--epochs', type=int, default=1, metavar='N',
                    help='number of epochs to train (default: 2)')
parser.add_argument('--seed', type=int, default=1, metavar='S',
                    help='random seed (default: 1)')
parser.add_argument('--lr', type=float, default=1e-1,
                    help='learning rate (default: 1e-1)')
parser.add_argument('--valid_ratio', type=float, default=0.5,
                    help='ratio used for validation (default: 0.5)')
parser.add_argument("--save_model", default="footsie_model", type=str,
        help="The file containing already trained model.")

args = parser.parse_args()

torch.manual_seed(args.seed)
random.seed(args.seed)

data, numZeros, numOnes = createTrainingData(maxFeaturesEnumVal())
# print(data)
training_data, validation_data = splitData(data, args.valid_ratio)
print(training_data, validation_data)

class FootsieDataset(torch.utils.data.Dataset):
    """Face Landmarks dataset."""

    def __init__(self, data):
        self.data =  [(self.toFloatTensor(fv),self.toFloatTensor([l]), self.toFloatTensor([w])) for (fv,l,w) in data]

    def toFloatTensor(self, a):
        return torch.from_numpy(np.array(a)).type(torch.FloatTensor)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        real_cpu, y_class, weight = self.data[idx]
        return real_cpu, y_class, weight

class FootsieModel(nn.Module):
    def __init__(self):
        super(FootsieModel, self).__init__()
        self.fc = nn.Linear(maxFeaturesEnumVal() + 1, 1, bias=False)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        return self.sigmoid(self.fc(x))

train_dataloader = torch.utils.data.DataLoader(
    FootsieDataset(training_data), batch_size=args.batch_size, shuffle=True)

validation_dataloader = torch.utils.data.DataLoader(
    FootsieDataset(validation_data), batch_size=args.batch_size, shuffle=False)

model = FootsieModel()

optimizer = optim.SGD(model.parameters(), lr=args.lr)

for epoch in range(args.epochs):

    model.train()
    total_train_loss = 0
    for data, y_class, weight in train_dataloader:
        optimizer.zero_grad()
        data = Variable(data)
        y_class = Variable(y_class)
        print(y_class)
        train_loss = nn.BCELoss(weight=weight)(model(data), y_class)
        total_train_loss += train_loss
        train_loss.backward()
        optimizer.step()

    print('Epoch: {}, \tTotal Train Loss: {:.6f}'.format(
                    epoch, total_train_loss.data[0]))
    print('Epoch: {}, \tAverage Train Loss: {:.6f}'.format(
                    epoch, total_train_loss.data[0] / len(train_dataloader)))

    model.eval()
    total_valid_loss = 0
    for data, y_class, weight in validation_dataloader:
        data = Variable(data)
        y_class = Variable(y_class)

        valid_loss = nn.BCELoss(weight=weight)(model(data), y_class)
        total_valid_loss += valid_loss

    print('Epoch: {}, \tTotal Validation Loss: {:.6f}'.format(
                    epoch, total_valid_loss.data[0]))
    print('Epoch: {}, \tAverage Validation Loss: {:.6f}'.format(
                    epoch, total_valid_loss.data[0] / len(validation_dataloader)))

weights = model.fc.weight.data.numpy().tolist()[0]
zeroScores = []
oneScores = []
for data, y_class, _ in validation_data:
    score = 0
    for i, weight in enumerate(weights):
        score += weight * (data[i])
    if y_class == 0:
        zeroScores.append(score)
    else:
        oneScores.append(score)

zeroScores = np.array(zeroScores)
oneScores = np.array(oneScores)

print(" ")
print("Final Statistics")
print("Average Zero Score: {:.6f}".format(np.mean(zeroScores)))
print("Std Zero Score: {:.6f}".format(np.std(zeroScores)))
print("Average One Score: {:.6f}".format(np.mean(oneScores)))
print("Std One Score: {:.6f}".format(np.std(oneScores)))


pickle.dump(weights, open(args.save_model, 'wb'))
from Environment import Environment
import asyncio
import random

import numpy as np
from numpy.random import choice
import torch
import torch.nn as nn
import torch.nn.functional as F

EPSILON = 0.10
GAMME = 0.99
BATCH_SIZE = 10
MEMORY = []

class DQN(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(190, 256)
        self.fc2 = nn.Linear(256, 512)
        self.fc3 = nn.Linear(512, 512)
        self.fc4 = nn.Linear(512, 10)
    def forward(self, x):
        x = self.fc1(x)
        x = F.relu(x)
        x = self.fc2(x)
        x = F.relu(x)
        x = self.fc3(x)
        x = F.relu(x)
        x = self.fc4(x)
        x = F.relu(x)
        return x

def softmax_stable(x):
    return(np.exp(x - np.max(x)) / np.exp(x - np.max(x)).sum())

def choose_move(available, eval, EPSILON):
    if np.random.random() < EPSILON:
        available = available/np.sum(available)
    else:
        print(eval, available)
        available = [e if a else np.min(eval.numpy) for (e,a) in zip(eval.numpy(),available)] * available
        available = available/np.sum(available)
        print(available)
    return choice(range(10),p=available)

async def main():
    env = Environment()
    dqn = DQN()
    dqn.double()
    criterion = torch.nn.MSELoss()
    opt = torch.optim.Adam(dqn.parameters(), lr=0.01)

    await env.connect()
    count = 0
    while True:
        await env.start_game()
        print(env.game_name)
        state = 1
        while not env.state is None:
            state = env.state.getState()
            with torch.no_grad():
                eval = dqn(torch.from_numpy(state))
                move = choose_move(env.state.getAvailableMoves(),eval,EPSILON)
            moves = ['move 1','move 2','move 3','move 4','switch 1','switch 2','switch 3','switch 4','switch 5','switch 6']
            move_txt = moves[move]
            reward = await env.make_move(move_txt)
            next_state = env.state.getState() if not env.state is None else None

            MEMORY.append((state, move, reward, next_state))
            count += 1
            if count > 0:
                y_batch, y_target_batch = [], []
                minibatch = random.sample(MEMORY, min(len(MEMORY), BATCH_SIZE))
                for state, action, reward, next_state in minibatch:
                    y = dqn(torch.from_numpy(state))
                    y_target = y.clone().detach()
                    with torch.no_grad():
                        y_target[action] = reward if next_state is None else reward + GAMME * torch.max(dqn(torch.from_numpy(state)))
                    y_batch.append(y)
                    y_target_batch.append(y_target)
                
                y_batch = torch.cat(y_batch)
                y_target_batch = torch.cat(y_target_batch)
                
                opt.zero_grad()
                loss = criterion(y_batch, y_target_batch)
                loss.backward()
                opt.step()

if __name__ == "__main__":
    asyncio.run(main())
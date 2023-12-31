from Environment import Environment
import asyncio
import numpy as np
from numpy.random import choice

EPSILON = 0.05

def choose_move(avialble):
    moves = ['move 1','move 2','move 3','move 4','switch 1','switch 2','switch 3','switch 4','switch 5','switch 6']
    avialble = avialble/np.sum(avialble)
    return choice(moves,p=avialble)

async def main():
    env = Environment()
    await env.connect()
    while True:
        await env.start_game()
        print(env.game_name)
        state = 1
        while state:
            state = env.state
            # print(state)
            move = choose_move(state.getAvailableMoves())
            # await asyncio.sleep(5)
            reward = await env.make_move(move)
            next_state = env.state
            print(state.getState())
            print(move)
            print(next_state.getState() if next_state else '')
            print(reward)
            state = next_state

if __name__ == "__main__":
    asyncio.run(main())
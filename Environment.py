import random
import math

import asyncio
import websockets
import requests
import json
import numpy as np
from State import State


class Environment:
    def __init__(self):
        self.game_name = None
        self.state = None
        self.username = None

    async def connect(self):
        uri = 'ws://sim.smogon.com:8000/showdown/websocket'
        self.websocket = await websockets.connect(uri, ping_interval=None)
        
        # wait for challstr
        greeting = ''
        while not greeting.startswith('|challstr|'):
            greeting = await self.websocket.recv()
            # print(f'<<< {greeting}')

        # parse login request
        f = open('user.txt','r')
        usname = f.readline()
        self.username = usname
        passwd = f.readline()
        header = {'Content-type': 'application/x-www-form-urlencoded; encoding=UTF-8'}
        content = {'act': 'login', 'name': usname[:-1],'pass': passwd, 'challstr': greeting[10:]}

        # send the login request
        url = 'https://play.pokemonshowdown.com/~~showdown/action.php'
        r = requests.post(url,data=content,headers=header)
        s = json.loads(r.text[1:])
        l = '|/trn ' + usname[0:-1] +',0,' + s['assertion']
        # print(f'>>> {l}')
        await self.websocket.send(l)
        print('Done Connecting')

    async def start_game(self, use_ladder = False, start_challenge = True, user = 'Ruang'):
        if self.game_name:
            print('Game already in progress')
            return

        await self.websocket.send('|/challenge {}, gen1randombattle'.format(user))
        while True:
            greeting = await self.websocket.recv()
            # print(f'<<< {greeting}')
            if greeting.startswith('|updatesearch|'):
                s = json.loads(greeting[14:])
                if s['games']: # this will exist if there is a game going on
                    self.game_name = list(s['games'].keys())[0]
                    self.state = State()
                    break
        receivedRequest = False
        receivedChange = False
        while True:
            greeting = await self.websocket.recv()
            # print(f'<<< {greeting}')
            if greeting.startswith('>battle'):
                lines = greeting.split('\n')[1:]
                if lines[0].startswith('|request|') and lines[0] != '|request|': # request for move
                    self.state.updateSelf(json.loads(lines[0][9:]))
                    receivedRequest = True
                elif lines[0] == '|' or '|start' in lines: # battle update
                    self.state.parseChange(lines,self.username.strip())
                    receivedChange = True
                if receivedRequest and receivedChange:
                    return
    
    async def make_move(self, move):
        await self.websocket.send('{}|/choose {}'.format(self.game_name, move))
        print('Chose {}'.format(move))
        receivedRequest = False
        receivedChange = False
        while True:
            greeting = await self.websocket.recv()
            print(f'<<< {greeting}')
            if greeting.startswith('>battle'):
                lines = greeting.split('\n')[1:]
                if lines[-1].startswith('|win|'):
                    print(self.username,greeting,lines[-1])
                    self.game_name = None
                    self.state = None
                    return 1 if self.username.strip() in lines[-1] else -1
                if lines[0].startswith('|request|') and lines[0] != '|request|': # request for move
                    self.state.updateSelf(json.loads(lines[0][9:]))
                    receivedRequest = True
                elif lines[0] == '|' or '|start' in lines: # battle update
                    self.state.parseChange(lines,self.username.strip())
                    receivedChange = True
                if receivedRequest and receivedChange:
                    return 0
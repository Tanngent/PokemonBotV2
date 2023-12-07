from Pokemon import Pokemon

class State:
    def __init__(self):
        self.ownId = ''
        self.enemyId = ''
        self.ownActive = 0
        self.enemyActive = 0

        self.ownTeam = [Pokemon(), Pokemon(), Pokemon(), Pokemon(), Pokemon(), Pokemon()]
        self.enemyTeam = [Pokemon(), Pokemon(), Pokemon(), Pokemon(), Pokemon(), Pokemon()]

        self.forceSwitch = False
        self.trapped = False
        self.disabled = [False, False, False, False]
        
        self.ownTransform = -1
        self.enemyTransform = -1
        self.ownStatBoost = [0, 0, 0, 0]
        self.enemyStatBoost = [0, 0, 0, 0]

        self.parsableChanges = ['switch','move','-damage','-heal','faint','-status','-curestatus','-cureteam','-transform','-boost','-unboost',]

    def updateSelf(self,json):
        #print(json)
        #print(json['side'])
        #print(json['side']['pokemon'])

        #self.ownId = json['side']['id']
        #self.enemyId = 'p2' if self.ownId == 'p1' else 'p1'

        i = 0
        while(not json['side']['pokemon'][i]['active']):
            i += 1
        self.ownActive = i

        self.ownTeam[0].update(json['side']['pokemon'][0])
        self.ownTeam[1].update(json['side']['pokemon'][1])
        self.ownTeam[2].update(json['side']['pokemon'][2])
        self.ownTeam[3].update(json['side']['pokemon'][3])
        self.ownTeam[4].update(json['side']['pokemon'][4])
        self.ownTeam[5].update(json['side']['pokemon'][5])
        self.forceSwitch = 'forceSwitch' in json
        self.trapped = False
        if('active' in json):
            self.disabled[0] = False if 'disabled' not in json['active'][0]['moves'][0] else json['active'][0]['moves'][0]['disabled']
            self.disabled[1] = True if len(json['active'][0]['moves']) <= 1 else json['active'][0]['moves'][1]['disabled']
            self.disabled[2] = True if len(json['active'][0]['moves']) <= 2 else json['active'][0]['moves'][2]['disabled']
            self.disabled[3] = True if len(json['active'][0]['moves']) <= 3 else json['active'][0]['moves'][3]['disabled']
            self.trapped = 'trapped' in json['active'][0]

    def parseChange(self,change,name):
        # print(change)
        for line in change:
            parts = line[1:].split('|')
            #print(parts[0])
            #print(len(parts))
            #if len(parts)>=3:
            #    print(parts[2])
            #    print(name)
            #    print(parts[2] == name)
            if parts[0] == 'player' and len(parts)>=3 and parts[2] == name:
                self.ownId = parts[1]
                self.enemyId = 'p2' if self.ownId == 'p1' else 'p1'
            if parts[0] == 'player' and len(parts)>=3 and parts[2] != name:
                self.enemyId = parts[1]
                self.ownId = 'p2' if self.enemyId == 'p1' else 'p1'
            if parts and parts[0] in self.parsableChanges:
                #print(line)
                isOwn = parts[1].startswith(self.ownId)
                inPokemon = parts[1].split(' ')[1]
                match parts[0]:
                    case 'switch':
                        #print(parts[1])
                        #print(isOwn)
                        #print(self.ownId)
                        if isOwn:
                            self.ownTransform = -1
                            self.ownStatBoost = [0, 0, 0, 0]
                        else:
                            self.enemyTransform = -1
                            self.enemyStatBoost = [0, 0, 0, 0]
                            inInfo = parts[2].split(',')
                            inPokemon = inInfo[0]
                            inLevel = 100 if len(inInfo)==1 else inInfo[1].translate(str.maketrans('', '', 'L '))
                            self.enemyActive = 0
                            for pk in self.enemyTeam:
                                if pk.specie == inPokemon:
                                    break
                                if pk.specie == '':
                                    pk.specie = inPokemon
                                    pk.level = inLevel
                                    pk.getStats(inPokemon)
                                    break
                                self.enemyActive += 1
                    case 'move':
                        if not isOwn:
                            inMove = parts[2]
                            #print(inPokemon)
                            #print(inMove)
                            for pk in self.enemyTeam:
                                if pk.specie == inPokemon:
                                    for i in range(4):
                                        if pk.moves[i] == inMove:
                                            break
                                        if pk.moves[i] == '':
                                            pk.moves[i] = inMove
                                            break
                                    break
                    case '-damage':
                        if not isOwn:
                            inHealth = 0.0 if parts[2] == '0 fnt' else int(parts[2].split(' ')[0].split('/')[0])/int(parts[2].split(' ')[0].split('/')[1])
                            #print(inPokemon)
                            #print(inHealth)
                            for pk in self.enemyTeam:
                                if pk.specie == inPokemon:
                                    pk.health = inHealth
                                    break
                    case '-heal':
                        if not isOwn:
                            inHealth = 0.0 if parts[2] == '0 fnt' else int(parts[2].split(' ')[0].split('/')[0])/int(parts[2].split(' ')[0].split('/')[1])
                            #print(inPokemon)
                            #print(inHealth)
                            for pk in self.enemyTeam:
                                if pk.specie == inPokemon:
                                    pk.health = inHealth
                                    break
                    case 'faint':
                        if not isOwn:
                            for pk in self.enemyTeam:
                                if pk.specie == inPokemon:
                                    pk.health = 0.0
                                    pk.status = 'fnt'
                                    break
                    case '-status':
                        if not isOwn:
                            for pk in self.enemyTeam:
                                if pk.specie == inPokemon:
                                    pk.status = parts[2]
                                    break
                    case '-curstatus':
                        if not isOwn:
                            for pk in self.enemyTeam:
                                if pk.specie == inPokemon:
                                    pk.status = ''
                                    break
                    case '-cureteam':
                        if not isOwn:
                            for pk in self.enemyTeam:
                                pk.status = ''
                    case '-transform':
                        if isOwn:
                            self.ownTransform = self.enemyActive
                        else:
                            self.enemyTransform = self.ownActive
                    case '-boost':
                        if not isOwn:
                            if parts[2] == 'atk':
                                self.enemyStatBoost[0] += int(parts[3])
                            if parts[2] == 'def':
                                self.enemyStatBoost[1] += int(parts[3])
                            if parts[2] == 'spa':
                                self.enemyStatBoost[2] += int(parts[3])
                            if parts[2] == 'spe':
                                self.enemyStatBoost[3] += int(parts[3])
                        if isOwn:
                            if parts[2] == 'atk':
                                self.ownStatBoost[0] += int(parts[3])
                            if parts[2] == 'def':
                                self.ownStatBoost[1] += int(parts[3])
                            if parts[2] == 'spa':
                                self.ownStatBoost[2] += int(parts[3])
                            if parts[2] == 'spe':
                                self.ownStatBoost[3] += int(parts[3])
                    case '-unboost':
                        if not isOwn:
                            if parts[2] == 'atk':
                                self.enemyStatBoost[0] -= int(parts[3])
                            if parts[2] == 'def':
                                self.enemyStatBoost[1] -= int(parts[3])
                            if parts[2] == 'spa':
                                self.enemyStatBoost[2] -= int(parts[3])
                            if parts[2] == 'spe':
                                self.enemyStatBoost[3] -= int(parts[3])
                        if isOwn:
                            if parts[2] == 'atk':
                                self.ownStatBoost[0] -= int(parts[3])
                            if parts[2] == 'def':
                                self.ownStatBoost[1] -= int(parts[3])
                            if parts[2] == 'spa':
                                self.ownStatBoost[2] -= int(parts[3])
                            if parts[2] == 'spe':
                                self.ownStatBoost[3] -= int(parts[3])
                    case _:
                        pass

    def getAvailableMoves(self):
        validMoves = [0 for _ in range(10)]
        for i in range(4):
            if not self.disabled[i] and not self.forceSwitch:
                validMoves[i] = 1
        for i in range(6):
            if i != self.ownActive and self.ownTeam[i].status != 'fnt' and not self.trapped:
                validMoves[i+4] = 1
        if self.trapped:
            validMoves
        return validMoves

    def __str__(self):
        return 'Own Id: ' + str(self.ownId) + '\nEnemy Id: ' + str(self.enemyId) + '\n'\
        + self.ownTeam[0].__str__() + '\n' + self.ownTeam[1].__str__() + '\n' + self.ownTeam[2].__str__() + '\n' + self.ownTeam[3].__str__()\
             + '\n' + self.ownTeam[4].__str__() + '\n' + self.ownTeam[5].__str__() + '\nOwn Active: ' + str(self.ownActive) + '\nForce Switch: ' + str(self.forceSwitch)\
                + '\nTrapped: ' + str(self.trapped) + '\nOwn Transform: ' + str(self.ownTransform) + '\nDisabled: ' + str(self.disabled[0]) + ':' + str(self.disabled[1]) + ':' + str(self.disabled[2]) + ':' + str(self.disabled[3])\
                    + '\nOwn Stats: ' + str(self.ownStatBoost[0]) + ':' + str(self.ownStatBoost[1]) + ':' + str(self.ownStatBoost[2]) + ':' + str(self.ownStatBoost[3])\
                        + '\n' + self.enemyTeam[0].__str__() + '\n' + self.enemyTeam[1].__str__() + '\n' + self.enemyTeam[2].__str__() + '\n' + self.enemyTeam[3].__str__()\
                            + '\n' + self.enemyTeam[4].__str__() + '\n' + self.enemyTeam[5].__str__() + '\nEnemy Active: ' + str(self.enemyActive) + '\nEnemy Transform: ' + str(self.enemyTransform)\
                                + '\nEnemy Stats: ' + str(self.enemyStatBoost[0]) + ':' + str(self.enemyStatBoost[1]) + ':' + str(self.enemyStatBoost[2]) + ':' + str(self.enemyStatBoost[3])

import json as js

class Pokemon:
    def __init__(self):
        self.specie = ''
        self.level = 100
        self.health = 1.0
        self.status = ''
        self.moves = ['','','','']
        self.atk = 0
        self.defe = 0
        self.spa = 0
        self.spd = 0
        self.spe = 0

    # Update state of party pokemon from JSON
    def update(self,json):
        #print(json)
        self.specie = json['details'].split(',')[0].translate(str.maketrans('', '', ' '))
        self.level = 100 if len(json['details'].split(',')) == 1 else int(json['details'].split(',')[1].translate(str.maketrans('', '', 'L ')))
        self.health = 0.0 if json['condition'].split(' ')[0] == '0' else int(json['condition'].split(' ')[0].split('/')[0])/int(json['condition'].split(' ')[0].split('/')[1])
        self.status = '' if len(json['condition'].split(' ')) == 1 else json['condition'].split(' ')[1]
        self.moves[0] = json['moves'][0]
        self.moves[1] = '' if len(json['moves']) <= 1 else json['moves'][1]
        self.moves[2] = '' if len(json['moves']) <= 2 else json['moves'][2]
        self.moves[3] = '' if len(json['moves']) <= 3 else json['moves'][3]
        self.atk = json['stats']['atk']
        self.defe = json['stats']['def']
        self.spa = json['stats']['spa']
        self.spd = json['stats']['spd']
        self.spe = json['stats']['spe']

    # Update state of enemy pokemon from text
    def getStats(self,specie):
        f = open('stats.json')
        json = js.load(f)
        self.atk = json[specie][0]
        self.defe = json[specie][1]
        self.spa = json[specie][2]
        self.spd = json[specie][3]
        self.spe = json[specie][4]
        f.close()

    def __str__(self):
        return str(self.specie) + ',' + str(self.level) + ',' + str(self.health) + ',' + self.status + ',' + self.moves[0]\
            + ',' + self.moves[1] + ',' + self.moves[2] + ',' + self.moves[3] + ',' + str(self.atk) + ',' + str(self.defe)\
                 + ',' + str(self.spa)  + ',' + str(self.spd)  + ',' + str(self.spe)
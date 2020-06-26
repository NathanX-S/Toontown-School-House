from otp.level.EntityTypes import *

class CogdoLevelMgr(LevelMgr):
    type = 'levelMgr'


class CogdoBoardroomGameSettings(Entity):
    type = 'cogdoBoardroomGameSettings'
    attribs = (('TimerScale', 1.0, 'float'),)


class CogdoCraneGameSettings(Entity):
    type = 'cogdoCraneGameSettings'
    attribs = (('GameDuration', 120, 'float'),
     ('EmptyFrictionCoef', 0.2, 'float'),
     ('Gravity', -32, 'int'),
     ('RopeLinkMass', 1.0, 'float'),
     ('MagnetMass', 1.0, 'float'),
     ('MoneyBagGrabHeight', -8.2, 'float'))


class CogdoCraneCogSettings(Entity):
    type = 'cogdoCraneCogSettings'
    attribs = (('CogSpawnPeriod', 10.0, 'float'),
     ('CogWalkSpeed', 2.0, 'float'),
     ('CogMachineInteractDuration', 2.0, 'float'))

from otp.level.EntityTypes import *

class CogdoLevelMgr(LevelMgr):
    type = 'levelMgr'


class CogdoBoardroomGameSettings(Entity):
    type = 'cogdoBoardroomGameSettings'
    attribs = (('TimerScale', 1.0, 'float'),)


class CogdoCraneGameSettings(Entity):
    type = 'cogdoCraneGameSettings'
    attribs = (('GameDuration', 120, 'float'),
     ('CogSpawnPeriod', 10.0, 'float'),
     ('EmptyFrictionCoef', 0.2, 'float'),
     ('Gravity', -32, 'int'),
     ('RopeLinkMass', 1.0, 'float'),
     ('MagnetMass', 1.0, 'float'),
     ('MoneyBagGrabHeight', -4.25, 'float'),
     ('MoneyBagAmount', 20, 'int'),
     ('CogDiedEvent', 'CraneCog_Died', 'str'))


class CogdoCraneCogSettings(Entity):
    type = 'cogdoCraneCogSettings'
    attribs = (('CogWalkSpeed', 2.0, 'float'),
     ('CogMachineInteractDuration', 0.5, 'float'))

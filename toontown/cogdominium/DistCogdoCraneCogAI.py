from direct.distributed.ClockDelta import globalClockDelta
from toontown.suit.DistributedSuitAI import DistributedSuitAI

class DistCogdoCraneCogAI(DistributedSuitAI):

    def __init__(self, air, game, dna, entranceId, spawnTime):
        DistributedSuitAI.__init__(self, air)
        self._gameId = game.doId
        self._dna = dna
        self._entranceId = entranceId
        self._spawnTime = spawnTime

    def getGameId(self):
        return self._gameId

    def getDNAString(self):
        return self._dna.makeNetString()

    def getSpawnInfo(self):
        return (self._entranceId, globalClockDelta.localToNetworkTime(self._spawnTime))

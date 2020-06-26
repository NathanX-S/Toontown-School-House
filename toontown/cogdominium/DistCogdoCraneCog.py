from panda3d.core import *
from direct.distributed.ClockDelta import globalClockDelta
from direct.distributed.DistributedObject import DistributedObject
from direct.interval import IntervalGlobal as IG
from toontown.cogdominium import CogdoCraneGameGlobals as Globals
from toontown.suit.DistributedSuit import DistributedSuit


class DistCogdoCraneCog(DistributedSuit):

    def __init__(self, cr):
        DistributedSuit.__init__(self, cr)
        self._moveIval = None
        return

    def setGameId(self, gameId):
        self._gameId = gameId

    def getGame(self):
        return self.cr.doId2do.get(self._gameId)

    def setSpawnInfo(self, entranceId, timestamp):
        self.initializeBodyCollisions('suit')
        self.setName('cog-%s' % self.doId)
        self.setTag('doId', str(self.doId))
        self.collNode.setName('cog')
        self._startMoveIval(entranceId, globalClockDelta.networkToLocalTime(timestamp))

    def _startMoveIval(self, entranceId, startT):
        self._stopMoveIval()
        game = self.getGame().game
        unitVecs = (Vec3(45, 0, 6.038),
         Vec3(0, 45, 6.038),
         Vec3(-45, 0, 6.038),
         Vec3(0, -45, 6.038))
        startPos = unitVecs[entranceId]
        endPos = Vec3(startPos.getX() * 0.1, startPos.getY() * 0.1, 6.038)
        walkDur = (endPos - startPos).length() / Globals.CogSettings.CogWalkSpeed.get()
        sceneRoot = game.getSceneRoot()
        moveIval = IG.Sequence(IG.Func(self.reparentTo, sceneRoot), IG.Func(self.setPos, startPos),
                               IG.Func(self.lookAt, game.stompOMatic), IG.Func(self.loop, 'walk'),
                               IG.LerpPosInterval(self, walkDur, endPos, startPos=startPos))
        interactIval = IG.Sequence(IG.ActorInterval(self, 'pickpocket'),
                                   IG.Wait(Globals.CogSettings.CogMachineInteractDuration.get()))
        flyIval = self.beginSupaFlyMove(endPos, 0, 'flyAway')
        self._moveIval = IG.Sequence(moveIval, interactIval, flyIval, IG.Wait(5))
        self._moveIval.start(globalClock.getFrameTime() - startT)

    def _getFlyAwayDest(self):
        return self.getPos() + Vec3(0, 0, Globals.CogSettings.CogFlyAwayHeight.get())

    def _stopMoveIval(self):
        if self._moveIval:
            self._moveIval.finish()
            self._moveIval = None
        return

    def disable(self):
        self._stopMoveIval()
        DistributedObject.disable(self)

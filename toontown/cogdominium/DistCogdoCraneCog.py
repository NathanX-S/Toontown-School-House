from panda3d.core import *
from direct.distributed.ClockDelta import globalClockDelta
from direct.distributed.DistributedObject import DistributedObject
from direct.interval import IntervalGlobal as IG
from toontown.cogdominium import CogdoCraneGameGlobals as Globals
from toontown.suit.Suit import Suit


class DistCogdoCraneCog(Suit, DistributedObject):

    def __init__(self, cr):
        DistributedObject.__init__(self, cr)
        Suit.__init__(self)
        self._moveIval = None
        return

    def setGameId(self, gameId):
        self._gameId = gameId

    def getGame(self):
        return self.cr.doId2do.get(self._gameId)

    def setSpawnInfo(self, entranceId, timestamp):
        self._startMoveIval(entranceId, globalClockDelta.networkToLocalTime(timestamp))

    def _startMoveIval(self, entranceId, startT):
        self._stopMoveIval()
        unitVecs = (Vec3(45, 0, 6.038),
         Vec3(0, 45, 6.038),
         Vec3(-45, 0, 6.038),
         Vec3(0, -45, 6.038))
        startPos = unitVecs[entranceId]
        endPos = Vec3(0, 0, 6.038)
        walkDur = (endPos - startPos).length() / Globals.CogSettings.CogWalkSpeed.get()
        sceneRoot = self.getGame().game.getSceneRoot()
        moveIval = IG.Sequence(IG.Func(self.reparentTo, sceneRoot), IG.Func(self.setPos, startPos),
                               IG.Func(self.lookAt, sceneRoot), IG.Func(self.loop, 'walk'),
                               IG.LerpPosInterval(self, walkDur, endPos, startPos=startPos))
        interactIval = IG.Sequence(IG.Func(self.loop, 'neutral'),
                                   IG.Wait(Globals.CogSettings.CogMachineInteractDuration.get()))
        flyIval = IG.Sequence(IG.Func(self.pose, 'landing', 0),
                              IG.LerpPosInterval(self, Globals.CogSettings.CogFlyAwayDuration.get(),
                                                 self._getFlyAwayDest, blendType='easeIn'))
        self._moveIval = IG.Sequence(moveIval, interactIval, flyIval)
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

    def delete(self):
        Suit.delete(self)
        DistributedObject.delete(self)

    def setDNAString(self, dnaString):
        Suit.setDNAString(self, dnaString)

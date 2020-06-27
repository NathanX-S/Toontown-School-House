from panda3d.core import *
from direct.directnotify.DirectNotifyGlobal import directNotify
from toontown.cogdominium.DistCogdoGameAI import DistCogdoGameAI
from toontown.cogdominium.DistCogdoCraneAI import DistCogdoCraneAI
from toontown.cogdominium import CogdoCraneGameGlobals as Globals
from toontown.cogdominium import CogdoGameConsts
from toontown.cogdominium.DistCogdoCraneMoneyBagAI import DistCogdoCraneMoneyBagAI
from toontown.cogdominium.DistCogdoCraneCogAI import DistCogdoCraneCogAI
from toontown.cogdominium.DistCogdoCraneObstacleAI import DistCogdoCraneObstacleAI
from toontown.suit.SuitDNA import SuitDNA
import random


class DistCogdoCraneGameAI(DistCogdoGameAI, NodePath):
    notify = directNotify.newCategory('DistCogdoCraneGameAI')

    def __init__(self, air, interior):
        DistCogdoGameAI.__init__(self, air, interior)
        NodePath.__init__(self, uniqueName('CraneGameAI'))

        self._cranes = [None] * CogdoGameConsts.MaxPlayers
        self._moneyBagCounter = 0
        self._moneyBags = [None] * 4
        self._cogs = []

        self._moneyBagsRespawnEvent = None
        self._gameDoneEvent = None
        self._finishDoneEvent = None

    def delete(self):
        DistCogdoGameAI.delete(self)
        self.removeNode()

    def enterLoaded(self):
        DistCogdoGameAI.enterLoaded(self)

        self.scene = NodePath('scene')
        cn = CollisionNode('walls')
        cs = CollisionSphere(0, 0, 0, 13)
        cn.addSolid(cs)
        cs = CollisionInvSphere(0, 0, 0, 42)
        cn.addSolid(cs)
        self.attachNewNode(cn)

        for i in xrange(CogdoGameConsts.MaxPlayers):
            crane = DistCogdoCraneAI(self.air, self, i)
            crane.generateWithRequired(self.zoneId)
            self._cranes[i] = crane

        for i in xrange(len(self._moneyBags)):
            mBag = DistCogdoCraneMoneyBagAI(self.air, self, i)
            mBag.generateWithRequired(self.zoneId)
            self._moneyBags[i] = mBag

    def exitLoaded(self):
        for bag in self._moneyBags:
            if bag:
                bag.requestDelete()
                bag = None

        for crane in self._cranes:
            if crane:
                crane.requestDelete()
                crane = None

        DistCogdoGameAI.exitLoaded(self)

    def enterGame(self):
        DistCogdoGameAI.enterGame(self)
        for i in xrange(self.getNumPlayers()):
            self._cranes[i].request('Controlled', self.getToonIds()[i])

        for bag in self._moneyBags:
            if bag:
                bag.request('Initial')

        self._moneyBagsRespawnEvent = taskMgr.doMethodLater(Globals.MoneyBagsRespawnRate, self.generateMoneyBags,
                                                             self.uniqueName('generateMoneyBags'))
        self._cogRespawnEvent = taskMgr.add(self.generateCog, self.uniqueName('respawnCog'))

        self._spotlightObstacle = DistCogdoCraneObstacleAI(self.air, self)
        self._spotlightObstacle.generateWithRequired(self.zoneId)
        duration = Globals.Settings.GameDuration.get()

        self._resistanceIncomingEvent = taskMgr.doMethodLater(duration / 2.0, self._resistanceIncoming, self.uniqueName('resistanceIncoming'))
        self._gameDoneEvent = taskMgr.doMethodLater(duration, self._gameDoneDL, self.uniqueName('craneGameDone'))

    def generateCog(self, task):
        task.delayTime = Globals.Settings.CogSpawnPeriod.get()
        cog = DistCogdoCraneCogAI(self.air, self, self.getDroneCogDNA(), random.randrange(4), globalClock.getFrameTime())
        cog.generateWithRequired(self.zoneId)
        self._cogs.append(cog)
        return task.again

    def generateMoneyBags(self, task):
        moneyBagsToSpawn = range(0, self.getNumPlayers())
        existingMoneyBags = []
        for moneyBag in self._moneyBags:
            index = moneyBag.getIndex()
            existingMoneyBags.append(index)

        moneyBagsToSpawn = [x for x in moneyBagsToSpawn if x not in existingMoneyBags]

        for i in moneyBagsToSpawn:
            mBag = DistCogdoCraneMoneyBagAI(self.air, self, i)
            mBag.generateWithRequired(self.zoneId)
            mBag.request('Join')
            self._moneyBags.insert(i, mBag)

        return task.again

    def exitGame(self):
        for cog in self._cogs:
            cog.requestDelete()
            cog = None

        self._spotlightObstacle.requestDelete()
        del self._spotlightObstacle

        taskMgr.remove(self._moneyBagsRespawnEvent)
        self._moneyBagsRespawnEvent = None

        taskMgr.remove(self._cogRespawnEvent)
        self._cogRespawnEvent = None

        taskMgr.remove(self._gameDoneEvent)
        self._gameDoneEvent = None

        taskMgr.remove(self._resistanceIncomingEvent)
        self._resistanceIncomingEvent = None

    def _gameDoneDL(self, task = None):
        self._handleGameFinished()
        return task.done

    def enterFinish(self):
        DistCogdoGameAI.enterFinish(self)
        self._finishDoneEvent = taskMgr.doMethodLater(10.0, self._finishDoneDL, self.uniqueName('craneFinishDone'))

    def exitFinish(self):
        taskMgr.remove(self._finishDoneEvent)
        self._finishDoneEvent = None

    def _finishDoneDL(self, task):
        self.announceGameDone()
        return task.done

    def _resistanceIncoming(self, task):
        self.sendUpdate('resistanceIncoming')
        return task.done

    def getDroneCogDNA(self):
        dna = SuitDNA()
        dna.newSuitRandom(level = random.randint(1, 3))
        return dna

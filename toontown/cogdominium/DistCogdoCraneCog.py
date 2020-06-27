from panda3d.core import *
from direct.distributed.ClockDelta import globalClockDelta
from direct.distributed.DistributedObject import DistributedObject
from direct.fsm import ClassicFSM, State
from direct.interval.IntervalGlobal import *
from toontown.battle import BattleParticles
from toontown.battle import MovieUtil
from toontown.cogdominium import CogdoCraneGameGlobals as Globals
from toontown.suit.DistributedSuit import DistributedSuit


class DistCogdoCraneCog(DistributedSuit):
    def __init__(self, cr):
        DistributedSuit.__init__(self, cr)
        self.fsm = ClassicFSM.ClassicFSM('DistributedSuit', [State.State('Off', self.enterOff, self.exitOff, ['Walk']),
         State.State('FlyAway', self.enterFlyAway, self.exitFlyAway, ['Off']),
         State.State('Walk', self.enterWalk, self.exitWalk, ['Interact', 'Off']),
         State.State('Interact', self.enterInteract, self.exitInteract, ['Off', 'FlyAway'])], 'Off', 'Off')
        self.fsm.enterInitialState()
        self._moveIval = None
        self._deathSoundIval = None
        return

    def setGameId(self, gameId):
        self._gameId = gameId

    def getGame(self):
        return self.cr.doId2do.get(self._gameId).game

    def setSpawnInfo(self, entranceId, timestamp):
        self.initializeBodyCollisions('suit')
        self.setName('cog-%s' % self.doId)
        self.setTag('doId', str(self.doId))
        self.deathSuit = self.getLoseActor()
        self.deathSuit.pose('lose', 0)
        audioMgr = self.getGame().audioMgr
        self._deathSoundIval = Sequence(audioMgr.createSfxIval('cogSpin', duration=1.6, startTime=0.6, volume=0.8, source=self.deathSuit), audioMgr.createSfxIval('cogDeath', volume=0.32, source=self.deathSuit))
        self.collNode.setName('cog')
        self.fsm.request('Walk', (entranceId, globalClockDelta.networkToLocalTime(timestamp))) #move it, please?

    def enterWalk(self, entranceId, startT):
        self._stopMoveIval()
        self.hideNametag3d()
        game = self.getGame()
        unitVecs = (Vec3(45, 0, 6.038),
         Vec3(0, 45, 6.038),
         Vec3(-45, 0, 6.038),
         Vec3(0, -45, 6.038))
        startPos = unitVecs[entranceId]
        endPos = Vec3(startPos.getX() * 0.1, startPos.getY() * 0.1, 6.038)
        walkDur = (endPos - startPos).length() / Globals.CogSettings.CogWalkSpeed.get()
        sceneRoot = game.getSceneRoot()
        moveIval = Sequence(Func(self.reparentTo, sceneRoot), Func(self.setPos, startPos),
                               Func(self.lookAt, game.stompOMatic), Func(self.loop, 'walk'),
                               LerpPosInterval(self, walkDur, endPos, startPos=startPos))
        interactIval = Sequence(Func(self.fsm.request, 'Interact'), Func(game.coinSfx.play), ActorInterval(self, 'pickpocket'),
                                   Wait(Globals.CogSettings.CogMachineInteractDuration.get()), Func(self.fsm.request, 'FlyAway'))
        self._moveIval = Sequence(moveIval, interactIval)
        self._moveIval.start(globalClock.getFrameTime() - startT)

    def exitWalk(self):
        pass

    def enterInteract(self):
        pass

    def exitInteract(self):
        pass

    def _stopMoveIval(self):
        if self._moveIval:
            self._moveIval.pause()
            self._moveIval = None
        return

    def explode(self):
        self._stopMoveIval()
        self.doDeathTrack()
        messenger.send(Globals.Settings.CogDiedEvent.get(), [self]) #We're done flyin'. Tell it we're dead.

    def doDeathTrack(self):

        def removeDeathSuit(suit, deathSuit):
            if not deathSuit.isEmpty():
                deathSuit.detachNode()
                suit.cleanupLoseActor()

        self.deathSuit.reparentTo(self.getParent())
        self.deathSuit.setScale(self.getScale())
        self.deathSuit.setPos(self.getPos())
        self.deathSuit.setHpr(self.getHpr())
        self.hide()
        self.collNodePath.reparentTo(self.deathSuit)
        gearPoint = Point3(0, 0, self.height / 2.0 + 2.0)
        smallGears = BattleParticles.createParticleEffect(file='gearExplosionSmall')
        singleGear = BattleParticles.createParticleEffect('GearExplosion', numParticles=1)
        smallGearExplosion = BattleParticles.createParticleEffect('GearExplosion', numParticles=10)
        bigGearExplosion = BattleParticles.createParticleEffect('BigGearExplosion', numParticles=30)
        smallGears.setPos(gearPoint)
        singleGear.setPos(gearPoint)
        smallGearExplosion.setPos(gearPoint)
        bigGearExplosion.setPos(gearPoint)
        smallGears.setDepthWrite(False)
        singleGear.setDepthWrite(False)
        smallGearExplosion.setDepthWrite(False)
        bigGearExplosion.setDepthWrite(False)
        suitTrack = Sequence(Func(self.collNodePath.stash), ActorInterval(self.deathSuit, 'lose', startFrame=80, endFrame=140), Func(removeDeathSuit, self, self.deathSuit, name='remove-death-suit'))
        explosionTrack = Sequence(Wait(1.5), MovieUtil.createKapowExplosionTrack(self.deathSuit, explosionPoint=gearPoint))
        gears1Track = Sequence(ParticleInterval(smallGears, self.deathSuit, worldRelative=0, duration=4.3, cleanup=True), name='gears1Track')
        gears2MTrack = Track((0.0, explosionTrack), (0.7, ParticleInterval(singleGear, self.deathSuit, worldRelative=0, duration=5.7, cleanup=True)), (5.2, ParticleInterval(smallGearExplosion, self.deathSuit, worldRelative=0, duration=1.2, cleanup=True)), (5.4, ParticleInterval(bigGearExplosion, self.deathSuit, worldRelative=0, duration=1.0, cleanup=True)), name='gears2MTrack')

        def removeParticle(particle):
            if particle and hasattr(particle, 'renderParent'):
                particle.cleanup()
                del particle

        removeParticles = Sequence(Func(removeParticle, smallGears), Func(removeParticle, singleGear), Func(removeParticle, smallGearExplosion), Func(removeParticle, bigGearExplosion))
        self.deathTrack = Sequence(Parallel(suitTrack, gears2MTrack, gears1Track, self._deathSoundIval), removeParticles)
        self.deathTrack.start()

    def disable(self):
        self.fsm.request('Off')
        DistributedObject.disable(self)

from panda3d.core import *
from direct.interval.IntervalGlobal import *
from direct.directnotify import DirectNotifyGlobal
from toontown.battle import BattleParticles
from toontown.toonbase import ToontownGlobals
from otp.otpbase import OTPGlobals
from toontown.cogdominium.DistCogdoCraneObject import DistCogdoCraneObject
from toontown.cogdominium import CogdoCraneGameGlobals as Globals
from CogdoCraneGameMovies import CogdoCraneGameIntro, CogdoCraneGameFinish


class DistCogdoCraneMoneyBag(DistCogdoCraneObject):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistCogdoCraneMoneyBag')
    grabPos = (0, 0, Globals.Settings.MoneyBagGrabHeight.get())
    craneFrictionCoef = 0.2
    craneSlideSpeed = 11
    craneRotateSpeed = 16
    wantsWatchDrift = 0

    def __init__(self, cr):
        DistCogdoCraneObject.__init__(self, cr)
        NodePath.__init__(self, 'object')
        self.index = None
        self.flyToMagnetSfxSoundInterval = self.audioMgr.createSfxIval('flyToMagnetSfx', duration=ToontownGlobals.CashbotBossToMagnetTime, source=self)
        self.hitMagnetSfxSoundInterval = self.audioMgr.createSfxIval('hitMagnetSfx', duration=1.0, source=self)
        self.toMagnetSoundInterval = Parallel(self.flyToMagnetSfxSoundInterval, Sequence(Wait(ToontownGlobals.CashbotBossToMagnetTime - 0.02), self.hitMagnetSfxSoundInterval))
        self.hitFloorSoundInterval = self.audioMgr.createSfxIval('hitFloorSfx', source=self)
        self.destroySfxSoundInterval = self.audioMgr.createSfxIval('destroySfx', source=self)
        return

    def announceGenerate(self):
        DistCogdoCraneObject.announceGenerate(self)
        self.name = 'moneyBag-%s' % self.doId
        self.setName(self.name)
        self.craneGame.game.moneyBag.copyTo(self)
        self.shadow = render.attachNewNode('shadow')
        shadowNode = self.find('**/MonetBagShadoww')
        shadowNode.reparentTo(self.shadow)
        self.collisionNode.setName('moneyBag')
        cs = CollisionSphere(0, 0, 0, 2)
        self.collisionNode.addSolid(cs)
        self.craneGame.moneyBags[self.index] = self
        self.setupPhysics('moneyBag')
        self.resetToInitialPosition()
        self.shadow.setPos(self.getPos())
        del shadowNode

    def disable(self):
        del self.craneGame.moneyBags[self.index]
        DistCogdoCraneObject.disable(self)

    def hideShadows(self):
        self.shadow.hide()

    def showShadows(self):
        self.shadow.show()

    def getMinImpact(self):
        if self.craneGame.heldObject:
            return ToontownGlobals.CashbotBossSafeKnockImpact
        else:
            return ToontownGlobals.CashbotBossSafeNewImpact

    def resetToInitialPosition(self):
        posHpr = Globals.MoneyBagPosHprs[self.index]
        self.setPosHpr(*posHpr)
        self.physicsObject.setVelocity(0, 0, 0)

    def fellOut(self):
        self.deactivatePhysics()
        self.d_requestInitial()

    def setIndex(self, index):
        self.index = index

    def setObjectState(self, state, avId, craneId):
        if state == 'I':
            self.demand('Initial')
        elif state == 'J':
            self.demand('Join')
        else:
            DistCogdoCraneObject.setObjectState(self, state, avId, craneId)

    def d_requestInitial(self):
        self.sendUpdate('requestInitial')

    def enterInitial(self):
        self.resetToInitialPosition()
        self.showShadows()

    def exitInitial(self):
        pass

    if __dev__:

        def _handleMoneyBagGrabHeightChanged(self, height):
            grabPos = DistCogdoCraneMoneyBag.grabPos
            DistCogdoCraneMoneyBag.grabPos = (grabPos[0], grabPos[1], height)

    def b_destroyMoneyBag(self):
        if not self.cleanedUp:
            self.d_destroyMoneyBag()
            self.destroyMoneyBag()

    def d_destroyMoneyBag(self):
        self.sendUpdate('destroyMoneyBag', [])

    def destroyMoneyBag(self):
        if not self.cleanedUp:
            self.playDestroyMovie()
        self.demand('Off')
        return

    def playDestroyMovie(self):
        bigGearExplosion = BattleParticles.createParticleEffect('CoinExplosion', numParticles=60)
        bigGearExplosion.setDepthWrite(False)

        pos = self.getPos()
        geom = self.craneGame.game.getSceneRoot()
        explosionPoint = geom.attachNewNode('moneyBagsExplosion_' + str(self.index))
        explosionPoint.setPos(pos)
        Parallel(self.destroySfxSoundInterval,
             ParticleInterval(bigGearExplosion, explosionPoint, worldRelative=0, duration=2.0, cleanup=True)).start()

        self.shadow.removeNode()
        del self.shadow

    def enterSlidingFloor(self, avId):
        DistCogdoCraneObject.enterSlidingFloor(self, avId)
        self.b_destroyMoneyBag()

    def enterJoin(self):
        initialPosition = Globals.MoneyBagPosHprs[self.index]
        x, y, z, h, p, r = initialPosition
        self.setPosHpr(x, y, z + Globals.MoneyBagsJoinHeight, h, p, r)
        self.shadow.setScale(0.001)
        self.shadow.setColorScale(1, 1, 1, 0)
        Sequence(
            Parallel(
                self.shadow.colorScaleInterval(0.4, (1, 1, 1, 1)),
                self.shadow.scaleInterval(0.6, (1.1, 1.1, 1.1)),
                self.posInterval(0.7, (x, y, z)),
            ),
            self.hitFloorSoundInterval,
            self.scaleInterval(0.08, (1, 1, 0.5)),
            Parallel(
                self.scaleInterval(0.13, (1, 1, 1.20)),
                self.posHprInterval(0.12, (x, y, z + 2), (0, 0, 3)),
            ),
            self.hprInterval(0.1, (0, 0, -3)),
            Parallel(
                self.posHprInterval(0.13, (x, y, z), (0, 0, 0)),
                self.scaleInterval(0.12, (1, 1, 1))
            ),
        ).start()

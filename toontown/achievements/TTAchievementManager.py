from direct.distributed.DistributedObjectGlobal import DistributedObjectGlobal
from direct.directnotify.DirectNotifyGlobal import directNotify

class TTAchievementManager(DistributedObjectGlobal):
    notify = directNotify.newCategory('TTAchievementManager')

    def __init__(self, cr):
        DistributedObjectGlobal.__init__(self, cr)

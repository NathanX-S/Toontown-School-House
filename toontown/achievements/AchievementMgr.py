from direct.distributed.DistributedObjectGlobal import DistributedObjectGlobal
from direct.directnotify.DirectNotifyGlobal import directNotify

class AchievementMgr(DistributedObjectGlobal):
    notify = directNotify.newCategory('AchievementMgr')

    def __init__(self, cr):
        DistributedObjectGlobal.__init__(self, cr)

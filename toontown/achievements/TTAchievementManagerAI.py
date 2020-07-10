from direct.distributed.DistributedObjectGlobalAI import DistributedObjectGlobalAI
from direct.directnotify.DirectNotifyGlobal import directNotify

class TTAchievementManagerAI(DistributedObjectGlobalAI):
    notify = directNotify.newCategory("TTAchievementManagerAI")
    def __init__(self):
        pass

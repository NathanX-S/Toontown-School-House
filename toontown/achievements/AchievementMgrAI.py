from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.DistributedObjectGlobalAI import DistributedObjectGlobalAI

class AchievementMgrAI(DistributedObjectGlobalAI):
    notify = directNotify.newCategory("AchievementMgrAI")

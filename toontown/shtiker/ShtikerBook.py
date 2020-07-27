from panda3d.core import *
from libotp import *
from toontown.toonbase import ToontownGlobals
from direct.showbase import DirectObject
from direct.fsm import StateData
from direct.gui.DirectGui import *
from toontown.toonbase import TTLocalizer as TTL
from toontown.effects import DistributedFireworkShow
from toontown.parties import DistributedPartyFireworksActivity
from direct.directnotify import DirectNotifyGlobal
from collections import OrderedDict
class ShtikerBook(DirectFrame, StateData.StateData):
    notify = DirectNotifyGlobal.directNotify.newCategory('ShtikerBook')

    def __init__(self, doneEvent):
        DirectFrame.__init__(self, relief=None, sortOrder=DGG.BACKGROUND_SORT_INDEX)
        self.initialiseoptions(ShtikerBook)
        StateData.StateData.__init__(self, doneEvent)
        self.pages = {}
        self.lockedPages = []
        self.pageTabs = {}
        self.categoryTabs = {}
        self.pageTabFrame = DirectFrame(parent=self, relief=None, pos=(0.93, 1, 0.575), scale=1.25)
        self.pageTabFrame.hide()
        self.currPage = None
        self.currPageIndex = None
        self.currCategory = None
        self.entered = 0
        self.safeMode = 0
        self.__obscured = 0
        self.__shown = 0
        self.__isOpen = 0
        self.hide()
        self.setPos(0, 0, 0.1)
        sos_textures = loader.loadModel('phase_3.5/models/gui/sos_textures')
        stickerbook_gui = loader.loadModel('phase_3.5/models/gui/stickerbook_gui')
        inventory_icons = loader.loadModel('phase_3.5/models/gui/inventory_icons')
        playing_card = loader.loadModel('phase_3.5/models/gui/playingCard')
        golf_gui = loader.loadModel('phase_6/models/golf/golf_gui')
        party_stickerbook = loader.loadModel('phase_4/models/parties/partyStickerbook')
        jar_gui = loader.loadModel('phase_3.5/models/gui/jar_gui')
        cloud = loader.loadModel('phase_3.5/models/gui/cloud')
        self.button_bg = loader.loadModel('phase_3/models/gui/tt_m_gui_ups_panelBg')
        self.categoryDefs = OrderedDict()
        cat_defs = self.categoryDefs
        cat_defs["Settings"] = [TTL.OptionsPageTitle]
        cat_defs["Navigation"] = [TTL.ShardPageTitle, TTL.MapPageTitle]
        cat_defs["Fighting"] = [TTL.InventoryPageTitle, TTL.QuestPageToonTasks, TTL.TrackPageShortTitle]
        cat_defs["Cogs 'n' Rewards"] = [TTL.SuitPageTitle, TTL.DisguisePageTitle, TTL.NPCFriendPageTitle]
        cat_defs["Activities"] = [TTL.FishPageTitle, TTL.KartPageTitle, TTL.GolfPageTitle, TTL.GardenPageTitle]
        cat_defs["Misc."] = [TTL.EventsPageName, TTL.SpellbookPageTitle]
        self.categoryIcons = {"Settings": [sos_textures.find('**/switch1')],
         "Navigation": [sos_textures.find('**/compass')],
         "Fighting": [inventory_icons.find('**/inventory_cake'), 7],
         "Cogs 'n' Rewards": [sos_textures.find('**/gui_gear')],
         "Activities": [sos_textures.find('**/kartIcon')],
         "Misc.": [cloud.find('**/cloud')]}
        self.pageIcons = {TTL.OptionsPageTitle: [sos_textures.find('**/switch1')],
         TTL.ShardPageTitle: [sos_textures.find('**/district')],
         TTL.MapPageTitle: [sos_textures.find('**/teleportIcon')],
         TTL.InventoryPageTitle: [inventory_icons.find('**/inventory_tart'), 7],
         TTL.QuestPageToonTasks: [stickerbook_gui.find('**/questCard'), 0.9],
         TTL.TrackPageShortTitle: [loader.loadModel('phase_3.5/models/gui/filmstrip'), 1.1, Vec4(0.7, 0.7, 0.7, 1)],
         TTL.SuitPageTitle: [sos_textures.find('**/gui_gear')],
         TTL.DisguisePageTitle: [sos_textures.find('**/disguise2'), 1, Vec4(0.7, 0.7, 0.7, 1)],
         TTL.NPCFriendPageTitle: [playing_card.find('**/card_back'), 0.22],
         TTL.FishPageTitle: [sos_textures.find('**/fish')],
         TTL.GardenPageTitle: [sos_textures.find('**/gardenIcon')],
         TTL.KartPageTitle: [sos_textures.find('**/kartIcon')],
         TTL.GolfPageTitle: [golf_gui.find('**/score_card_icon')],
         TTL.EventsPageName: [party_stickerbook.find('**/Stickerbook_PartyIcon')],
         TTL.SpellbookPageTitle: [sos_textures.find('**/spellbookIcon')]}
        return

    def setSafeMode(self, setting):
        self.safeMode = setting

    def enter(self):
        if base.config.GetBool('want-qa-regression', 0):
            self.notify.info('QA-REGRESSION: SHTICKERBOOK: Open')
        if self.entered:
            return
        self.entered = 1
        messenger.send('releaseDirector')
        messenger.send('stickerBookEntered')
        base.playSfx(self.openSound)
        base.disableMouse()
        base.setCellsAvailable([base.rightCells[0]], 0)
        self.oldMin2dAlpha = NametagGlobals.getMin2dAlpha()
        self.oldMax2dAlpha = NametagGlobals.getMax2dAlpha()
        NametagGlobals.setMin2dAlpha(0.8)
        NametagGlobals.setMax2dAlpha(1.0)
        self.__isOpen = 1
        self.__setButtonVisibility()
        self.show()
        self.showPageArrows()
        if not self.safeMode:
            self.accept('shtiker-page-done', self.__pageDone)
            self.accept(ToontownGlobals.StickerBookHotkey, self.__close)
            self.accept(ToontownGlobals.OptionsPageHotkey, self.__close)
            self.pageTabFrame.show()
        self.currPage.enter()

    def exit(self):
        if not self.entered:
            return
        self.entered = 0
        messenger.send('stickerBookExited')
        base.playSfx(self.closeSound)
        self.currPage.exit()
        NametagGlobals.setMin2dAlpha(self.oldMin2dAlpha)
        NametagGlobals.setMax2dAlpha(self.oldMax2dAlpha)
        base.setCellsAvailable([base.rightCells[0]], 1)
        self.__isOpen = 0
        self.hide()
        self.hideButton()
        cleanupDialog('globalDialog')
        self.pageTabFrame.hide()
        self.ignore('shtiker-page-done')
        self.ignore(ToontownGlobals.StickerBookHotkey)
        self.ignore(ToontownGlobals.OptionsPageHotkey)
        self.ignore('arrow_right')
        self.ignore('arrow_left')
        if base.config.GetBool('want-qa-regression', 0):
            self.notify.info('QA-REGRESSION: SHTICKERBOOK: Close')

    def load(self):
        self.checkGardenStarted = localAvatar.getGardenStarted()
        bookModel = loader.loadModel('phase_3.5/models/gui/stickerbook_gui')
        self['image'] = bookModel.find('**/big_book')
        self['image_scale'] = (2, 1, 1.5)
        self.resetFrameSize()
        self.bookOpenButton = DirectButton(image=(bookModel.find('**/BookIcon_CLSD'), bookModel.find('**/BookIcon_OPEN'), bookModel.find('**/BookIcon_RLVR')), relief=None, pos=(-0.158, 0, 0.17), parent=base.a2dBottomRight, scale=0.305, command=self.__open)
        self.bookCloseButton = DirectButton(image=(bookModel.find('**/BookIcon_OPEN'), bookModel.find('**/BookIcon_CLSD'), bookModel.find('**/BookIcon_RLVR2')), relief=None, pos=(-0.158, 0, 0.17), parent=base.a2dBottomRight, scale=0.305, command=self.__close)
        self.bookOpenButton.hide()
        self.bookCloseButton.hide()
        self.nextArrow = DirectButton(parent=self, relief=None, image=(bookModel.find('**/arrow_button'), bookModel.find('**/arrow_down'), bookModel.find('**/arrow_rollover')), scale=(0.1, 0.1, 0.1), pos=(0.838, 0, -0.661), command=self.__pageChange, extraArgs=[1])
        self.prevArrow = DirectButton(parent=self, relief=None, image=(bookModel.find('**/arrow_button'), bookModel.find('**/arrow_down'), bookModel.find('**/arrow_rollover')), scale=(-0.1, 0.1, 0.1), pos=(-0.838, 0, -0.661), command=self.__pageChange, extraArgs=[-1])
        bookModel.removeNode()
        self.openSound = base.loader.loadSfx('phase_3.5/audio/sfx/GUI_stickerbook_open.ogg')
        self.closeSound = base.loader.loadSfx('phase_3.5/audio/sfx/GUI_stickerbook_delete.ogg')
        self.pageSound = base.loader.loadSfx('phase_3.5/audio/sfx/GUI_stickerbook_turn.ogg')
        i = 0
        for cat in self.categoryDefs.keys():
            self.addCategoryTab(i, cat)
            i += 1
        return

    def unload(self):
        loader.unloadModel('phase_3.5/models/gui/stickerbook_gui')
        self.destroy()
        self.bookOpenButton.destroy()
        del self.bookOpenButton
        self.bookCloseButton.destroy()
        del self.bookCloseButton
        self.nextArrow.destroy()
        del self.nextArrow
        self.prevArrow.destroy()
        del self.prevArrow
        for page in self.pages.values():
            page.unload()

        del self.pages
        for pageTab in self.pageTabs.values():
            pageTab.destroy()

        del self.pageTabs
        del self.openSound
        del self.closeSound
        del self.pageSound

    def addPage(self, page, pageName = 'Page'):
        self.pages[pageName] = page
        page.setBook(self)
        page.setPageName(pageName)
        page.reparentTo(self)

    def addPageTab(self, catName, pageName = 'Page'):
        tabIndex = len(self.pageTabs)
        categoryDef = self.categoryDefs[catName]
        catIndex = self.categoryDefs.keys().index(catName)
        pageIndex = catIndex + categoryDef.index(pageName)
        page = self.pages[pageName]
        def goToPage():
            messenger.send('wakeup')
            base.playSfx(self.pageSound)
            self.setPage(page)
            if base.config.GetBool('want-qa-regression', 0):
                self.notify.info('QA-REGRESSION: SHTICKERBOOK: Browse tabs %s' % page.pageName)

        yOffset = (-0.065 * pageIndex) + 0.0875
        iconGeom = None
        iconImage = None
        iconScale = 1
        iconColor = Vec4(1)
        buttonPressedCommand = goToPage
        extraArgs = []
        pageItem = self.pageIcons[pageName]
        iconGeom = pageItem[0]
        if len(pageItem) > 1:
            iconScale = pageItem[1]
        if len(pageItem) > 2:
            iconColor = pageItem[2]
        if pageName == TTL.OptionsPageTitle:
            pageName = TTL.OptionsTabTitle
        pageTab = DirectButton(parent=self.pageTabFrame, relief=None,
         frameSize=(-0.575, 0.575, -0.575, 0.575),
         borderWidth=(0.05, 0.05),
         text=('', '', pageName, ''),
         text_align=TextNode.ALeft,
         text_pos=(1, -0.2), text_scale=TTL.SBpageTab,
         text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
         image=self.button_bg, image_scale=1.15, geom=iconGeom, geom_scale=iconScale, geom_color=iconColor,
         pos=(0.075, 0, yOffset), scale=0.06, command=buttonPressedCommand, extraArgs=extraArgs)
        self.pageTabs[pageName] = pageTab
        return

    def setPage(self, page, enterPage = True):
        if self.currPage is not None:
            self.currPage.exit()
        self.currPage = self.pages[page.getPageName()]
        if enterPage:
            self.showPageArrows()
            page.enter()
        return

    def isOnPage(self, page):
        return page == self.currPage

    def openCategory(self, catName):
        if self.currCategory:
            self.categoryTabs[self.currCategory]['image_color'] = Vec4(1)
        self.categoryTabs[catName]['image_color'] = Vec4(0.82, 0.71, 0.11, 1)
        for pageName, pageTab in self.pageTabs.items():
            pageTab.destroy()
        pageNames = self.categoryDefs[catName]
        for pageName in pageNames:
            if pageName in self.lockedPages:
                continue
            self.addPageTab(catName, pageName)
        self.currCategory = catName

    def addCategoryTab(self, catIndex, catName = 'Category'):
        yOffset = (-0.065 * catIndex) + 0.0875
        iconGeom = None
        iconImage = None
        iconScale = 1
        iconColor = Vec4(1)
        buttonPressedCommand = self.openCategory
        extraArgs = [catName]
        catItem = self.categoryIcons[catName]
        iconGeom = catItem[0]
        if len(catItem) > 1:
            iconScale = catItem[1]
        if len(catItem) > 2:
            iconColor = catItem[2]
        if catName == TTL.OptionsPageTitle:
            catName = TTL.OptionsTabTitle
        categoryTab = DirectButton(parent=self.pageTabFrame, relief=None,
         frameSize=(-0.575, 0.575, -0.575, 0.575),
         borderWidth=(0.05, 0.05),
         text=('', '', catName, ''),
         text_align=TextNode.ALeft,
         text_pos=(1.75, -0.2), text_scale=TTL.SBpageTab,
         text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
         image=self.button_bg, image_scale=1.15, geom=iconGeom, geom_scale=iconScale, geom_color=iconColor,
         pos=(0, 0, yOffset), scale=0.06, command=buttonPressedCommand, extraArgs=extraArgs)
        self.categoryTabs[catName] = categoryTab
        return

    def obscureButton(self, obscured):
        self.__obscured = obscured
        self.__setButtonVisibility()

    def isObscured(self):
        return self.__obscured

    def showButton(self):
        self.__shown = 1
        self.__setButtonVisibility()

    def hideButton(self):
        self.__shown = 0
        self.__setButtonVisibility()

    def __setButtonVisibility(self):
        if self.__isOpen:
            self.bookOpenButton.hide()
            self.bookCloseButton.show()
        elif self.__shown and not self.__obscured:
            self.bookOpenButton.show()
            self.bookCloseButton.hide()
        else:
            self.bookOpenButton.hide()
            self.bookCloseButton.hide()

    def shouldBookButtonBeHidden(self):
        result = False
        if self.__isOpen:
            pass
        elif self.__shown and not self.__obscured:
            pass
        else:
            result = True
        return result

    def __open(self):
        messenger.send('enterStickerBook')
        if not localAvatar.getGardenStarted():
            self.lockedPages.append(TTL.GardenPageTitle)

    def __close(self):
        base.playSfx(self.closeSound)
        self.doneStatus = {'mode': 'close'}
        messenger.send('exitStickerBook')
        messenger.send(self.doneEvent)

    def closeBook(self):
        self.__close()

    def __pageDone(self):
        page = self.currPage
        pageDoneStatus = page.getDoneStatus()
        if pageDoneStatus:
            if pageDoneStatus['mode'] == 'close':
                self.__close()
            else:
                self.doneStatus = pageDoneStatus
                messenger.send(self.doneEvent)

    def __pageChange(self, offset):
        messenger.send('wakeup')
        base.playSfx(self.pageSound)
        self.currPage.exit()
        self.currPageIndex = self.currPageIndex + offset
        messenger.send('stickerBookPageChange-' + str(self.currPageIndex))
        self.currPageIndex = max(self.currPageIndex, 0)
        self.currPageIndex = min(self.currPageIndex, len(self.categoryDefs[self.currCategory]) - 1)
        self.showPageArrows()
        page = self.categoryDefs[self.currCategory][self.currPageIndex]
        page.enter()

    def showPageArrows(self):
        self.ignore('arrow_left')
        self.ignore('arrow_right')
        if self.currPageIndex == len(self.pages) - 1:
            self.accept('arrow_left', self.__pageChange, [-1])
            self.prevArrow.show()
            self.nextArrow.hide()
        else:
            self.prevArrow.show()
            self.nextArrow.show()
            self.accept('arrow_right', self.__pageChange, [1])
            self.accept('arrow_left', self.__pageChange, [-1])
        if self.currPageIndex == 0:
            self.accept('arrow_right', self.__pageChange, [1])
            self.prevArrow.hide()
            self.nextArrow.show()

    def disableBookCloseButton(self):
        if self.bookCloseButton:
            self.bookCloseButton['command'] = None
        return

    def enableBookCloseButton(self):
        if self.bookCloseButton:
            self.bookCloseButton['command'] = self.__close

    def disableAllPageTabs(self):
        for button in self.pageTabs:
            button['state'] = DGG.DISABLED

    def enableAllPageTabs(self):
        for button in self.pageTabs:
            button['state'] = DGG.NORMAL

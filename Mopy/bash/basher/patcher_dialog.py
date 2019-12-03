# -*- coding: utf-8 -*-
#
# GPL License and Copyright Notice ============================================
#  This file is part of Wrye Bash.
#
#  Wrye Bash is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  Wrye Bash is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Wrye Bash; if not, write to the Free Software Foundation,
#  Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
#  Wrye Bash copyright (C) 2005-2009 Wrye, 2010-2019 Wrye Bash Team
#  https://github.com/wrye-bash
#
# =============================================================================

"""Patch dialog"""
import StringIO
import copy
import errno
import re
import time
from datetime import timedelta
from . import BashFrame ##: drop this - decouple !
from .. import balt, bass, bolt, bosh, bush, env, load_order
from ..balt import Link, Resources, set_event_hook, Events, HorizontalLine
from ..bolt import SubProgress, GPath, Path
from ..exception import BoltError, CancelError, FileEditError, \
    PluginsFullError, SkipError
from ..gui import CancelButton, DeselectAllButton, HLayout, Label, \
    LayoutOptions, OkButton, OpenButton, RevertButton, RevertToSavedButton, \
    SaveAsButton, SelectAllButton, Stretch, VLayout
from ..patcher import configIsCBash, exportConfig
from ..patcher.patch_files import PatchFile, CBash_PatchFile
from ..patcher.base import AListPatcher

# Final lists of gui patcher classes instances, initialized in
# gui_patchers.InitPatchers() based on game. These must be copied as needed.
PBash_gui_patchers = [] #--All gui patchers classes for this game
CBash_gui_patchers = [] #--All gui patchers classes for this game (CBash mode)

class PatchDialog(balt.Dialog):
    """Bash Patch update dialog.

    :type _gui_patchers: list[basher.gui_patchers._PatcherPanel]
    """

    def __init__(self, parent, patchInfo, doCBash, importConfig,
                 mods_to_reselect):
        self.mods_to_reselect = mods_to_reselect
        self.parent = parent
        if (doCBash or doCBash is None) and bass.settings['bash.CBashEnabled']:
            doCBash = True
        else:
            doCBash = False
        self.doCBash = doCBash
        title = _(u'Update ') + patchInfo.name.s + [u'', u' (CBash)'][doCBash]
        size = balt.sizes.get(self.__class__.__name__, (500,600))
        super(PatchDialog, self).__init__(parent, title=title, size=size)
        self.SetSizeHints(400,300)
        #--Data
        AListPatcher.list_patches_dir()
        groupOrder = dict([(group,index) for index,group in
            enumerate((_(u'General'),_(u'Importers'),_(u'Tweakers'),_(u'Special')))])
        patchConfigs = bosh.modInfos.table.getItem(patchInfo.name,'bash.patch.configs',{})
        # If the patch config isn't from the same mode (CBash/Python), try converting
        # it over to the current mode
        if configIsCBash(patchConfigs) != self.doCBash:
            if importConfig:
                patchConfigs = self.ConvertConfig(patchConfigs)
            else:
                patchConfigs = {}
        isFirstLoad = 0 == len(patchConfigs)
        self.patchInfo = patchInfo
        self._gui_patchers = [copy.deepcopy(p) for p in (
            CBash_gui_patchers if doCBash else PBash_gui_patchers)]
        self._gui_patchers.sort(key=lambda a: a.__class__.name)
        self._gui_patchers.sort(key=lambda a: groupOrder[a.__class__.group])
        for patcher in self._gui_patchers:
            patcher.getConfig(patchConfigs) #--Will set patcher.isEnabled
            patcher.SetIsFirstLoad(isFirstLoad)
        self.currentPatcher = None
        patcherNames = [patcher.getName() for patcher in self._gui_patchers]
        #--GUI elements
        self.gExecute = OkButton(self, label=_(u'Build Patch'))
        self.gExecute.on_clicked.subscribe(self.PatchExecute)
        # TODO(nycz): somehow move setUAC further into env?
        # Note: for this to work correctly, it needs to be run BEFORE
        # appending a menu item to a menu (and so, needs to be enabled/
        # disabled prior to that as well.
        # TODO(nycz): DEWX - Button.GetHandle
        env.setUAC(self.gExecute._native_widget.GetHandle(), True)
        self.gSelectAll = SelectAllButton(self)
        self.gSelectAll.on_clicked.subscribe(self.SelectAll)
        self.gDeselectAll = DeselectAllButton(self)
        self.gDeselectAll.on_clicked.subscribe(self.DeselectAll)
        cancelButton = CancelButton(self)
        self.gPatchers = balt.listBox(self, choices=patcherNames,
                                      isSingle=True, kind=u'checklist',
                                      onSelect=self.OnSelect,
                                      onCheck=self.OnCheck)
        self.gExportConfig = SaveAsButton(self, label=_(u'Export'))
        self.gExportConfig.on_clicked.subscribe(self.ExportConfig)
        self.gImportConfig = OpenButton(self, label=_(u'Import'))
        self.gImportConfig.on_clicked.subscribe(self.ImportConfig)
        self.gRevertConfig = RevertToSavedButton(self)
        self.gRevertConfig.on_clicked.subscribe(self.RevertConfig)
        self.gRevertToDefault = RevertButton(self,
                                             label=_(u'Revert To Default'))
        self.gRevertToDefault.on_clicked.subscribe(self.DefaultConfig)
        for index,patcher in enumerate(self._gui_patchers):
            self.gPatchers.Check(index,patcher.isEnabled)
        self.defaultTipText = _(u'Items that are new since the last time this patch was built are displayed in bold')
        self.gTipText = Label(self,self.defaultTipText)
        #--Events
        set_event_hook(self, Events.RESIZE, self.OnSize) # save dialog size
        set_event_hook(self.gPatchers, Events.MOUSE_MOTION, self.OnMouse)
        set_event_hook(self.gPatchers, Events.MOUSE_LEAVE_WINDOW, self.OnMouse)
        set_event_hook(self.gPatchers, Events.CHAR_KEY_PRESSED, self.OnChar)
        self.mouse_dex = -1
        #--Layout
        self.config_layout = VLayout(default_fill=True, default_weight=1)
        VLayout(border=4, spacing=4, default_fill=True, items=[
            (HLayout(spacing=8, default_fill=True, items=[
                self.gPatchers,
                (self.config_layout, LayoutOptions(weight=1))
             ]), LayoutOptions(weight=1)),
            self.gTipText,
            HorizontalLine(parent),
            HLayout(spacing=4, items=[
                Stretch(), self.gExportConfig, self.gImportConfig,
                self.gRevertConfig, self.gRevertToDefault]),
            HLayout(spacing=4, items=[
                Stretch(), self.gExecute, self.gSelectAll, self.gDeselectAll,
                cancelButton])
        ]).apply_to(self)
        self.SetIcons(Resources.bashMonkey)
        #--Patcher panels
        for patcher in self._gui_patchers:
            patcher.GetConfigPanel(self, self.config_layout,
                                   self.gTipText).Hide()
        initial_select = min(len(self._gui_patchers) - 1, 1)
        if initial_select >= 0:
            self.gPatchers.SetSelection(initial_select) # callback not fired
            self.ShowPatcher(self._gui_patchers[initial_select]) # so this is needed
        self.SetOkEnable()

    #--Core -------------------------------
    def SetOkEnable(self):
        """Enable Build Patch button if at least one patcher is enabled."""
        self.gExecute.enabled = any(p.isEnabled for p in self._gui_patchers)

    def ShowPatcher(self,patcher):
        """Show patcher panel."""
        if patcher == self.currentPatcher: return
        if self.currentPatcher is not None:
            self.currentPatcher.gConfigPanel.Hide()
        patcher.GetConfigPanel(self, self.config_layout, self.gTipText).Show()
        self.Layout()
        patcher.Layout()
        self.currentPatcher = patcher

    @balt.conversation
    def PatchExecute(self): # TODO(ut): needs more work to reduce P/C differences to an absolute minimum
        """Do the patch."""
        self.EndModalOK()
        patchFile = progress = None
        try:
            patch_name = self.patchInfo.name
            patch_size = self.patchInfo.size
            progress = balt.Progress(patch_name.s,(u' '*60+u'\n'), abort=True)
            timer1 = time.clock()
            #--Save configs
            self._saveConfig(patch_name)
            #--Do it
            log = bolt.LogFile(StringIO.StringIO())
            patchers = [p for p in self._gui_patchers if p.isEnabled]
            patchFile = CBash_PatchFile(patch_name, patchers) if self.doCBash \
                   else PatchFile(self.patchInfo, patchers)
            patchFile.init_patchers_data(SubProgress(progress, 0, 0.1)) #try to speed this up!
            if self.doCBash:
                #try to speed this up!
                patchFile.buildPatch(SubProgress(progress,0.1,0.9))
                #no speeding needed/really possible (less than 1/4 second even with large LO)
                patchFile.buildPatchLog(log, SubProgress(progress, 0.95, 0.99))
                #--Save
                progress.setCancel(False, patch_name.s+u'\n'+_(u'Saving...'))
                progress(1.0)
                self._save_cbash(patchFile, patch_name)
            else:
                patchFile.initFactories(SubProgress(progress,0.1,0.2)) #no speeding needed/really possible (less than 1/4 second even with large LO)
                patchFile.scanLoadMods(SubProgress(progress,0.2,0.8)) #try to speed this up!
                patchFile.buildPatch(log,SubProgress(progress,0.8,0.9))#no speeding needed/really possible (less than 1/4 second even with large LO)
                #--Save
                progress.setCancel(False, patch_name.s+u'\n'+_(u'Saving...'))
                progress(0.9)
                self._save_pbash(patchFile, patch_name)
            #--Done
            progress.Destroy(); progress = None
            timer2 = time.clock()
            #--Readme and log
            log.setHeader(None)
            log(u'{{CSS:wtxt_sand_small.css}}')
            logValue = log.out.getvalue()
            log.out.close()
            timerString = unicode(timedelta(seconds=round(timer2 - timer1, 3))).rstrip(u'0')
            logValue = re.sub(u'TIMEPLACEHOLDER', timerString, logValue, 1)
            readme = bosh.modInfos.store_dir.join(u'Docs', patch_name.sroot + u'.txt')
            docsDir = bass.settings.get(u'balt.WryeLog.cssDir', GPath(u''))
            if self.doCBash: ##: eliminate this if/else
                with readme.open('w',encoding='utf-8') as file:
                    file.write(logValue)
                #--Convert log/readme to wtxt and show log
                bolt.WryeText.genHtml(readme,None,docsDir)
            else:
                tempReadmeDir = Path.tempDir().join(u'Docs')
                tempReadme = tempReadmeDir.join(patch_name.sroot+u'.txt')
                #--Write log/readme to temp dir first
                with tempReadme.open('w',encoding='utf-8-sig') as file:
                    file.write(logValue)
                #--Convert log/readmeto wtxt
                bolt.WryeText.genHtml(tempReadme,None,docsDir)
                #--Try moving temp log/readme to Docs dir
                try:
                    env.shellMove(tempReadmeDir, bass.dirs[u'mods'],
                                  parent=self)
                except (CancelError,SkipError):
                    # User didn't allow UAC, move to My Games directory instead
                    env.shellMove([tempReadme, tempReadme.root + u'.html'],
                                  bass.dirs[u'saveBase'], parent=self)
                    readme = bass.dirs[u'saveBase'].join(readme.tail)
                #finally:
                #    tempReadmeDir.head.rmtree(safety=tempReadmeDir.head.stail)
            readme = readme.root + u'.html'
            bosh.modInfos.table.setItem(patch_name, u'doc', readme)
            balt.playSound(self.parent, bass.inisettings[u'SoundSuccess'].s)
            balt.WryeLog(self.parent, readme, patch_name.s,
                         log_icons=Resources.bashBlue)
            #--Select?
            if self.mods_to_reselect:
                for mod in self.mods_to_reselect:
                    bosh.modInfos.lo_activate(mod, doSave=False)
                self.mods_to_reselect.clear()
                bosh.modInfos.cached_lo_save_active() ##: also done below duh
            count, message = 0, _(u'Activate %s?') % patch_name.s
            if load_order.cached_is_active(patch_name) or (
                        bass.inisettings[u'PromptActivateBashedPatch'] and
                        balt.askYes(self.parent, message, patch_name.s)):
                try:
                    changedFiles = bosh.modInfos.lo_activate(patch_name,
                                                             doSave=True)
                    count = len(changedFiles)
                    if count > 1: Link.Frame.SetStatusInfo(
                            _(u'Masters Activated: ') + unicode(count - 1))
                except PluginsFullError:
                    balt.showError(self, _(
                        u'Unable to add mod %s because load list is full.')
                                   % patch_name.s)
            # although improbable user has package with bashed patches...
            info = bosh.modInfos.new_info(patch_name, notify_bain=True)
            if info.size == patch_size:
                # needed if size remains the same - mtime is set in
                # parsers.ModFile#safeSave (or save for CBash...) which can't
                # use setmtime(crc_changed), as no info is there. In this case
                # _reset_cache > calculate_crc() would not detect the crc
                # change. That's a general problem with crc cache - API limits
                info.calculate_crc(recalculate=True)
            BashFrame.modList.RefreshUI(refreshSaves=bool(count))
        except FileEditError as error:
            balt.playSound(self.parent, bass.inisettings[u'SoundError'].s)
            balt.showError(self,u'%s'%error,_(u'File Edit Error'))
        except CancelError:
            pass
        except BoltError as error:
            balt.playSound(self.parent, bass.inisettings[u'SoundError'].s)
            balt.showError(self,u'%s'%error,_(u'Processing Error'))
        except:
            balt.playSound(self.parent, bass.inisettings[u'SoundError'].s)
            raise
        finally:
            if self.doCBash:
                try: patchFile.Current.Close()
                except:
                    bolt.deprint(u'Failed to close CBash collection',
                                 traceback=True)
            if progress: progress.Destroy()

    def _save_pbash(self, patchFile, patch_name):
        while True:
            try:
                # FIXME will keep displaying a bogus UAC prompt if file is
                # locked - aborting bogus UAC dialog raises SkipError() in
                # shellMove, not sure if ever a Windows or Cancel are raised
                patchFile.safeSave()
                return
            except (CancelError, SkipError, OSError) as werr:
                if isinstance(werr, OSError) and werr.errno != errno.EACCES:
                    raise
                if self._pretry(patch_name):
                    continue
                raise # will raise the SkipError which is correctly processed

    def _save_cbash(self, patchFile, patch_name):
        patchFile.save()
        patchTime = self.patchInfo.mtime
        while True:
            try:
                patch_name.untemp()
                patch_name.mtime = patchTime
                return
            except OSError as werr:
                if werr.errno == errno.EACCES:
                    if not self._cretry(patch_name):
                        raise SkipError() # caught - Processing error displayed
                    continue
                raise

    def _pretry(self, patch_name):
        return balt.askYes(
            self, _(u'Bash encountered an error when saving %(patch_name)s.'
                    u'\n\nEither Bash needs Administrator Privileges to save '
                    u'the file, or the file is in use by another process such '
                    u'as %(xedit_name)s.\nPlease close any program that is '
                    u'accessing %(patch_name)s, and provide Administrator '
                    u'Privileges if prompted to do so.\n\nTry again?') % {
                u'patch_name': patch_name.s,
                u'xedit_name': bush.game.xe.full_name},
            _(u'Bashed Patch - Save Error'))

    def _cretry(self, patch_name):
        return balt.askYes(
            self, _(u'Bash encountered an error when renaming '
                    u'%(temp_patch)s to %(patch_name)s.\n\nThe file is in use '
                    u'by another process such as %(xedit_name)s.\nPlease '
                    u'close the other program that is accessing %s.\n\nTry '
                    u'again?') % {
                u'temp_patch': patch_name.temp.s, u'patch_name': patch_name.s,
                u'xedit_name': bush.game.xe.full_name},
            _(u'Bashed Patch - Save Error'))

    def __config(self):
        config = {'ImportedMods': set()}
        for p in self._gui_patchers: p.saveConfig(config)
        return config

    def _saveConfig(self, patch_name):
        """Save the configuration"""
        config = self.__config()
        bosh.modInfos.table.setItem(patch_name, u'bash.patch.configs', config)

    def ExportConfig(self):
        """Export the configuration to a user selected dat file."""
        config = self.__config()
        exportConfig(patch_name=self.patchInfo.name, config=config,
                     isCBash=self.doCBash, win=self.parent,
                     outDir=bass.dirs[u'patches'])

    __old_key = GPath(u'Saved Bashed Patch Configuration')
    __new_key = u'Saved Bashed Patch Configuration (%s)'
    def ImportConfig(self):
        """Import the configuration from a user selected dat file."""
        config_dat = self.patchInfo.name + _(u'_Configuration.dat')
        textDir = bass.dirs[u'patches']
        textDir.makedirs()
        #--File dialog
        textPath = balt.askOpen(self.parent,
                                _(u'Import Bashed Patch configuration from:'),
                                textDir, config_dat, u'*.dat', mustExist=True)
        if not textPath: return
        table = bolt.Table(bolt.PickleDict(textPath))
        # try the current Bashed Patch mode.
        patchConfigs = table.getItem(
            GPath(self.__new_key % ([u'Python', u'CBash'][self.doCBash])),
            u'bash.patch.configs', {})
        convert = False
        if not patchConfigs: # try the non-current Bashed Patch mode
            patchConfigs = table.getItem(
                GPath(self.__new_key % ([u'CBash', u'Python'][self.doCBash])),
                u'bash.patch.configs', {})
            convert = bool(patchConfigs)
        if not patchConfigs: # try the old format
            patchConfigs = table.getItem(self.__old_key, u'bash.patch.configs',
                                         {})
            convert = configIsCBash(patchConfigs) != self.doCBash
        if not patchConfigs:
            balt.showWarning(_(u'No patch config data found in %s') % textPath,
                             _(u'Import Config'))
            return
        if convert:
            patchConfigs = self.UpdateConfig(patchConfigs)
            if patchConfigs is None: return
        self._load_config(patchConfigs)

    def _load_config(self, patchConfigs, set_first_load=False, default=False):
        for index, patcher in enumerate(self._gui_patchers):
            patcher.import_config(patchConfigs, set_first_load=set_first_load,
                                  default=default)
            self.gPatchers.Check(index, patcher.isEnabled)
        self.SetOkEnable()

    def UpdateConfig(self, patchConfigs):
        if not balt.askYes(self.parent, _(
            u"Wrye Bash detects that the selected file was saved in Bash's "
            u'%s mode, do you want Wrye Bash to attempt to adjust the '
            u'configuration on import to work with %s mode (Good chance '
            u'there will be a few mistakes)? (Otherwise this import will '
            u'have no effect.)') % ([u'CBash', u'Python'][self.doCBash],
                                    [u'Python', u'CBash'][self.doCBash])):
            return
        return self.ConvertConfig(patchConfigs)

    @staticmethod
    def ConvertConfig(patchConfigs):
        newConfig = {}
        for key in patchConfigs:
            if key in otherPatcherDict:
                newConfig[otherPatcherDict[key]] = patchConfigs[key]
            else:
                newConfig[key] = patchConfigs[key]
        return newConfig

    def RevertConfig(self):
        """Revert configuration back to saved"""
        patchConfigs = bosh.modInfos.table.getItem(self.patchInfo.name,
                                                   u'bash.patch.configs', {})
        if configIsCBash(patchConfigs) and not self.doCBash:
            patchConfigs = self.ConvertConfig(patchConfigs)
        self._load_config(patchConfigs)

    def DefaultConfig(self):
        """Revert configuration back to default"""
        self._load_config({}, set_first_load=True, default=True)

    def SelectAll(self):
        """Select all patchers and entries in patchers with child entries."""
        for index,patcher in enumerate(self._gui_patchers):
            self.gPatchers.Check(index,True)
            patcher.mass_select()
        self.gExecute.enabled = True

    def DeselectAll(self):
        """Deselect all patchers and entries in patchers with child entries."""
        for index,patcher in enumerate(self._gui_patchers):
            self.gPatchers.Check(index,False)
            patcher.mass_select(select=False)
        self.gExecute.enabled = False

    #--GUI --------------------------------
    def OnSize(self,event):
        balt.sizes[self.__class__.__name__] = tuple(self.GetSize())
        event.Skip()

    def OnSelect(self,event):
        """Responds to patchers list selection."""
        itemDex = event.GetSelection()
        self.ShowPatcher(self._gui_patchers[itemDex])
        self.gPatchers.SetSelection(itemDex)

    def CheckPatcher(self, patcher):
        """Enable a patcher - Called from a patcher's OnCheck method."""
        index = self._gui_patchers.index(patcher)
        self.gPatchers.Check(index)
        self.SetOkEnable()

    def BoldPatcher(self, patcher):
        """Set the patcher label to bold font.  Called from a patcher when
        it realizes it has something new in its list"""
        index = self._gui_patchers.index(patcher)
        get_font = self.gPatchers.GetFont()
        self.gPatchers.SetItemFont(index, balt.Font.Style(get_font, bold=True))

    def OnCheck(self,event):
        """Toggle patcher activity state."""
        index = event.GetSelection()
        patcher = self._gui_patchers[index]
        patcher.isEnabled = self.gPatchers.IsChecked(index)
        self.gPatchers.SetSelection(index)
        self.ShowPatcher(patcher) # SetSelection does not fire the callback
        self.SetOkEnable()

    def OnMouse(self,event):
        """Show tip text when changing item."""
        mouseItem = -1
        if event.Moving():
            mouseItem = self.gPatchers.HitTest(event.GetPosition())
            if mouseItem != self.mouse_dex:
                self.mouse_dex = mouseItem
        elif event.Leaving():
            pass # will be set to defaultTipText
        if 0 <= mouseItem < len(self._gui_patchers):
            patcherClass = self._gui_patchers[mouseItem].__class__
            tip = patcherClass.tip or re.sub(u'' r'\..*', u'.',
                            patcherClass.text.split(u'\n')[0], flags=re.U)
            self.gTipText.label_text = tip
        else:
            self.gTipText.label_text = self.defaultTipText
        event.Skip()

    def OnChar(self,event):
        """Keyboard input to the patchers list box"""
        if event.GetKeyCode() == 1 and event.CmdDown(): # Ctrl+'A'
            patcher = self.currentPatcher
            if patcher is not None:
                if event.ShiftDown():
                    patcher.DeselectAll()
                else:
                    patcher.SelectAll()
                return
        event.Skip()

# Used in ConvertConfig to convert between C and P *gui* patchers config - so
# it belongs with gui_patchers (and not with patchers/ package). Still a hack
otherPatcherDict = {
    u'AliasesPatcher' : u'CBash_AliasesPatcher',
    u'AssortedTweaker' : u'CBash_AssortedTweaker',
    u'PatchMerger' : u'CBash_PatchMerger',
    u'KFFZPatcher' : u'CBash_KFFZPatcher',
    u'ActorImporter' : u'CBash_ActorImporter',
    u'DeathItemPatcher' : u'CBash_DeathItemPatcher',
    u'NPCAIPackagePatcher' : u'CBash_NPCAIPackagePatcher',
    u'UpdateReferences' : u'CBash_UpdateReferences',
    u'CellImporter' : u'CBash_CellImporter',
    u'ClothesTweaker' : u'CBash_ClothesTweaker',
    u'GmstTweaker' : u'CBash_GmstTweaker',
    u'GraphicsPatcher' : u'CBash_GraphicsPatcher',
    u'ImportFactions' : u'CBash_ImportFactions',
    u'ImportInventory' : u'CBash_ImportInventory',
    u'SpellsPatcher' : u'CBash_SpellsPatcher',
    u'TweakActors' : u'CBash_TweakActors',
    u'ImportRelations' : u'CBash_ImportRelations',
    u'ImportScripts' : u'CBash_ImportScripts',
    u'ImportActorsSpells' : u'CBash_ImportActorsSpells',
    u'ListsMerger' : u'CBash_ListsMerger',
    u'NamesPatcher' : u'CBash_NamesPatcher',
    u'NamesTweaker' : u'CBash_NamesTweaker',
    u'NpcFacePatcher' : u'CBash_NpcFacePatcher',
    u'RacePatcher' : u'CBash_RacePatcher',
    u'RoadImporter' : u'CBash_RoadImporter',
    u'SoundPatcher' : u'CBash_SoundPatcher',
    u'StatsPatcher' : u'CBash_StatsPatcher',
    u'ContentsChecker' : u'CBash_ContentsChecker',
    u'CBash_AliasesPatcher' : u'AliasesPatcher',
    u'CBash_AssortedTweaker' : u'AssortedTweaker',
    u'CBash_PatchMerger' : u'PatchMerger',
    u'CBash_KFFZPatcher' : u'KFFZPatcher',
    u'CBash_ActorImporter' : u'ActorImporter',
    u'CBash_DeathItemPatcher' : u'DeathItemPatcher',
    u'CBash_NPCAIPackagePatcher' : u'NPCAIPackagePatcher',
    u'CBash_UpdateReferences' : u'UpdateReferences',
    u'CBash_CellImporter' : u'CellImporter',
    u'CBash_ClothesTweaker' : u'ClothesTweaker',
    u'CBash_GmstTweaker' : u'GmstTweaker',
    u'CBash_GraphicsPatcher' : u'GraphicsPatcher',
    u'CBash_ImportFactions' : u'ImportFactions',
    u'CBash_ImportInventory' : u'ImportInventory',
    u'CBash_SpellsPatcher' : u'SpellsPatcher',
    u'CBash_TweakActors' : u'TweakActors',
    u'CBash_ImportRelations' : u'ImportRelations',
    u'CBash_ImportScripts' : u'ImportScripts',
    u'CBash_ImportActorsSpells' : u'ImportActorsSpells',
    u'CBash_ListsMerger' : u'ListsMerger',
    u'CBash_NamesPatcher' : u'NamesPatcher',
    u'CBash_NamesTweaker' : u'NamesTweaker',
    u'CBash_NpcFacePatcher' : u'NpcFacePatcher',
    u'CBash_RacePatcher' : u'RacePatcher',
    u'CBash_RoadImporter' : u'RoadImporter',
    u'CBash_SoundPatcher' : u'SoundPatcher',
    u'CBash_StatsPatcher' : u'StatsPatcher',
    u'CBash_ContentsChecker' : u'ContentsChecker',
    }

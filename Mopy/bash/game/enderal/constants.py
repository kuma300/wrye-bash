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

# Import all constants from skyrim then edit them as needed

from ..skyrim.constants import *

bethDataFiles = {
    u'skyrim.esm',
    u'update.esm',
    u'update.bsa',
    u'enderal - forgotten stories.esm',
    u'e - meshes.bsa',
    u'e - music.bsa',
    u'e - scripts.bsa',
    u'e - sounds.bsa',
    u'e - textures1.bsa',
    u'e - textures2.bsa',
    u'e - textures3.bsa',
    u'l - textures.bsa',
    u'l - voices.bsa',
    u'skyrim - animations.bsa',
    u'skyrim - interface.bsa',
    u'skyrim - meshes.bsa',
    u'skyrim - misc.bsa',
    u'skyrim - shaders.bsa',
    u'skyrim - sounds.bsa',
    u'skyrim - textures.bsa',
}

# Generated with:
#  find . -type f | cut -d'/' -f 2- | sed -e "s/^/u'/; s/$/',/; s./.\\\\\\\.g"
# Then manually added entries for other languages from SteamDB:
# https://steamdb.info/sub/302557/depots/
allBethFiles = {
    u'E - Meshes.bsa',
    u'E - Music.bsa',
    u'E - Scripts.bsa',
    u'E - Sounds.bsa',
    u'E - Textures1.bsa',
    u'E - Textures2.bsa',
    u'E - Textures3.bsa',
    u'Enderal - Forgotten Stories.esm',
    u'Interface\\00E_heromenu.swf',
    u'Interface\\00E_statsmenu.swf',
    u'Interface\\bartermenu.swf',
    u'Interface\\book.swf',
    u'Interface\\bookmenu.swf',
    u'Interface\\console.swf',
    u'Interface\\console_alias.ini',
    u'Interface\\containermenu.swf',
    u'Interface\\controls\\360\\controlmap.txt',
    u'Interface\\controls\\360\\gamepad.txt',
    u'Interface\\controls\\360\\keyboard_english.txt',
    u'Interface\\controls\\pc\\controlmap.txt',
    u'Interface\\controls\\pc\\gamepad.txt',
    u'Interface\\controls\\pc\\keyboard_english.txt',
    u'Interface\\controls\\pc\\keyboard_french.txt',
    u'Interface\\controls\\pc\\keyboard_german.txt',
    u'Interface\\controls\\pc\\keyboard_italian.txt',
    u'Interface\\controls\\pc\\keyboard_spanish.txt',
    u'Interface\\controls\\pc\\mouse.txt',
    u'Interface\\controls\\ps3\\controlmap.txt',
    u'Interface\\controls\\ps3\\gamepad.txt',
    u'Interface\\controls\\ps3\\keyboard_english.txt',
    u'Interface\\cosmeticmenu.swf',
    u'Interface\\craftingmenu.swf',
    u'Interface\\credits.txt',
    u'Interface\\creditsmenu.swf',
    u'Interface\\cursormenu.swf',
    u'Interface\\dialoguemenu.swf',
    u'Interface\\dyemenu.swf',
    u'Interface\\exported\\skyui\\icons_effect_psychosteve.swf',
    u'Interface\\exported\\skyui\\widgetloader.swf',
    u'Interface\\exported\\uilib\\uilib_1_notificationarea.swf',
    u'Interface\\exported\\widgets\\skyui\\activeeffects.swf',
    u'Interface\\exported\\widgets\\skyui\\followerpanel.swf',
    u'Interface\\exported\\widgets\\skyui\\meter.swf',
    u'Interface\\extension_assets\\bottombar.swf',
    u'Interface\\extension_assets\\buttonart.swf',
    u'Interface\\extension_assets\\icons_category_psychosteve.swf',
    u'Interface\\extension_assets\\meter.swf',
    u'Interface\\fadermenu.swf',
    u'Interface\\FangZhengKaiTi_GBK.swf',
    u'Interface\\favoritesmenu.swf',
    u'Interface\\fontconfig.txt',
    u'Interface\\fonts_console.swf',
    u'Interface\\fonts_en.swf',
    u'Interface\\fonts_en2.swf',
    u'Interface\\fonts_fh2.swf',
    u'Interface\\fonts_ru.swf',
    u'Interface\\giftmenu.swf',
    u'Interface\\inventorymenu.swf',
    u'Interface\\levelupmenu.swf',
    u'Interface\\listmenu.swf',
    u'Interface\\loadingmenu.swf',
    u'Interface\\lockpickingmenu.swf',
    u'Interface\\magicmenu.swf',
    u'Interface\\magicmenuext.swf',
    u'Interface\\magic_card_2.swf',
    u'Interface\\map.swf',
    u'Interface\\messagebox.swf',
    u'Interface\\quest_journal.swf',
    u'Interface\\selectionmenu.swf',
    u'Interface\\sharedcomponents.swf',
    u'Interface\\skyui\\bottombar.swf',
    u'Interface\\skyui\\buttonart.swf',
    u'Interface\\skyui\\config.txt',
    u'Interface\\skyui\\configpanel.swf',
    u'Interface\\skyui\\icons_category_celtic.swf',
    u'Interface\\skyui\\icons_category_curved.swf',
    u'Interface\\skyui\\icons_category_psychosteve.swf',
    u'Interface\\skyui\\icons_category_straight.swf',
    u'Interface\\skyui\\icons_item_psychosteve.swf',
    u'Interface\\skyui\\inventorylists.swf',
    u'Interface\\skyui\\itemcard.swf',
    u'Interface\\skyui\\mapmarkerart.swf',
    u'Interface\\skyui\\mcm_splash.swf',
    u'Interface\\skyui\\res\\mcm_logo.dds',
    u'Interface\\skyui\\skyui_splash.swf',
    u'Interface\\sleepwaitmenu.swf',
    u'Interface\\startmenu.swf',
    u'Interface\\startmenu_fs.swf',
    u'Interface\\statsmenu.swf',
    u'Interface\\statssheetmenu.swf',
    u'Interface\\textentrymenu.swf',
    u'Interface\\titles.swf',
    u'Interface\\trainingmenu.swf',
    u'Interface\\Translate_CHINESE.txt',
    u'Interface\\Translate_ENGLISH.txt',
    u'Interface\\Translate_GERMAN.txt',
    u'Interface\\Translate_ITALIAN.txt',
    u'Interface\\Translate_RUSSIAN.txt',
    u'Interface\\translations\\buriedtreasure_chinese.txt',
    u'Interface\\translations\\buriedtreasure_english.txt',
    u'Interface\\translations\\buriedtreasure_italian.txt',
    u'Interface\\translations\\skyui_chinese.txt',
    u'Interface\\translations\\skyui_czech.txt',
    u'Interface\\translations\\skyui_english.txt',
    u'Interface\\translations\\skyui_french.txt',
    u'Interface\\translations\\skyui_german.txt',
    u'Interface\\translations\\skyui_italian.txt',
    u'Interface\\translations\\skyui_japanese.txt',
    u'Interface\\translations\\skyui_polish.txt',
    u'Interface\\translations\\skyui_russian.txt',
    u'Interface\\translations\\skyui_spanish.txt',
    u'Interface\\translations\\taverngamesczech.txt',
    u'Interface\\translations\\taverngames_chinese.txt',
    u'Interface\\translations\\taverngames_english.txt',
    u'Interface\\translations\\taverngames_french.txt',
    u'Interface\\translations\\taverngames_german.txt',
    u'Interface\\translations\\taverngames_italian.txt',
    u'Interface\\translations\\taverngames_japanese.txt',
    u'Interface\\translations\\taverngames_polish.txt',
    u'Interface\\translations\\taverngames_russian.txt',
    u'Interface\\translations\\taverngames_spanish.txt',
    u'Interface\\translations\\uiextensions_chinese.txt',
    u'Interface\\translations\\uiextensions_english.txt',
    u'Interface\\translations\\uiextensions_german.txt',
    u'Interface\\translations\\uiextensions_italian.txt',
    u'Interface\\tweenmenu.swf',
    u'Interface\\uilib\\buttonart.swf',
    u'Interface\\uilib\\uilib_1_listmenu.swf',
    u'Interface\\uilib\\uilib_1_textinputmenu.swf',
    u'Interface\\wheelmenu.swf',
    u'Interface\\widgetoverlay.swf',
    u'L - Textures.bsa',
    u'L - Voices.bsa',
    u'Meshes\\Actors\\character\\behaviors\\0_master.hkx',
    u'Meshes\\Actors\\character\\behaviors\\1hm_behavior.hkx',
    u'Meshes\\Actors\\character\\behaviors\\FNIS_Enderal_Behavior.hkx',
    u'Meshes\\Actors\\character\\behaviors\\FNIS_FNISBase_Behavior.hkx',
    u'Meshes\\Actors\\character\\behaviors\\FNIS_PaleTest04_Behavior.hkx',
    u'Meshes\\Actors\\character\\behaviors\\FNIS_PipeSmoking_Behavior.hkx',
    u'Meshes\\Actors\\character\\behaviors\\magicbehavior.hkx',
    u'Meshes\\Actors\\character\\behaviors\\mt_behavior.hkx',
    u'Meshes\\Actors\\character\\behaviors\\sprintbehavior - Kopie.hkx',
    u'Meshes\\Actors\\character\\behaviors\\sprintbehavior.hkx',
    u'Meshes\\Actors\\character\\characters\\defaultmale.hkx',
    u'Meshes\\Actors\\character\\characters female\\defaultfemale.hkx',
    u'Meshes\\animationdatasinglefile.txt',
    u'Meshes\\animationsetdatasinglefile.txt',
    u'Meshes\\~AnimationDataSingleFile.txt',
    u'SKSE\\Plugins\\AHZmoreHUDPlugin.dll',
    u'SKSE\\Plugins\\CharGen\\Jespar.dds',
    u'SKSE\\Plugins\\CharGen\\Jespar.nif',
    u'SKSE\\Plugins\\CrashFixPlugin.dll',
    u'SKSE\\Plugins\\CrashFixPlugin.ini',
    u'SKSE\\Plugins\\CrashFixPlugin_preload.txt',
    u'SKSE\\Plugins\\flat_map_markers.dll',
    u'SKSE\\Plugins\\flat_map_markers.ini',
    u'SKSE\\Plugins\\fs.dll',
    u'SKSE\\Plugins\\InsertAttackData.dll',
    u'SKSE\\Plugins\\JCData\\Domains\\JContainers_DomainExample\\dummy-file',
    u'SKSE\\Plugins\\JCData\\InternalLuaScripts\\api_for_lua.h',
    u'SKSE\\Plugins\\JCData\\InternalLuaScripts\\init.lua',
    u'SKSE\\Plugins\\JCData\\InternalLuaScripts\\jc.lua',
    u'SKSE\\Plugins\\JCData\\lua\\jc\\init.lua',
    u'SKSE\\Plugins\\JCData\\lua\\testing\\basic.lua',
    u'SKSE\\Plugins\\JCData\\lua\\testing\\init.lua',
    u'SKSE\\Plugins\\JCData\\lua\\testing\\jc-tests.lua',
    u'SKSE\\Plugins\\JCData\\lua\\testing\\misc.lua',
    u'SKSE\\Plugins\\JCData\\lua\\testing\\test.lua',
    u'SKSE\\Plugins\\JContainers.dll',
    u'SKSE\\Plugins\\LipSyncFix.dll',
    u'SKSE\\Plugins\\MDX_NoPoisonDialogs.dll',
    u'SKSE\\Plugins\\MfgConsole.dll',
    u'SKSE\\Plugins\\MfgConsole.ini',
    u'SKSE\\Plugins\\OneTweak.dll',
    u'SKSE\\Plugins\\OneTweak.ini',
    u'SKSE\\Plugins\\SkyrimRedirector.dll',
    u'SKSE\\Plugins\\SkyrimRedirector.ini',
    u'SKSE\\Plugins\\SkyrimRedirector.log',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\common\\common.vcxproj',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\common\\IArchive.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\common\\IArchive.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\common\\IBufferStream.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\common\\IBufferStream.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\common\\IConsole.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\common\\IConsole.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\common\\ICriticalSection.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\common\\IDatabase.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\common\\IDatabase.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\common\\IDatabase.inc',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\common\\IDataStream.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\common\\IDataStream.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\common\\IDebugLog.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\common\\IDebugLog.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\common\\IDirectoryIterator.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\common\\IDirectoryIterator.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\common\\IDynamicCreate.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\common\\IDynamicCreate.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\common\\IErrors.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\common\\IErrors.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\common\\IEvent.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\common\\IEvent.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\common\\IFIFO.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\common\\IFIFO.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\common\\IFileStream.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\common\\IFileStream.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\common\\IInterlockedLong.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\common\\IInterlockedLong.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\common\\ILinkedList.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\common\\IMemPool.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\common\\IMemPool.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\common\\IMutex.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\common\\IMutex.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\common\\IPipeClient.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\common\\IPipeClient.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\common\\IPipeServer.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\common\\IPipeServer.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\common\\IPrefix.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\common\\IPrefix.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\common\\IRangeMap.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\common\\IRangeMap.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\common\\IReadWriteLock.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\common\\IReadWriteLock.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\common\\ISegmentStream.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\common\\ISegmentStream.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\common\\ISingleton.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\common\\ISingleton.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\common\\ITextParser.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\common\\ITextParser.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\common\\IThread.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\common\\IThread.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\common\\ITimer.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\common\\ITimer.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\common\\ITypes.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\common\\ITypes.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\forgotten_stories_skse_plugin.sln',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\fs\\Achievements.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\fs\\Achievements.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\fs\\CreatePotion.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\fs\\CreatePotion.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\fs\\exports.def',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\fs\\fs.vcxproj',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\fs\\main.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\fs\\PhasmalistInventoryFunctions.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\fs\\PhasmalistInventoryFunctions.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\phasmalist_skse_plugin.VC.db',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skaar_skse_plugin.VC.db',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\Colors.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\Colors.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\CommandTable.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\CommandTable.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\CustomMenu.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\CustomMenu.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\exports.def',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\GameAPI.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\GameAPI.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\GameBSExtraData.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\GameCamera.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\GameCamera.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\GameData.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\GameData.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\GameEvents.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\GameEvents.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\GameExtraData.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\GameExtraData.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\GameFormComponents.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\GameFormComponents.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\GameForms.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\GameForms.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\GameHandlers.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\GameHandlers.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\GameInput.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\GameInput.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\GameMenus.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\GameMenus.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\GameObjects.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\GameObjects.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\GamePathing.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\GamePathing.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\GameReferences.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\GameReferences.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\GameResources.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\GameResources.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\GameRTTI.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\GameRTTI.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\GameSettings.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\GameSettings.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\GameStreams.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\GameStreams.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\GameThreads.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\GameThreads.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\GameTypes.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\GameTypes.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\GlobalLocks.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\GlobalLocks.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\HashUtil.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\HashUtil.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\Hooks_Camera.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\Hooks_Camera.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\Hooks_Debug.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\Hooks_Debug.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\Hooks_DirectInput8Create.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\Hooks_DirectInput8Create.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\Hooks_Event.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\Hooks_Event.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\Hooks_Gameplay.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\Hooks_Gameplay.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\Hooks_Handlers.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\Hooks_Handlers.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\Hooks_Memory.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\Hooks_Memory.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\Hooks_NetImmerse.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\Hooks_NetImmerse.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\Hooks_ObScript.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\Hooks_ObScript.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\Hooks_Papyrus.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\Hooks_Papyrus.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\Hooks_SaveLoad.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\Hooks_SaveLoad.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\Hooks_Scaleform.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\Hooks_Scaleform.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\Hooks_Threads.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\Hooks_Threads.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\Hooks_UI.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\Hooks_UI.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\InputMap.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\InputMap.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\InternalSerialization.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\InternalSerialization.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\NiControllers.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\NiControllers.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\NiExtraData.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\NiExtraData.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\NiGeometry.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\NiGeometry.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\NiInterpolators.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\NiInterpolators.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\NiLight.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\NiLight.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\NiMaterial.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\NiMaterial.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\NiNodes.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\NiNodes.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\NiObjects.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\NiObjects.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\NiProperties.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\NiProperties.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\NiRenderer.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\NiRenderer.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\NiRTTI.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\NiRTTI.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\NiSerialization.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\NiSerialization.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\NiTextures.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\NiTextures.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\NiTypes.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\NiTypes.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusActiveMagicEffect.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusActiveMagicEffect.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusActor.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusActor.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusActorBase.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusActorBase.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusActorValueInfo.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusActorValueInfo.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusAlias.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusAlias.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusAmmo.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusAmmo.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusArgs.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusArgs.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusArmor.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusArmor.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusArmorAddon.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusArmorAddon.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusArt.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusArt.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusBook.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusBook.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusCell.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusCell.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusClass.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusClass.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusColorForm.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusColorForm.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusCombatStyle.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusCombatStyle.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusConstructibleObject.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusConstructibleObject.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusDefaultObjectManager.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusDefaultObjectManager.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusEnchantment.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusEnchantment.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusEquipSlot.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusEquipSlot.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusEvents.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusEvents.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusFlora.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusFlora.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusForm.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusForm.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusGame.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusGame.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusHeadPart.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusHeadPart.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusIngredient.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusIngredient.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusInput.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusInput.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusKeyword.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusKeyword.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusLeveledActor.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusLeveledActor.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusLeveledItem.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusLeveledItem.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusLeveledSpell.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusLeveledSpell.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusMagicEffect.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusMagicEffect.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusMath.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusMath.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusMisc.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusMisc.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusModEvent.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusModEvent.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusNativeFunctionDef.inl',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusNativeFunctionDef_Base.inl',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusNativeFunctions.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusNativeFunctions.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusNetImmerse.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusNetImmerse.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusObjectReference.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusObjectReference.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusObjects.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusObjects.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusPerk.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusPerk.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusPotion.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusPotion.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusQuest.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusQuest.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusRace.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusRace.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusScroll.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusScroll.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusShout.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusShout.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusSKSE.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusSKSE.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusSound.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusSound.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusSoundDescriptor.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusSoundDescriptor.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusSpell.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusSpell.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusStringUtil.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusStringUtil.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusTextureSet.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusTextureSet.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusTree.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusTree.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusUI.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusUI.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusUICallback.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusUICallback.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusUtility.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusUtility.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusVM.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusVM.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusWeapon.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusWeapon.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusWeather.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusWeather.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusWornObject.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PapyrusWornObject.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PluginAPI.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PluginManager.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\PluginManager.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\SafeWrite.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\SafeWrite.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\ScaleformAPI.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\ScaleformAPI.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\ScaleformCallbacks.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\ScaleformCallbacks.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\ScaleformExtendedData.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\ScaleformExtendedData.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\ScaleformLoader.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\ScaleformLoader.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\ScaleformMovie.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\ScaleformMovie.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\ScaleformState.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\ScaleformState.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\ScaleformTypes.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\ScaleformTypes.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\ScaleformVM.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\ScaleformVM.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\Serialization.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\Serialization.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\skse.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\skse.vcxproj',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\skse_license.txt',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\skse_version.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\skse_version.rc',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\Translation.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\Translation.h',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\Utilities.cpp',
    u'SKSE\\Plugins\\Source\\fs_skse_plugin\\skse\\Utilities.h',
    u'SKSE\\Plugins\\StorageUtil.dll',
    u'SKSE\\Plugins\\tkplugin.dll',
    u'SKSE\\SKSE.ini',
    u'Skyrim - Animations.bsa',
    u'Skyrim - Interface.bsa',
    u'Skyrim - Meshes.bsa',
    u'Skyrim - Misc.bsa',
    u'Skyrim - Shaders.bsa',
    u'Skyrim - Sounds.bsa',
    u'Skyrim - Textures.bsa',
    u'Skyrim.esm',
    u'Strings\\Enderal - Forgotten Stories_chinese.DLSTRINGS',
    u'Strings\\Enderal - Forgotten Stories_chinese.ILSTRINGS',
    u'Strings\\Enderal - Forgotten Stories_chinese.STRINGS',
    u'Strings\\Enderal - Forgotten Stories_english.DLSTRINGS',
    u'Strings\\Enderal - Forgotten Stories_english.ILSTRINGS',
    u'Strings\\Enderal - Forgotten Stories_english.STRINGS',
    u'Strings\\enderal - forgotten stories_italian.DLSTRINGS',
    u'Strings\\enderal - forgotten stories_italian.ILSTRINGS',
    u'Strings\\enderal - forgotten stories_italian.STRINGS',
    u'Strings\\Enderal - Forgotten Stories_russian.DLSTRINGS',
    u'Strings\\Enderal - Forgotten Stories_russian.ILSTRINGS',
    u'Strings\\Enderal - Forgotten Stories_russian.STRINGS',
    u'Strings\\Skyrim_chinese.DLSTRINGS',
    u'Strings\\Skyrim_chinese.ILSTRINGS',
    u'Strings\\Skyrim_chinese.STRINGS',
    u'Strings\\Skyrim_english.DLSTRINGS',
    u'Strings\\Skyrim_English.ILSTRINGS',
    u'Strings\\Skyrim_English.STRINGS',
    u'Strings\\skyrim_italian.DLSTRINGS',
    u'Strings\\skyrim_italian.ILSTRINGS',
    u'Strings\\skyrim_italian.STRINGS',
    u'Strings\\Skyrim_russian.DLSTRINGS',
    u'Strings\\Skyrim_russian.ILSTRINGS',
    u'Strings\\Skyrim_russian.STRINGS',
    u'Update.bsa',
    u'Update.esm',
    u'Video\\EnderalIntro.bik',
    u'Video\\Enderal_Credits.bik',
    u'Video\\MQ17BlackGuardian.bik',
    u'Video\\MQP03NearDeathExperience.bik',
}

# xEdit menu string and key for expert setting
xEdit_expert = (_(u'EnderalEdit Expert'), 'enderalView.iKnowWhatImDoing')

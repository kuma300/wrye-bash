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

"""Menu items for the main and item menus of the ini tweaks tab - their window
attribute points to BashFrame.iniList singleton.
"""

from itertools import imap
from .. import bass, bosh, balt
from ..balt import ItemLink, BoolLink, EnabledLink, OneItemLink

__all__ = ['INI_SortValid', 'INI_AllowNewLines', 'INI_ListINIs', 'INI_Apply',
           'INI_CreateNew', 'INI_ListErrors', 'INI_FileOpenOrCopy',
           'INI_Delete']

class INI_SortValid(BoolLink):
    """Sort valid INI Tweaks to the top."""
    _text, key, _help = _(u'Valid Tweaks First'), 'bash.ini.sortValid', \
                        _(u'Valid tweak files will be shown first.')

    def Execute(self):
        super(INI_SortValid, self).Execute()
        self.window.SortItems()

#------------------------------------------------------------------------------
class INI_AllowNewLines(BoolLink):
    """Consider INI Tweaks with new lines valid."""
    _text = _(u'Allow Tweaks with New Settings')
    key = 'bash.ini.allowNewLines'
    _help = _(u'Tweak files adding new sections/settings are considered valid')

    def Execute(self):
        super(INI_AllowNewLines, self).Execute()
        self.window.RefreshUI()

#------------------------------------------------------------------------------
class INI_ListINIs(ItemLink):
    """List errors that make an INI Tweak invalid."""
    _text = _(u'List Active INIs...')
    _help = _(u'Lists all fully applied tweak files.')

    def Execute(self):
        """Handle printing out the errors."""
        tweak_list = self.window.ListTweaks()
        balt.copyToClipboard(tweak_list)
        self._showLog(tweak_list, title=_(u'Active INIs'), fixedFont=False)

#------------------------------------------------------------------------------
class INI_ListErrors(EnabledLink):
    """List errors that make an INI Tweak invalid."""
    _text = _(u'List Errors...')
    _help = _(u'Lists any errors in the tweak file causing it to be invalid.')

    def _enable(self):
        return any(imap(lambda inf: inf.tweak_status < 0,
                        self.iselected_infos()))

    def Execute(self):
        """Handle printing out the errors."""
        error_text = u'\n'.join(inf.listErrors() for inf in
                                self.iselected_infos())
        balt.copyToClipboard(error_text)
        self._showLog(error_text, title=_(u'INI Tweak Errors'),
                      fixedFont=False)

#------------------------------------------------------------------------------
class INI_FileOpenOrCopy(OneItemLink):
    """Open specified file(s) only if they aren't Bash supplied defaults."""
    def _initData(self, window, selection):
        super(INI_FileOpenOrCopy, self)._initData(window, selection)
        if not len(selection) == 1:
            self._text = _(u'Open/Copy...')
            self._help = _(u'Only one INI file can be opened or copied at a time.')
        elif not self._selected_info.is_default_tweak:
            self._text = _(u'Open...')
            self._help = _(u"Open '%s' with the system's default program.") % selection[0]
        else:
            self._text = _(u'Copy...')
            self._help = _(u"Make an editable copy of the default tweak '%s'.") % selection[0]

    def Execute(self):
        if bosh.iniInfos.open_or_copy(self._selected_item):
            self.window.RefreshUI(redraw=[self._selected_item])

#------------------------------------------------------------------------------
class INI_Delete(balt.UIList_Delete, EnabledLink):
    """Delete the file and all backups."""

    def _initData(self, window, selection):
        super(INI_Delete, self)._initData(window, selection)
        self.selected = self.window.filterOutDefaultTweaks(self.selected)
        if len(self.selected) and len(selection) == 1:
            self._help = _(u"Delete %(filename)s.") % ({'filename': selection[0]})
        elif len(self.selected):
            self._help = _(
                u"Delete selected tweaks (default tweaks won't be deleted)")
        else: self._help = _(u"Bash default tweaks can't be deleted")

    def _enable(self): return len(self.selected) > 0

#------------------------------------------------------------------------------
class INI_Apply(EnabledLink):
    """Apply an INI Tweak."""
    _text = _(u'Apply')

    @property
    def menu_help(self):
        if len(self.selected) == 1:
            tweak = self.selected[0]
            return _(u"Applies '%(tweak)s' to '%(ini)s'.") % {
                'tweak': tweak, 'ini': self.window.current_ini_name}
        else:
            return _(u"Applies selected tweaks to '%(ini)s'.") % {
            'ini': self.window.current_ini_name}

    def _enable(self):
        return all(imap(bosh.INIInfo.is_applicable, self.iselected_infos()))

    def Execute(self):
        """Handle applying INI Tweaks."""
        if self.window.apply_tweaks(self.iselected_infos()):
            self.window.panel.ShowPanel(refresh_target=True)

#------------------------------------------------------------------------------
class INI_CreateNew(OneItemLink):
    """Create a new INI Tweak using the settings from the tweak file,
    but values from the target INI."""
    _text = _(u'Create Tweak with current settings...')

    @property
    def menu_help(self):
        if not len(self.selected) == 1:
            return _(u'Please choose one Ini Tweak')
        else:
            return _(u"Creates a new tweak based on '%(tweak)s' but with "
                          u"values from '%(ini)s'.") % {
                'tweak': (self.selected[0]), 'ini': self.window.current_ini_name}

    def _enable(self): return super(INI_CreateNew, self)._enable() and \
                              self._selected_info.tweak_status >= 0

    @balt.conversation
    def Execute(self):
        """Handle creating a new INI tweak."""
        pathFrom = self._selected_item
        fileName = pathFrom.sbody + u' - Copy' + pathFrom.ext
        tweak_path = self._askSave(
            title=_(u'Copy Tweak with current settings...'),
            defaultDir=bass.dirs['ini_tweaks'], defaultFile=fileName,
            wildcard=_(u'INI Tweak File (*.ini)|*.ini'))
        if bosh.iniInfos.duplicate_ini(pathFrom, tweak_path):
            self.window.RefreshUI(redraw=[tweak_path.tail], # to_add
                                  detail_item=tweak_path.tail)

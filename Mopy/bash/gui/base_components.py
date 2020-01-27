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

"""This module houses parts of the GUI code that form the basis for the the
more specialized parts (e.g. _AWidget)."""

__author__ = 'nycz, Infernio'

import wx as _wx

# Base Elements ---------------------------------------------------------------
class _AWidget(object):
    """Abstract base class for all GUI items. Holds a reference to the native
    wx widget that we abstract over."""
    def __init__(self):
        """Creates a new _AWidget instance. This initializes _native_widget to
        None, which will later receive a proper value inside the __init__
        methods of _AWidget's subclasses."""
        self._native_widget = None  # type: _wx.Window

    @property
    def widget_name(self): # type: () -> unicode
        """Returns the name of this widget.

        :return: This widget's name."""
        return self._native_widget.GetName()

    @widget_name.setter
    def widget_name(self, new_name): # type: (unicode) -> None
        """Sets the name of this widget to the specified name.

        :param new_name: The string to change this widget's name to."""
        self._native_widget.SetName(new_name)

    @property
    def visible(self): # type: () -> bool
        """Returns True if this widget is currently visible, i.e. if the user
        can see it in the GUI.

        :return: True if this widget is currently visible."""
        return self._native_widget.IsShown()

    @visible.setter
    def visible(self, is_visible): # type: (bool) -> None
        """Shows or hides this widget based on the specified parameter.

        :param is_visible: Whether or not to show this widget."""
        self._native_widget.Show(is_visible)

    @property
    def enabled(self): # type: () -> bool
        """Returns True if this widget is currently enabled, i.e. if the user
        can interact with it. Disabled widgets are typically styled in some way
        to indicate this fact to the user (e.g. greyed out).

        :return: True if this widget is currently enabled."""
        return self._native_widget.IsEnabled()

    @enabled.setter
    def enabled(self, enabled): # type: (bool) -> None
        """Enables or disables this widget based on the specified parameter.

        :param enabled: Whether or not to enable this widget."""
        self._native_widget.Enable(enabled)

    @property
    def tooltip(self): # type: () -> unicode
        """Returns the current contents of this widget's tooltip. If no tooltip
        is set, returns an empty string.

        :return: This widget's tooltip."""
        return self._native_widget.GetToolTipString() or u''

    @tooltip.setter
    def tooltip(self, new_tooltip): # type: (unicode) -> None
        """Sets the tooltip of this widget to the specified string. If the
        string is empty or None, the tooltip is simply removed.

        :param new_tooltip: The string to change the tooltip to."""
        if not new_tooltip:
            self._native_widget.UnsetToolTip()
        else:
            # TODO(inf) textwrap.fill(text, 50)
            self._native_widget.SetToolTipString(new_tooltip)

    # TODO: use a custom color class here
    @property
    def background_color(self): # type: () -> _wx.Colour
        """Returns the background color of this widget as a wx.Colour
        object.

        :return: The background color of this widget."""
        return self._native_widget.GetBackgroundColour()

    @background_color.setter
    def background_color(self, new_color): # type: (_wx.Colour) -> None
        """Changes the background color of this widget to the color represented
        by the specified wx.Colour object.

        :param new_color: The color to change the background color to."""
        self._native_widget.SetBackgroundColour(new_color)
        self._native_widget.Refresh()

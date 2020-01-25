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

"""This package contains the Oblivion specific patchers. This module
contains the data structures that are dynamically set on a per game basis in
bush."""
# Note patcher_text and not _patcher_txt - later is a class var of the gui patchers

from ....patcher import PatcherInfo as pi
from .importers import RoadImporter, CBash_RoadImporter
from .special import AlchemicalCatalogs, CBash_AlchemicalCatalogs, \
    SEWorldEnforcer, CBash_SEWorldEnforcer, CoblExhaustion, \
    CBash_CoblExhaustion, MFactMarker, CBash_MFactMarker

_spedial_patchers = (
    ("AlchemicalCatalogs", AlchemicalCatalogs, 'CBash_AlchemicalCatalogs'),
    ("CBash_AlchemicalCatalogs", CBash_AlchemicalCatalogs,
     'AlchemicalCatalogs'),
    ("SEWorldEnforcer", SEWorldEnforcer, 'CBash_SEWorldEnforcer'),
    ("CBash_SEWorldEnforcer", CBash_SEWorldEnforcer, 'SEWorldEnforcer')
)
gameSpecificPatchers = {
    pname: pi(ptype, twin, {'_patcher_txt': ptype.patcher_text,
                            'patcher_name': ptype.patcher_name}) for
    pname, ptype, twin in _spedial_patchers}

_list_pacthers =(
    ("CoblExhaustion", CoblExhaustion, 'CBash_CoblExhaustion'),
    ("CBash_CoblExhaustion", CBash_CoblExhaustion, 'CoblExhaustion'),
    ("MFactMarker", MFactMarker, 'CBash_MFactMarker'),
    ("CBash_MFactMarker", CBash_MFactMarker, 'MFactMarker')
)
gameSpecificListPatchers =  {
    pname: pi(ptype, twin, {'_patcher_txt': ptype.patcher_text,
                            'patcher_name': ptype.patcher_name,
                            'autoKey': ptype.autoKey}) for
    pname, ptype, twin in _list_pacthers}

_import_patchers = (
    ('RoadImporter', RoadImporter, 'CBash_RoadImporter'),
    ('CBash_RoadImporter', CBash_RoadImporter, 'RoadImporter')
)
game_specific_import_patchers = {
    pname: pi(ptype, twin,
              {'patcher_type': ptype, '_patcher_txt': ptype.patcher_text,
               'patcher_name': ptype.patcher_name, 'autoKey': ptype.autoKey})
    for pname, ptype, twin in _import_patchers
}

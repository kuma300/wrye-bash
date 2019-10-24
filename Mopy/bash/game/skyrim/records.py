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
"""This module contains the skyrim record classes."""
import itertools
import struct

from .constants import condition_function_data
from ... import brec
from ...bass import null1, null2, null3, null4
from ...bolt import Flags, DataDict, encode, struct_pack, struct_unpack
from ...brec import MelRecord, MelStructs, MelObject, MelGroups, MelStruct, \
    FID, MelGroup, MelString, MreLeveledListBase, MelSet, MelFid, MelNull, \
    MelOptStruct, MelFids, MreHeaderBase, MelBase, MelUnicode, MelFidList, \
    MelStructA, MreGmstBase, MelLString, MelSortedFidList, MelMODS, \
    MreHasEffects, MelColorInterpolator, MelValueInterpolator, MelUnion, \
    AttrValDecider, MelRegnEntrySubrecord, PartialLoadDecider, FlagDecider, \
    MelFloat, MelSInt8, MelSInt32, MelUInt8, MelUInt16, MelUInt32, \
    MelOptFloat, MelOptSInt16, MelOptSInt32, MelOptUInt8, MelOptUInt16, \
    MelOptUInt32, MelOptFid, MelCounter, MelPartialCounter
from ...exception import BoltError, ModError, ModSizeError, StateError
# Set MelModel in brec but only if unset, otherwise we are being imported from
# fallout4.records
if brec.MelModel is None:

    class _MelModel(MelGroup):
        """Represents a model record."""
        # MODB and MODD are no longer used by TES5Edit
        typeSets = {
            'MODL': ('MODL', 'MODT', 'MODS'),
            'MOD2': ('MOD2', 'MO2T', 'MO2S'),
            'MOD3': ('MOD3', 'MO3T', 'MO3S'),
            'MOD4': ('MOD4', 'MO4T', 'MO4S'),
            'MOD5': ('MOD5', 'MO5T', 'MO5S'),
            'DMDL': ('DMDL', 'DMDT', 'DMDS'),
        }

        def __init__(self, attr='model', subType='MODL'):
            types = self.__class__.typeSets[subType]
            MelGroup.__init__(
                self, attr,
                MelString(types[0], 'modPath'),
                # Ignore texture hashes - they're only an
                # optimization, plenty of records in Skyrim.esm
                # are missing them
                MelNull(types[1]),
                MelMODS(types[2], 'alternateTextures')
            )

        def debug(self, on=True):
            for element in self.elements[:2]: element.debug(on)
            return self

    brec.MelModel = _MelModel
from ...brec import MelModel

#------------------------------------------------------------------------------
# Record Elements    ----------------------------------------------------------
#------------------------------------------------------------------------------
# TODO(inf) Unused - use or bin (not sure if this actually works though)
class MreActor(MelRecord):
    """Creatures and NPCs."""

    def mergeFilter(self,modSet):
        """Filter out items that don't come from specified modSet.
        Filters spells, factions and items."""
        if not self.longFids: raise StateError(_("Fids not in long format"))
        self.spells = [x for x in self.spells if x[0] in modSet]
        self.factions = [x for x in self.factions if x.faction[0] in modSet]
        self.items = [x for x in self.items if x.item[0] in modSet]

#------------------------------------------------------------------------------
class MelBipedObjectData(MelStruct):
    """Handler for BODT/BOD2 subrecords.  Reads both types, writes only BOD2"""
    BipedFlags = Flags(0L,Flags.getNames(
            (0, 'head'),
            (1, 'hair'),
            (2, 'body'),
            (3, 'hands'),
            (4, 'forearms'),
            (5, 'amulet'),
            (6, 'ring'),
            (7, 'feet'),
            (8, 'calves'),
            (9, 'shield'),
            (10, 'bodyaddon1_tail'),
            (11, 'long_hair'),
            (12, 'circlet'),
            (13, 'bodyaddon2'),
            (14, 'dragon_head'),
            (15, 'dragon_lwing'),
            (16, 'dragon_rwing'),
            (17, 'dragon_body'),
            (18, 'bodyaddon7'),
            (19, 'bodyaddon8'),
            (20, 'decapate_head'),
            (21, 'decapate'),
            (22, 'bodyaddon9'),
            (23, 'bodyaddon10'),
            (24, 'bodyaddon11'),
            (25, 'bodyaddon12'),
            (26, 'bodyaddon13'),
            (27, 'bodyaddon14'),
            (28, 'bodyaddon15'),
            (29, 'bodyaddon16'),
            (30, 'bodyaddon17'),
            (31, 'fx01'),
        ))

    ## Legacy Flags, (For BODT subrecords) - #4 is the only one not discarded.
    LegacyFlags = Flags(0L,Flags.getNames(
            (0, 'modulates_voice'), #{>>> From ARMA <<<}
            (1, 'unknown_2'),
            (2, 'unknown_3'),
            (3, 'unknown_4'),
            (4, 'non_playable'), #{>>> From ARMO <<<}
        ))

    ArmorTypeFlags = Flags(0L,Flags.getNames(
        (0, 'light_armor'),
        (1, 'heavy_armor'),
        (2, 'clothing'),
        ))

    def __init__(self):
        MelStruct.__init__(self,'BOD2','=2I',(MelBipedObjectData.BipedFlags,'bipedFlags',0L),(MelBipedObjectData.ArmorTypeFlags,'armorFlags',0L))

    def getLoaders(self,loaders):
        # Loads either old style BODT or new style BOD2 records
        loaders['BOD2'] = self
        loaders['BODT'] = self

    def loadData(self, record, ins, sub_type, size_, readId):
        if sub_type == 'BODT':
            # Old record type, use alternate loading routine
            if size_ == 8:
                # Version 20 of this subrecord is only 8 bytes (armorType omitted)
                bipedFlags,legacyData = ins.unpack('=2I', size_, readId)
                armorFlags = 0
            elif size_ != 12:
                raise ModSizeError(ins.inName, readId, 12, size_, True)
            else:
                bipedFlags,legacyData,armorFlags = ins.unpack('=3I', size_, readId)
            # legacyData is discarded except for non-playable status
            setter = record.__setattr__
            setter('bipedFlags',MelBipedObjectData.BipedFlags(bipedFlags))
            legacyFlags = MelBipedObjectData.LegacyFlags(legacyData)
            record.flags1[2] = legacyFlags[4]
            setter('armorFlags',MelBipedObjectData.ArmorTypeFlags(armorFlags))
        else:
            # BOD2 - new style, MelStruct can handle it
            MelStruct.loadData(self, record, ins, sub_type, size_, readId)

class MelAttackData(MelStruct):
    """Wrapper around MelStruct to share some code between the NPC_ and RACE
    definitions."""
    DataFlags = Flags(0L, Flags.getNames('ignoreWeapon', 'bashAttack',
                                         'powerAttack', 'leftAttack',
                                         'rotatingAttack', 'unknown6',
                                         'unknown7', 'unknown8', 'unknown9',
                                         'unknown10', 'unknown11', 'unknown12',
                                         'unknown13', 'unknown14', 'unknown15',
                                         'unknown16',))

    def __init__(self):
        MelStruct.__init__(self, 'ATKD', '2f2I3fI3f', 'damageMult',
                           'attackChance', (FID, 'attackSpell'),
                           (MelAttackData.DataFlags, 'attackDataFlags', 0L),
                           'attackAngle', 'strikeAngle', 'stagger',
                           (FID, 'attackType'), 'knockdown', 'recoveryTime',
                           'staminaMult')

#------------------------------------------------------------------------------
class MelBounds(MelStruct):
    def __init__(self):
        MelStruct.__init__(self,'OBND','=6h',
            'boundX1','boundY1','boundZ1',
            'boundX2','boundY2','boundZ2')

#------------------------------------------------------------------------------
class MelCoed(MelOptStruct):
    """Needs custom unpacker to look at FormID type of owner.  If owner is an
    NPC then it is followed by a FormID.  If owner is a faction then it is
    followed by an signed integer or '=Iif' instead of '=IIf' """ # see #282
    def __init__(self):
        MelOptStruct.__init__(self,'COED','=IIf',(FID,'owner'),(FID,'glob'),
                              'itemCondition')
#------------------------------------------------------------------------------
class MelColor(MelStruct):
    """Required Color."""
    def __init__(self, signature='CNAM'):
        MelStruct.__init__(self, signature, '=4B', 'red', 'green', 'blue',
                           'unk_c')

class MelColorO(MelOptStruct):
    """Optional Color."""
    def __init__(self, signature='CNAM'):
        MelOptStruct.__init__(self, signature, '=4B', 'red', 'green', 'blue',
                           'unk_c')

#------------------------------------------------------------------------------
class MelCTDAHandler(MelStructs):
    """Represents the CTDA subrecord and it components. Difficulty is that FID
    state of parameters depends on function index."""
    def __init__(self):
        MelStructs.__init__(self,'CTDA','=B3sfH2siiIIi','conditions',
            'operFlag',('unused1',null3),'compValue','ifunc',('unused2',null2),
            'param1','param2','runOn','reference','param3')

    def getDefault(self):
        target = MelStructs.getDefault(self)
        target.form12345 = 'iiIIi'
        return target

    def hasFids(self,formElements):
        formElements.add(self)

    def loadData(self, record, ins, sub_type, size_, readId):
        if sub_type == 'CTDA':
            if size_ != 32 and size_ != 28 and size_ != 24 and size_ != 20:
                raise ModSizeError(ins.inName, readId, 32, size_, False)
        else:
            raise ModError(ins.inName,_(u'Unexpected subrecord: ')+readId)
        target = MelObject()
        record.conditions.append(target)
        target.__slots__ = self.attrs
        unpacked1 = ins.unpack('=B3sfH2s',12,readId)
        (target.operFlag,target.unused1,target.compValue,ifunc,target.unused2) = unpacked1
        #--Get parameters
        if ifunc not in condition_function_data:
            raise BoltError(u'Unknown condition function: %d\nparam1: '
                            u'%08X\nparam2: %08X' % (ifunc, ins.unpackRef(),
                                                     ins.unpackRef()))
        # Form1 is Param1 - 2 means fid
        form1 = 'I' if condition_function_data[ifunc][1] == 2 else 'i'
        # Form2 is Param2
        form2 = 'I' if condition_function_data[ifunc][2] == 2 else 'i'
        # Form3 is runOn
        form3 = 'I'
        # Form4 is reference, this is a formID when runOn = 2
        form4 = 'I'
        # Form5 is Param3
        form5 = 'I' if condition_function_data[ifunc][3] == 2 else 'i'
        if size_ == 32:
            form12345 = form1+form2+form3+form4+form5
            unpacked2 = ins.unpack(form12345,20,readId)
            (target.param1,target.param2,target.runOn,target.reference,target.param3) = unpacked2
        elif size_ == 28:
            form12345 = form1+form2+form3+form4
            unpacked2 = ins.unpack(form12345,16,readId)
            (target.param1,target.param2,target.runOn,target.reference) = unpacked2
            target.param3 = null4
        elif size_ == 24:
            form12345 = form1+form2+form3
            unpacked2 = ins.unpack(form12345,12,readId)
            (target.param1,target.param2,target.runOn) = unpacked2
            target.reference = null4
            target.param3 = null4
        elif size_ == 20:
            form12345 = form1+form2
            unpacked2 = ins.unpack(form12345,8,readId)
            (target.param1,target.param2) = unpacked2
            target.runOn = null4
            target.reference = null4
            target.param3 = null4
        # form12 = form1+form2
        # unpacked2 = ins.unpack(form12,8,readId)
        # (target.param1,target.param2) = unpacked2
        # target.unused3,target.reference,target.unused4 = ins.unpack('=4s2I',12,readId)
        else:
            raise ModSizeError(ins.inName, readId, 32, size_, False)
        (target.ifunc,target.form12345) = (ifunc,form12345)
        if self._debug:
            unpacked = unpacked1+unpacked2
            print u' ',zip(self.attrs,unpacked)
            if len(unpacked) != len(self.attrs):
                print u' ',unpacked

    def dumpData(self,record,out):
        for target in record.conditions:
            out.packSub('CTDA','=B3sfH2s'+target.form12345,
                target.operFlag, target.unused1, target.compValue,
                target.ifunc, target.unused2, target.param1, target.param2,
                target.runOn, target.reference, target.param3)

    def mapFids(self,record,function,save=False):
        for target in record.conditions:
            form12345 = target.form12345
            if form12345[0] == 'I':
                result = function(target.param1)
                if save: target.param1 = result
            if form12345[1] == 'I':
                result = function(target.param2)
                if save: target.param2 = result
            # runOn is intU32, never FID
            if len(form12345) > 3 and form12345[3] == 'I' and target.runOn == 2:
                result = function(target.reference)
                if save: target.reference = result
            if len(form12345) > 4 and form12345[4] == 'I':
                result = function(target.param3)
                if save: target.param3 = result

class MelConditionCounter(MelCounter):
    """Wraps MelCounter for the common task of defining a counter that counts
    MelConditions."""
    def __init__(self):
        MelCounter.__init__(
            self, MelUInt32('CITC', 'conditionCount'), counts='conditions')

class MelConditions(MelGroups):
    """Wraps MelGroups for the common task of defining an array of
    conditions. See also MelConditionCounter, which is commonly combined with
    this class."""
    def __init__(self, attr='conditions'):
        MelGroups.__init__(self, attr,
            MelCTDAHandler(),
            MelString('CIS1','param_cis1'),
            MelString('CIS2','param_cis2'),
        )

#------------------------------------------------------------------------------
class MelDecalData(MelOptStruct):
    """Represents Decal Data."""

    DecalDataFlags = Flags(0L,Flags.getNames(
            (0, 'parallax'),
            (1, 'alphaBlending'),
            (2, 'alphaTesting'),
            (3, 'noSubtextures'),
        ))

    def __init__(self):
        """Initialize elements."""
        MelOptStruct.__init__(
            self, 'DODT', '7f2B2s3Bs', 'minWidth', 'maxWidth',
            'minHeight', 'maxHeight', 'depth', 'shininess', 'parallaxScale',
            'parallaxPasses', (MelDecalData.DecalDataFlags, 'flags', 0L),
            ('unknownDecal1', null2), 'redDecal', 'greenDecal', 'blueDecal',
            ('unknownDecal2', null1)
        )

#------------------------------------------------------------------------------
class MelDestructible(MelGroup):
    """Represents a set of destruct record."""

    MelDestStageFlags = Flags(0L,Flags.getNames(
        (0, 'capDamage'),
        (1, 'disable'),
        (2, 'destroy'),
        (3, 'ignoreExternalDmg'),
        ))

    def __init__(self,attr='destructible'):
        MelGroup.__init__(self,attr,
            MelStruct('DEST','i2B2s','health','count','vatsTargetable','dest_unused'),
            MelGroups('stages',
                MelStruct('DSTD','=4Bi2Ii','health','index','damageStage',
                         (MelDestructible.MelDestStageFlags,'flags',0L),'selfDamagePerSecond',
                         (FID,'explosion',None),(FID,'debris',None),'debrisCount'),
                MelModel('model','DMDL'),
                MelBase('DSTF','footer'),
            ),
        )

#------------------------------------------------------------------------------
class MelEffects(MelGroups):
    """Represents ingredient/potion/enchantment/spell effects."""

    def __init__(self,attr='effects'):
        MelGroups.__init__(self,attr,
            MelFid('EFID','name'), # baseEffect, name
            MelStruct('EFIT','f2I','magnitude','area','duration',),
            MelConditions(),
        )

#------------------------------------------------------------------------------
# TODO(inf) Unused - move to brec and use it everywhere!
class MelIcons(MelGroup):
    """Handles ICON and MICO."""

    def __init__(self,attr='iconsIaM'):
        # iconsIaM = icons ICON and MICO
        MelGroup.__init__(self,attr,
            MelString('ICON','iconPath'),
            MelString('MICO','smallIconPath'),
        )
    def dumpData(self,record,out):
        if record.iconsIaM and record.iconsIaM.iconPath:
            MelGroup.dumpData(self,record,out)
        if record.iconsIaM and record.iconsIaM.smallIconPath:
            MelGroup.dumpData(self,record,out)

#------------------------------------------------------------------------------
# TODO(inf) Unused - move to brec and use it everywhere!
class MelIcons2(MelGroup):
    """Handles ICON and MICO."""

    def __init__(self,attr='iconsIaM2'):
        # iconsIaM = icons ICON and MICO
        MelGroup.__init__(self,attr,
            MelString('ICO2','iconPath2'),
            MelString('MIC2','smallIconPath2'),
        )
    def dumpData(self,record,out):
        if record.iconsIaM and record.iconsIaM.iconPath2:
            MelGroup.dumpData(self,record,out)
        if record.iconsIaM and record.iconsIaM.smallIconPath2:
            MelGroup.dumpData(self,record,out)

#------------------------------------------------------------------------------
class MelItems(MelGroups):
    """Wraps MelGroups for the common task of defining a list of items."""
    def __init__(self):
        MelGroups.__init__(self, 'items',
            MelStruct('CNTO', 'Ii', (FID, 'item', None), 'count'),
            MelCoed(),
        )

class MelItemsCounter(MelCounter):
    """Wraps MelCounter for the common task of defining an items counter."""
    def __init__(self):
        MelCounter.__init__(
            self, MelUInt32('COCT', 'item_count'), counts='items')

#------------------------------------------------------------------------------
class MelKeywords(MelGroup):
    """Wraps MelGroup for the common task of defining a list of keywords"""
    def __init__(self):
        MelGroup.__init__(self, 'keywords',
            # TODO(inf) Kept it as such, why little-endian?
            MelCounter(MelStruct('KSIZ', '<I', 'keyword_count'),
                       counts='keyword_list'),
            MelFidList('KWDA', 'keyword_list'),
        )

#------------------------------------------------------------------------------
class MelOwnership(MelGroup):
    """Handles XOWN, XRNK for cells and cell children."""

    def __init__(self,attr='ownership'):
        MelGroup.__init__(self,attr,
            MelFid('XOWN','owner'),
            MelOptSInt32('XRNK', ('rank', None)),
        )

    def dumpData(self,record,out):
        if record.ownership and record.ownership.owner:
            MelGroup.dumpData(self,record,out)

#------------------------------------------------------------------------------
class MelVmad(MelBase):
    """Virtual Machine data (VMAD)"""
    # Maybe use this later for better access to Fid,Aid pairs?
    ##ObjectRef = collections.namedtuple('ObjectRef',['fid','aid'])
    class FragmentInfo(object):
        __slots__ = ('unk','fileName',)
        def __init__(self):
            self.unk = 2
            self.fileName = u''

        def loadData(self,ins,Type,readId):
            if Type == 'INFO':
                # INFO record fragment scripts are by default stored in a TIF file,
                # i.e., a file named "TIF_<editorID>_<formID>". Since most INFO records
                # do not have an editorID, this actually ends up being "TIF__<formID>"
                # (with two underscores, not one).
                raise Exception(u"Fragment Scripts for 'INFO' records are not implemented.")
            elif Type == 'PACK':
                self.unk,count = ins.unpack('=bB',2,readId)
                self.fileName = ins.readString16(readId)
                count = bin(count).count('1')
            elif Type == 'PERK':
                self.unk, = ins.unpack('=b',1,readId)
                self.fileName = ins.readString16(readId)
                count, = ins.unpack('=H',2,readId)
            elif Type == 'QUST':
                self.unk,count = ins.unpack('=bH',3,readId)
                self.fileName = ins.readString16(readId)
            elif Type == 'SCEN':
                # SCEN record fragment scripts are by default stored in a SF file,
                # i.e., a file named "SF_<editorID>_<formID>".
                raise Exception(u"Fragment Scripts for 'SCEN' records are not implemented.")
            else:
                raise Exception(u"Unexpected Fragment Scripts for record type '%s'." % Type)
            return count

        def dumpData(self,Type,count):
            fileName = encode(self.fileName)
            if Type == 'INFO':
                raise Exception(u"Fragment Scripts for 'INFO' records are not implemented.")
            elif Type == 'PACK':
                # TODO: check if this is right!
                count = int(count*'1',2)
                data = struct_pack('=bBH', self.unk, count,
                                   len(fileName)) + fileName
            elif Type == 'PERK':
                data = struct_pack('=bH', self.unk, len(fileName)) + fileName
                data += struct_pack('=H', count)
            elif Type == 'QUST':
                data = struct_pack('=bHH', self.unk, count,
                                   len(fileName)) + fileName
            elif Type == 'SCEN':
                raise Exception(u"Fragment Scripts for 'SCEN' records are not implemented.")
            else:
                raise Exception(u"Unexpected Fragment Scripts for record type '%s'." % Type)
            return data

    class INFOFragment(object):
        pass

    class PACKFragment(object):
        __slots__ = ('unk','scriptName','fragmentName',)
        def __init__(self):
            self.unk = 0
            self.scriptName = u''
            self.fragmentName = u''

        def loadData(self,ins,readId):
            self.unk, = ins.unpack('=b',1,readId)
            self.scriptName = ins.readString16(readId)
            self.fragmentName = ins.readString16(readId)

        def dumpData(self):
            scriptName = encode(self.scriptName)
            fragmentName = encode(self.fragmentName)
            data = struct_pack('=bH', self.unk, len(scriptName)) + scriptName
            data += struct_pack('=H', len(fragmentName)) + fragmentName
            return data

    class PERKFragment(object):
        __slots__ = ('index','unk1','unk2','scriptName','fragmentName',)
        def __init__(self):
            self.index = -1
            self.unk1 = 0
            self.unk2 = 0
            self.scriptName = u''
            self.fragmentName= u''

        def loadData(self,ins,readId):
            self.index,self.unk1,self.unk2 = ins.unpack('=Hhb',4,readId)
            self.scriptName = ins.readString16(readId)
            self.fragmentName = ins.readString16(readId)

        def dumpData(self):
            scriptName = encode(self.scriptName)
            fragmentName = encode(self.fragmentName)
            data = struct_pack('=HhbH', self.index, self.unk1, self.unk2,
                               len(scriptName)) + scriptName
            data += struct_pack('=H', len(fragmentName)) + fragmentName
            return data

    class QUSTFragment(object):
        __slots__ = ('index','unk1','logentry','unk2','scriptName','fragmentName',)
        def __init__(self):
            self.index = -1
            self.unk1 = 0
            self.logentry = 0
            self.unk2 = 1
            self.scriptName = u''
            self.fragmentName = u''

        def loadData(self,ins,readId):
            self.index,self.unk1,self.logentry,self.unk2 = ins.unpack('=Hhib',9,readId)
            self.scriptName = ins.readString16(readId)
            self.fragmentName = ins.readString16(readId)

        def dumpData(self):
            scriptName = encode(self.scriptName)
            fragmentName = encode(self.fragmentName)
            data = struct_pack('=HhibH', self.index, self.unk1, self.logentry,
                               self.unk2, len(scriptName)) + scriptName
            data += struct_pack('=H', len(fragmentName)) + fragmentName
            return data

    class SCENFragment(object):
        pass

    FragmentMap = {'INFO': INFOFragment,
                   'PACK': PACKFragment,
                   'PERK': PERKFragment,
                   'QUST': QUSTFragment,
                   'SCEN': SCENFragment,
                   }

    class Property(object):
        __slots__ = ('name','status','value',)
        def __init__(self):
            self.name = u''
            self.status = 1
            self.value = None

        def loadData(self,ins,version,objFormat,readId):
            insUnpack = ins.unpack
            # Script Property
            self.name = ins.readString16(readId)
            if version >= 4:
                Type,self.status = insUnpack('=2B',2,readId)
            else:
                Type, = insUnpack('=B',1,readId)
                self.status = 1
            # Data
            if Type == 0:
                # Null
                return
            elif Type == 1:
                # Object (8 Bytes)
                if objFormat == 1:
                    fid,aid,nul = insUnpack('=IHH',8,readId)
                else:
                    nul,aid,fid = insUnpack('=HHI',8,readId)
                self.value = (fid,aid)
            elif Type == 2:
                # String
                self.value = ins.readString16(readId)
            elif Type == 3:
                # Int32
                self.value, = insUnpack('=i',4,readId)
            elif Type == 4:
                # Float
                self.value, = insUnpack('=f',4,readId)
            elif Type == 5:
                # Bool (Int8)
                self.value = bool(insUnpack('=b',1,readId)[0])
            elif Type == 11:
                # List of Objects
                count, = insUnpack('=I',4,readId)
                if objFormat == 1: # (fid,aid,nul)
                    value = insUnpack('='+count*'IHH',count*8,readId)
                    self.value = zip(value[::3],value[1::3]) # list of (fid,aid)'s
                else: # (nul,aid,fid)
                    value = insUnpack('='+count*'HHI',count*8,readId)
                    self.value = zip(value[2::3],value[1::3]) # list of (fid,aid)'s
            elif Type == 12:
                # List of Strings
                count, = insUnpack('=I',4,readId)
                self.value = [ins.readString16(readId) for i in xrange(count)]
            elif Type == 13:
                # List of Int32s
                count, = insUnpack('=I',4,readId)
                self.value = list(insUnpack('='+`count`+'i',count*4,readId))
            elif Type == 14:
                # List of Floats
                count, = insUnpack('=I',4,readId)
                self.value = list(insUnpack('='+`count`+'f',count*4,readId))
            elif Type == 15:
                # List of Bools (int8)
                count, = insUnpack('=I',4,readId)
                self.value = map(bool,insUnpack('='+`count`+'b',count,readId))
            else:
                raise Exception(u'Unrecognized VM Data property type: %i' % Type)

        def dumpData(self):
            ## Property Entry
            # Property Name
            name = encode(self.name)
            data = struct_pack('=H', len(name)) + name
            # Property Type
            value = self.value
            # Type 0 - Null
            if value is None:
                pass
            # Type 1 - Object Reference
            elif isinstance(value,tuple):
                # Object Format 1 - (Fid, Aid, NULL)
                #data += structPack('=BBIHH',1,self.status,value[0],value[1],0)
                # Object Format 2 - (NULL, Aid, Fid)
                data += struct_pack('=BBHHI', 1, self.status, 0, value[1],
                                    value[0])
            # Type 2 - String
            elif isinstance(value,basestring):
                value = encode(value)
                data += struct_pack('=BBH', 2, self.status, len(value)) + value
            # Type 3 - Int
            elif isinstance(value,(int,long)) and not isinstance(value,bool):
                data += struct_pack('=BBi', 3, self.status, value)
            # Type 4 - Float
            elif isinstance(value,float):
                data += struct_pack('=BBf', 4, self.status, value)
            # Type 5 - Bool
            elif isinstance(value,bool):
                data += struct_pack('=BBb', 5, self.status, value)
            # Type 11 -> 15 - lists, Only supported if vmad version >= 5
            elif isinstance(value,list):
                # Empty list, fail to object refereneces?
                count = len(value)
                if not count:
                    data += struct_pack('=BBI', 11, self.status, count)
                else:
                    Type = value[0]
                    # Type 11 - Object References
                    if isinstance(Type,tuple):
                        # Object Format 1 - value = [fid,aid,NULL, fid,aid,NULL, ...]
                        #value = list(from_iterable([x+(0,) for x in value]))
                        #data += structPack('=BBI'+count*'IHH',11,self.status,count,*value)
                        # Object Format 2 - value = [NULL,aid,fid, NULL,aid,fid, ...]
                        value = list(itertools.chain.from_iterable(
                            [(0,aid,fid) for fid,aid in value]))
                        data += struct_pack('=BBI' + count * 'HHI', 11,
                                            self.status, count, *value)
                    # Type 12 - Strings
                    elif isinstance(Type,basestring):
                        data += struct_pack('=BBI', 12, self.status, count)
                        for string in value:
                            string = encode(string)
                            data += struct_pack('=H', len(string)) + string
                    # Type 13 - Ints
                    elif isinstance(Type,(int,long)) and not isinstance(
                            Type,bool):
                        data += struct_pack('=BBI' + `count` + 'i', 13,
                                            self.status, count, *value)
                    # Type 14 - Floats
                    elif isinstance(Type,float):
                        data += struct_pack('=BBI' + `count` + 'f', 14,
                                            self.status, count, *value)
                    # Type 15 - Bools
                    elif isinstance(Type,bool):
                        data += struct_pack('=BBI' + `count` + 'b', 15,
                                            self.status, count, *value)
                    else:
                        raise Exception(u'Unrecognized VMAD property type: %s' % type(Type))
            else:
                raise Exception(u'Unrecognized VMAD property type: %s' % type(value))
            return data

    class Script(object):
        __slots__ = ('name','status','properties',)
        def __init__(self):
            self.name = u''
            self.status = 0
            self.properties = []

        def loadData(self,ins,version,objFormat,readId):
            Property = MelVmad.Property
            self.properties = []
            propAppend = self.properties.append
            # Script Entry
            self.name = ins.readString16(readId)
            if version >= 4:
                self.status,propCount = ins.unpack('=BH',3,readId)
            else:
                self.status = 0
                propCount, = ins.unpack('=H',2,readId)
            # Properties
            for x in xrange(propCount):
                prop = Property()
                prop.loadData(ins,version,objFormat,readId)
                propAppend(prop)

        def dumpData(self):
            ## Script Entry
            # scriptName
            name = encode(self.name)
            data = struct_pack('=H', len(name)) + name
            # status, property count
            data += struct_pack('=BH', self.status, len(self.properties))
            # properties
            for prop in self.properties:
                data += prop.dumpData()
            return data

        def mapFids(self,record,function,save=False):
            for prop in self.properties:
                value = prop.value
                # Type 1 - Object Reference: (fid,aid)
                if isinstance(value,tuple):
                    value = (function(value[0]),value[1])
                    if save:
                        prop.value = value
                # Type 11 - List of Object References: [(fid,aid), (fid,aid), ...]
                elif isinstance(value,list) and value and isinstance(value[0],tuple):
                    value = [(function(x[0]),x[1]) for x in value]
                    if save:
                        prop.value = value

    class Alias(object):
        __slots__ = ('fid','aid','scripts',)
        def __init__(self):
            self.fid = None
            self.aid = 0
            self.scripts = []

        def loadData(self,ins,version,objFormat,readId):
            insUnpack = ins.unpack
            if objFormat == 1:
                self.fid,self.aid,nul = insUnpack('=IHH',8,readId)
            else:
                nul,self.aid,self.fid = insUnpack('=HHI',8,readId)
            # _version - always the same as the primary script's version.
            # _objFormat - always the same as the primary script's objFormat.
            _version,_objFormat,count = insUnpack('=hhH',6,readId)
            Script = MelVmad.Script
            self.scripts = []
            scriptAppend = self.scripts.append
            for x in xrange(count):
                script = Script()
                script.loadData(ins,version,objFormat,readId)
                scriptAppend(script)

        def dumpData(self):
            # Object Format 2 - (NULL, Aid, Fid)
            data = struct_pack('=HHI', 0, self.aid, self.fid)
            # vmad version, object format, script count
            data += struct_pack('=3H', 5, 2, len(self.scripts))
            # Primary Scripts
            for script in self.scripts:
                data += script.dumpData()
            return data

        def mapFids(self,record,function,save=False):
            if self.fid:
                fid = function(self.fid)
                if save: self.fid = fid
            for script in self.scripts:
                script.mapFids(record,function,save)

    class Vmad(object):
        __slots__ = ('scripts','fragmentInfo','fragments','aliases',)
        def __init__(self):
            self.scripts = []
            self.fragmentInfo = None
            self.fragments = None
            self.aliases = None

        def loadData(self, record, ins, size_, readId):
            insTell = ins.tell
            endOfField = insTell() + size_
            self.scripts = []
            scriptsAppend = self.scripts.append
            Script = MelVmad.Script
            # VMAD Header
            version,objFormat,scriptCount = ins.unpack('=3H',6,readId)
            # Primary Scripts
            for x in xrange(scriptCount):
                script = Script()
                script.loadData(ins,version,objFormat,readId)
                scriptsAppend(script)
            # Script Fragments
            if insTell() < endOfField:
                self.fragmentInfo = MelVmad.FragmentInfo()
                Type = record.recType
                fragCount = self.fragmentInfo.loadData(ins,Type,readId)
                self.fragments = []
                fragAppend = self.fragments.append
                Fragment = MelVmad.FragmentMap[Type]
                for x in xrange(fragCount):
                    frag = Fragment()
                    frag.loadData(ins,readId)
                    fragAppend(frag)
                # Alias Scripts
                if Type == 'QUST':
                    aliasCount, = ins.unpack('=H',2,readId)
                    Alias = MelVmad.Alias
                    self.aliases = []
                    aliasAppend = self.aliases.append
                    for x in xrange(aliasCount):
                        alias = Alias()
                        alias.loadData(ins,version,objFormat,readId)
                        aliasAppend(alias)
                else:
                    self.aliases = None
            else:
                self.fragmentInfo = None
                self.fragments = None
                self.aliases = None

        def dumpData(self,record):
            # Header
            #data = structPack('=3H',4,1,len(self.scripts)) # vmad version, object format, script count
            data = struct_pack('=3H', 5, 2, len(self.scripts)) # vmad version, object format, script count
            # Primary Scripts
            for script in self.scripts:
                data += script.dumpData()
            # Script Fragments
            if self.fragments:
                Type = record.recType
                data += self.fragmentInfo.dumpData(Type,len(self.fragments))
                for frag in self.fragments:
                    data += frag.dumpData()
                if Type == 'QUST':
                    # Alias Scripts
                    aliases = self.aliases
                    data += struct_pack('=H', len(aliases))
                    for alias in aliases:
                        data += alias.dumpData()
            return data

        def mapFids(self,record,function,save=False):
            for script in self.scripts:
                script.mapFids(record,function,save)
            if not self.aliases:
                return
            for alias in self.aliases:
                alias.mapFids(record,function,save)

    def __init__(self, subType='VMAD', attr='vmdata'):
        MelBase.__init__(self, subType, attr)

    def hasFids(self,formElements):
        formElements.add(self)

    def setDefault(self,record):
        record.__setattr__(self.attr,None)

    def getDefault(self):
        target = MelObject()
        return self.setDefault(target)

    def loadData(self, record, ins, sub_type, size_, readId):
        vmad = MelVmad.Vmad()
        vmad.loadData(record, ins, size_, readId)
        record.__setattr__(self.attr,vmad)

    def dumpData(self,record,out):
        vmad = record.__getattribute__(self.attr)
        if vmad is None: return
        # Write
        out.packSub(self.subType,vmad.dumpData(record))

    def mapFids(self,record,function,save=False):
        vmad = record.__getattribute__(self.attr)
        if vmad is None: return
        vmad.mapFids(record,function,save)

#------------------------------------------------------------------------------
# Skyrim Records --------------------------------------------------------------
#------------------------------------------------------------------------------
class MreHeader(MreHeaderBase):
    """TES4 Record.  File header."""
    classType = 'TES4'

    melSet = MelSet(
        MelStruct('HEDR', 'f2I', ('version', 1.7), 'numRecords',
                  ('nextObject', 0x800)),
        MelUnicode('CNAM','author',u'',512),
        MelUnicode('SNAM','description',u'',512),
        MreHeaderBase.MelMasterName('MAST','masters'),
        MelNull('DATA'), # 8 Bytes in Length
        MelFidList('ONAM','overrides',),
        MelBase('SCRN', 'screenshot'),
        MelBase('INTV', 'unknownINTV'),
        MelBase('INCC', 'unknownINCC'),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreAact(MelRecord):
    """Action."""
    classType = 'AACT'
    melSet = MelSet(
        MelString('EDID','eid'),
        MelColorO('CNAM'),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreAchr(MelRecord):
    """Placed NPC."""
    classType = 'ACHR'
    _flags = Flags(0L,Flags.getNames('oppositeParent','popIn'))

    ActivateParentsFlags = Flags(0L,Flags.getNames(
            (0, 'parentActivateOnly'),
        ))

    # TODO class MelAchrPdto: if 'type' in PDTO is equal to 1 then 'data' is
    #  '4s', not FID

    melSet = MelSet(
        MelString('EDID','eid'),
        MelVmad(),
        MelFid('NAME','base'),
        MelFid('XEZN','encounterZone'),
        MelBase('XRGD','ragdollData'),
        MelBase('XRGB','ragdollBipedData'),
        MelGroup('patrolData',
            MelFloat('XPRD', 'idleTime',),
            MelNull('XPPA'),
            MelFid('INAM','idle'),
            MelGroup('patrolData',
                MelBase('SCHR','schr_p'),
                MelBase('SCDA','scda_p'),
                MelBase('SCTX','sctx_p'),
                MelBase('QNAM','qnam_p'),
                MelBase('SCRO','scro_p'),
            ),
            MelStructs('PDTO','2I','topicData','type',(FID,'data'),),
            MelFid('TNAM','topic'),
        ),
        MelSInt32('XLCM', 'levelModifier'),
        MelFid('XMRC','merchantContainer',),
        MelSInt32('XCNT', 'count'),
        MelFloat('XRDS', 'radius',),
        MelFloat('XHLP', 'health',),
        MelGroup('linkedReferences',
            MelSortedFidList('XLKR', 'fids'),
        ),
        MelGroup('activateParents',
            MelUInt32('XAPD', (ActivateParentsFlags, 'flags', 0L)),
            MelGroups('activateParentRefs',
                MelStruct('XAPR','If',(FID,'reference'),'delay',),
            ),
        ),
        MelStruct('XCLP','3Bs3Bs','startColorRed','startColorGreen','startColorBlue',
                  'startColorUnknown','endColorRed','endColorGreen','endColorBlue',
                  'endColorUnknown',),
        MelFid('XLCN','persistentLocation',),
        MelFid('XLRL','locationReference',),
        MelNull('XIS2'),
        MelFidList('XLRT','locationRefType',),
        MelFid('XHOR','horse',),
        MelFloat('XHTW', 'headTrackingWeight',),
        MelFloat('XFVC', 'favorCost',),
        MelOptStruct('XESP','IB3s',(FID,'parent'),(_flags,'parentFlags'),'unused',),
        MelOwnership(),
        MelOptFid('XEMI', 'emittance'),
        MelFid('XMBR','multiBoundReference',),
        MelNull('XIBS'),
        MelOptFloat('XSCL', ('scale', 1.0)),
        MelOptStruct('DATA','=6f',('posX',None),('posY',None),('posZ',None),('rotX',None),('rotY',None),('rotZ',None)),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreActi(MelRecord):
    """Activator."""
    classType = 'ACTI'

    ActivatorFlags = Flags(0L,Flags.getNames(
        (0, 'noDisplacement'),
        (1, 'ignoredBySandbox'),
    ))

    melSet = MelSet(
        MelString('EDID','eid'),
        MelVmad(),
        MelBounds(),
        MelLString('FULL','full'),
        MelModel(),
        MelDestructible(),
        MelKeywords(),
        MelColor('PNAM'),
        MelOptFid('SNAM', 'dropSound'),
        MelOptFid('VNAM', 'pickupSound'),
        MelOptFid('WNAM', 'water'),
        MelLString('RNAM', 'activate_text_override'),
        MelOptUInt16('FNAM', (ActivatorFlags, 'flags', 0L)),
        MelOptFid('KNAM', 'keyword'),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreAddn(MelRecord):
    """Addon Node."""
    classType = 'ADDN'

    _AddnFlags = Flags(0L, Flags.getNames(
        (1, 'alwaysLoaded'),
    ))

    melSet = MelSet(
        MelString('EDID','eid'),
        MelBounds(),
        MelModel(),
        MelSInt32('DATA', 'node_index'),
        MelOptFid('SNAM', 'ambientSound'),
        MelStruct('DNAM', '2H', 'master_particle_system_cap',
                  (_AddnFlags, 'addon_flags')),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreAlch(MelRecord,MreHasEffects):
    """Ingestible."""
    classType = 'ALCH'

    IngestibleFlags = Flags(0L,Flags.getNames(
        (0, 'noAutoCalc'),
        (1, 'isFood'),
        (16, 'medicine'),
        (17, 'poison'),
    ))

    melSet = MelSet(
        MelString('EDID','eid'),
        MelBounds(),
        MelLString('FULL','full'),
        MelKeywords(),
        MelLString('DESC','description'),
        MelModel(),
        MelDestructible(),
        MelString('ICON','iconPath'),
        MelString('MICO','smallIconPath'),
        MelOptFid('YNAM', 'pickupSound'),
        MelOptFid('ZNAM', 'dropSound'),
        MelOptFid('ETYP', 'equipType'),
        MelFloat('DATA', 'weight'),
        MelStruct('ENIT','i2IfI','value',(IngestibleFlags,'flags',0L),
                  'addiction','addictionChance','soundConsume',),
        MelEffects(),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreAmmo(MelRecord):
    """Ammunition."""
    classType = 'AMMO'

    AmmoTypeFlags = Flags(0L,Flags.getNames(
        (0, 'notNormalWeapon'),
        (1, 'nonPlayable'),
        (2, 'nonBolt'),
    ))

    melSet = MelSet(
        MelString('EDID','eid'),
        MelBounds(),
        MelLString('FULL','full'),
        MelModel(),
        MelString('ICON','iconPath'),
        MelString('MICO','smallIconPath'),
        MelDestructible(),
        MelFid('YNAM','pickupSound'),
        MelFid('ZNAM','dropSound'),
        MelLString('DESC','description'),
        MelKeywords(),
        MelStruct('DATA','IIfI',(FID,'projectile'),(AmmoTypeFlags,'flags',0L),'damage','value'),
        MelString('ONAM', 'short_name'),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreAnio(MelRecord):
    """Animated Object."""
    classType = 'ANIO'
    melSet = MelSet(
        MelString('EDID','eid'),
        MelModel(),
        MelString('BNAM', 'unload_event'),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreAppa(MelRecord):
    """Alchemical Apparatus."""
    classType = 'APPA'

    melSet = MelSet(
        MelString('EDID','eid'),
        MelVmad(),
        MelBounds(),
        MelLString('FULL','full'),
        MelModel(),
        MelString('ICON','iconPath'),
        MelString('MICO','smallIconPath'),
        MelDestructible(),
        MelFid('YNAM','pickupSound'),
        MelFid('ZNAM','dropSound'),
        MelUInt32('QUAL', 'quality'),
        MelLString('DESC','description'),
        MelStruct('DATA','If','value','weight'),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreArma(MelRecord):
    """Armor Addon."""
    classType = 'ARMA'

    WeightSliderFlags = Flags(0L,Flags.getNames(
            (0, 'unknown0'),
            (1, 'enabled'),
        ))

    melSet = MelSet(
        MelString('EDID','eid'),
        MelBipedObjectData(),
        MelFid('RNAM','race'),
        MelStruct('DNAM','4B2sBsf','malePriority','femalePriority',
                  (WeightSliderFlags,'maleFlags',0L),
                  (WeightSliderFlags,'femaleFlags',0L),
                  'unknown','detectionSoundValue','unknown1','weaponAdjust',),
        MelModel('male_model','MOD2'),
        MelModel('female_model','MOD3'),
        MelModel('male_model_1st','MOD4'),
        MelModel('female_model_1st','MOD5'),
        MelOptFid('NAM0', 'skin0'),
        MelOptFid('NAM1', 'skin1'),
        MelOptFid('NAM2', 'skin2'),
        MelOptFid('NAM3', 'skin3'),
        MelFids('MODL','races'),
        MelOptFid('SNDD', 'footstepSound'),
        MelOptFid('ONAM', 'art_object'),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreArmo(MelRecord):
    """Armor."""
    classType = 'ARMO'

    melSet = MelSet(
        MelString('EDID','eid'),
        MelVmad(),
        MelBounds(),
        MelLString('FULL','full'),
        MelOptFid('EITM', 'enchantment'),
        MelOptSInt16('EAMT', 'enchantmentAmount'),
        MelModel('model2','MOD2'),
        MelString('ICON','maleIconPath'),
        MelString('MICO','maleSmallIconPath'),
        MelModel('model4','MOD4'),
        MelString('ICO2','femaleIconPath'),
        MelString('MIC2','femaleSmallIconPath'),
        MelBipedObjectData(),
        MelDestructible(),
        MelOptFid('YNAM', 'pickupSound'),
        MelOptFid('ZNAM', 'dropSound'),
        MelString('BMCT', 'ragdollTemplatePath'), #Ragdoll Constraint Template
        MelOptFid('ETYP', 'equipType'),
        MelOptFid('BIDS', 'bashImpact'),
        MelOptFid('BAMT', 'material'),
        MelOptFid('RNAM', 'race'),
        MelKeywords(),
        MelLString('DESC','description'),
        MelFids('MODL','addons'),
        MelStruct('DATA','=if','value','weight'),
        MelSInt32('DNAM', 'armorRating'),
        MelFid('TNAM','templateArmor'),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreArto(MelRecord):
    """Art Effect Object."""
    classType = 'ARTO'

    ArtoTypeFlags = Flags(0L,Flags.getNames(
            (0, 'magic_casting'),
            (1, 'magic_hit_effect'),
            (2, 'enchantment_effect'),
        ))

    melSet = MelSet(
        MelString('EDID','eid'),
        MelBounds(),
        MelModel(),
        MelUInt32('DNAM', (ArtoTypeFlags, 'flags', 0L)),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreAspc(MelRecord):
    """Acoustic Space."""
    classType = 'ASPC'
    melSet = MelSet(
        MelString('EDID','eid'),
        MelBounds(),
        MelOptFid('SNAM', 'ambientSound'),
        MelOptFid('RDAT', 'regionData'),
        MelOptFid('BNAM', 'reverb'),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreAstp(MelRecord):
    """Association Type."""
    classType = 'ASTP'

    AstpTypeFlags = Flags(0L,Flags.getNames('related'))

    melSet = MelSet(
        MelString('EDID','eid'),
        MelString('MPRT','maleParent'),
        MelString('FPRT','femaleParent'),
        MelString('MCHT','maleChild'),
        MelString('FCHT','femaleChild'),
        MelUInt32('DATA', (AstpTypeFlags, 'flags', 0L)),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreAvif(MelRecord):
    """Actor Value Information."""
    classType = 'AVIF'

    class MelCnamLoaders(DataDict):
        """Since CNAM subrecords occur in two different places, we need
        to replace ordinary 'loaders' dictionary with a 'dictionary' that will
        return the correct element to handle the CNAM subrecord. 'Correct'
        element is determined by which other subrecords have been
        encountered."""
        def __init__(self,loaders,actorinfo,perks):
            self.data = loaders
            self.type_cnam = {'EDID':actorinfo, 'PNAM':perks}
            self.cnam = actorinfo #--Which cnam element loader to use next.
        def __getitem__(self,key):
            if key == 'CNAM': return self.cnam
            self.cnam = self.type_cnam.get(key, self.cnam)
            return self.data[key]

    melSet = MelSet(
        MelString('EDID','eid'),
        MelLString('FULL','full'),
        MelLString('DESC','description'),
        MelString('ANAM','abbreviation'),
        MelBase('CNAM','cnam_p'),
        MelOptStruct('AVSK','4f','skillUseMult','skillOffsetMult','skillImproveMult',
                     'skillImproveOffset',),
        MelGroups('perkTree',
            MelFid('PNAM', 'perk',),
            MelBase('FNAM','fnam_p'),
            MelUInt32('XNAM', 'perkGridX'),
            MelUInt32('YNAM', 'perkGridY'),
            MelFloat('HNAM', 'horizontalPosition'),
            MelFloat('VNAM', 'verticalPosition'),
            MelFid('SNAM','associatedSkill',),
            MelStructs('CNAM','I','connections','lineToIndex',),
            MelUInt32('INAM', 'index',),
        ),
    )
    melSet.loaders = MelCnamLoaders(melSet.loaders,melSet.elements[4],melSet.elements[6])
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreBook(MelRecord):
    """Book."""
    classType = 'BOOK'

    _book_type_flags = Flags(0, Flags.getNames(
        'teaches_skill',
        'cant_be_taken',
        'teaches_spell',
    ))

    melSet = MelSet(
        MelString('EDID','eid'),
        MelVmad(),
        MelBounds(),
        MelLString('FULL','full'),
        MelModel(),
        MelString('ICON','iconPath'),
        MelString('MICO','smallIconPath'),
        MelLString('DESC','description'),
        MelDestructible(),
        MelOptFid('YNAM', 'pickupSound'),
        MelOptFid('ZNAM', 'dropSound'),
        MelKeywords(),
        MelUnion({
            False: MelStruct('DATA', '2B2siIf',
                             (_book_type_flags, 'book_flags'), 'book_type',
                             ('unused1', null2), 'book_skill', 'value',
                             'weight'),
            True: MelStruct('DATA', '2B2s2If',
                             (_book_type_flags, 'book_flags'), 'book_type',
                             ('unused1', null2), (FID, 'book_spell'), 'value',
                             'weight'),
        }, decider=PartialLoadDecider(
            loader=MelUInt8('DATA', (_book_type_flags, 'book_flags')),
            decider=FlagDecider('book_flags', 'teaches_spell'),
        )),
        MelFid('INAM','inventoryArt'),
        MelLString('CNAM','text'),
    )
    __slots__ = melSet.getSlotsUsed() + ['modb']

#------------------------------------------------------------------------------
class MreBptd(MelRecord):
    """Body Part Data."""
    classType = 'BPTD'

    _flags = Flags(0L,Flags.getNames('severable','ikData','ikBipedData',
        'explodable','ikIsHead','ikHeadtracking','toHitChanceAbsolute'))

    melSet = MelSet(
        MelString('EDID','eid'),
        MelModel(),
        MelGroups('bodyParts',
            MelString('BPTN', 'partName'),
            MelString('PNAM','poseMatching'),
            MelString('BPNN', 'nodeName'),
            MelString('BPNT','vatsTarget'),
            MelString('BPNI','ikDataStartNode'),
            MelStruct('BPND','f3Bb2BH2I2fi2I7f2I2B2sf','damageMult',
                      (_flags,'flags'),'partType','healthPercent','actorValue',
                      'toHitChance','explodableChancePercent',
                      'explodableDebrisCount',(FID,'explodableDebris',0L),
                      (FID,'explodableExplosion',0L),'trackingMaxAngle',
                      'explodableDebrisScale','severableDebrisCount',
                      (FID,'severableDebris',0L),(FID,'severableExplosion',0L),
                      'severableDebrisScale','goreEffectPosTransX',
                      'goreEffectPosTransY','goreEffectPosTransZ',
                      'goreEffectPosRotX','goreEffectPosRotY','goreEffectPosRotZ',
                      (FID,'severableImpactDataSet',0L),
                      (FID,'explodableImpactDataSet',0L),'severableDecalCount',
                      'explodableDecalCount',('unused',null2),
                      'limbReplacementScale'),
            MelString('NAM1','limbReplacementModel'),
            MelString('NAM4','goreEffectsTargetBone'),
            # Ignore texture hashes - they're only an optimization, plenty of
            # records in Skyrim.esm are missing them
            MelNull('NAM5'),
        ),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreCams(MelRecord):
    """Camera Shot."""
    classType = 'CAMS'

    CamsFlagsFlags = Flags(0L,Flags.getNames(
            (0, 'positionFollowsLocation'),
            (1, 'rotationFollowsTarget'),
            (2, 'dontFollowBone'),
            (3, 'firstPersonCamera'),
            (4, 'noTracer'),
            (5, 'startAtTimeZero'),
        ))

    class MelCamsData(MelStruct):
        """Handle older truncated DATA for CAMS subrecord."""
        def loadData(self, record, ins, sub_type, size_, readId):
            if size_ == 44:
                MelStruct.loadData(self, record, ins, sub_type, size_, readId)
                return
            elif size_ == 40:
                unpacked = ins.unpack('4I6f', size_, readId)
            else:
                raise ModSizeError(record.inName, readId, 44, size_, True)
            unpacked += self.defaults[len(unpacked):]
            setter = record.__setattr__
            for attr,value,action in zip(self.attrs,unpacked,self.actions):
                if callable(action): value = action(value)
                setter(attr,value)
            if self._debug: print unpacked

    melSet = MelSet(
        MelString('EDID','eid'),
        MelModel(),
        MelCamsData('DATA','4I7f','action','location','target',
                  (CamsFlagsFlags,'flags',0L),'timeMultPlayer',
                  'timeMultTarget','timeMultGlobal','maxTime','minTime',
                  'targetPctBetweenActors','nearTargetDistance',),
        MelFid('MNAM','imageSpaceModifier',),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreCell(MelRecord):
    """Cell."""
    classType = 'CELL'

    CellDataFlags1 = Flags(0L,Flags.getNames(
        (0,'isInterior'),
        (1,'hasWater'),
        (2,'cantFastTravel'),
        (3,'noLODWater'),
        (5,'publicPlace'),
        (6,'handChanged'),
        (7,'showSky'),
        ))

    CellDataFlags2 = Flags(0L,Flags.getNames(
        (0,'useSkyLighting'),
        ))

    CellInheritedFlags = Flags(0L,Flags.getNames(
            (0, 'ambientColor'),
            (1, 'directionalColor'),
            (2, 'fogColor'),
            (3, 'fogNear'),
            (4, 'fogFar'),
            (5, 'directionalRotation'),
            (6, 'directionalFade'),
            (7, 'clipDistance'),
            (8, 'fogPower'),
            (9, 'fogMax'),
            (10, 'lightFadeDistances'),
        ))

    # 'Force Hide Land' flags
    CellFHLFlags = Flags(0L,Flags.getNames(
            (0, 'quad1'),
            (1, 'quad2'),
            (2, 'quad3'),
            (3, 'quad4'),
        ))

    class MelCellXcll(MelOptStruct):
        """Handle older truncated XCLL for CELL subrecord."""
        def loadData(self, record, ins, sub_type, size_, readId):
            if size_ == 92:
                MelStruct.loadData(self, record, ins, sub_type, size_, readId)
                return
            elif size_ == 64:
                unpacked = ins.unpack('BBBsBBBsBBBsffiifffBBBsBBBsBBBsBBBsBBBsBBBs', size_, readId)
            elif size_ == 24:
                unpacked = ins.unpack('BBBsBBBsBBBsffi', size_, readId)
            else:
                raise ModSizeError(record.inName, readId, 92, size_, True)
            unpacked += self.defaults[len(unpacked):]
            setter = record.__setattr__
            for attr,value,action in zip(self.attrs,unpacked,self.actions):
                if callable(action): value = action(value)
                setter(attr,value)
            if self._debug: print unpacked, record.flags.getTrueAttrs()

    class MelCellData(MelStruct):
        """Handle older truncated DATA for CELL subrecord."""
        def loadData(self, record, ins, sub_type, size_, readId):
            if size_ == 2:
                MelStruct.loadData(self, record, ins, sub_type, size_, readId)
                return
            elif size_ == 1:
                unpacked = ins.unpack('B', size_, readId)
            else:
                raise ModSizeError(record.inName, readId, 2, size_, True)
            unpacked += self.defaults[len(unpacked):]
            setter = record.__setattr__
            for attr,value,action in zip(self.attrs,unpacked,self.actions):
                if callable(action): value = action(value)
                setter(attr,value)
            if self._debug: print unpacked, record.flags.getTrueAttrs()

    class MelWaterHeight(MelOptFloat):
        """XCLW sometimes has $FF7FFFFF and causes invalid floating point."""
        default_heights = {4294953216.0, -2147483648.0,
            -3.4028234663852886e+38, 3.4028234663852886e+38} # unused, see #302

        def __init__(self):
            MelOptFloat.__init__(self, 'XCLW', ('waterHeight', -2147483649))

        def loadData(self, record, ins, sub_type, size_, readId):
            # from brec.MelStruct#loadData - formatLen is 0 for MelWaterHeight
            waterHeight = ins.unpack(self.format, size_, readId)
            if not record.flags.isInterior: # drop interior cells for Skyrim
                attr,value = self.attrs[0],waterHeight[0]
                # if value in __default_heights:
                #     value = 3.4028234663852886e+38 # normalize values
                record.__setattr__(attr, value)

        def dumpData(self,record,out):
            if not record.flags.isInterior:
                MelOptFloat.dumpData(self, record, out)

    melSet = MelSet(
        MelString('EDID','eid'),
        MelLString('FULL','full'),
        MelCellData('DATA','BB',(CellDataFlags1,'flags',0L),(CellDataFlags2,'skyFlags',0L),),
        MelOptStruct('XCLC','2iI',('posX', 0),('posY', 0),(CellFHLFlags,'fhlFlags',0L),),
        MelCellXcll('XCLL','BBBsBBBsBBBsffiifffBBBsBBBsBBBsBBBsBBBsBBBsBBBsfBBBsfffI',
                 'ambientRed','ambientGreen','ambientBlue',('unused1',null1),
                 'directionalRed','directionalGreen','directionalBlue',('unused2',null1),
                 'fogRed','fogGreen','fogBlue',('unused3',null1),
                 'fogNear','fogFar','directionalXY','directionalZ',
                 'directionalFade','fogClip','fogPower',
                 'redXplus','greenXplus','blueXplus',('unknownXplus',null1),
                 'redXminus','greenXminus','blueXminus',('unknownXminus',null1),
                 'redYplus','greenYplus','blueYplus',('unknownYplus',null1),
                 'redYminus','greenYminus','blueYminus',('unknownYminus',null1),
                 'redZplus','greenZplus','blueZplus',('unknownZplus',null1),
                 'redZminus','greenZminus','blueZminus',('unknownZminus',null1),
                 'redSpec','greenSpec','blueSpec',('unknownSpec',null1),
                 'fresnelPower',
                 'fogColorFarRed','fogColorFarGreen','fogColorFarBlue',('unused4',null1),
                 'fogMax','lightFadeBegin','lightFadeEnd',(CellInheritedFlags,'inherits',0L),
        ),
        MelBase('TVDT','occlusionData'),
        # Decoded in xEdit, but properly reading it is relatively slow - see
        # 'Simple Records' option in xEdit - so we skip that for now
        MelBase('MHDT','maxHeightData'),
        MelFid('LTMP','lightTemplate',),
        # leftover flags, they are now in XCLC
        MelBase('LNAM','unknown_LNAM'),
        MelWaterHeight(),
        MelString('XNAM','waterNoiseTexture'),
        MelFidList('XCLR','regions'),
        MelFid('XLCN','location',),
        MelBase('XWCN','unknown_XWCN'), # leftover
        MelBase('XWCS','unknown_XWCS'), # leftover
        MelOptStruct('XWCU', '3f4s3f', ('xOffset', 0.0), ('yOffset', 0.0),
                     ('zOffset', 0.0), ('unk1XWCU', null4), ('xAngle', 0.0),
                     ('yAngle', 0.0), ('zAngle', 0.0), dumpExtra='unk2XWCU',),
        MelFid('XCWT','water'),
        MelOwnership(),
        MelFid('XILL','lockList',),
        MelString('XWEM','waterEnvironmentMap'),
        MelFid('XCCM','climate',), # xEdit calls this 'Sky/Weather From Region'
        MelFid('XCAS','acousticSpace',),
        MelFid('XEZN','encounterZone',),
        MelFid('XCMO','music',),
        MelFid('XCIM','imageSpace',),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreClas(MelRecord):
    """Class."""
    classType = 'CLAS'

    melSet = MelSet(
        MelString('EDID','eid'),
        MelLString('FULL','full'),
        MelLString('DESC','description'),
        MelString('ICON','iconPath'),
        MelString('MICO','smallIconPath'),
        MelStruct('DATA','4sb19BfI4B','unknown','teaches','maximumtraininglevel',
                  'skillWeightsOneHanded','skillWeightsTwoHanded',
                  'skillWeightsArchery','skillWeightsBlock',
                  'skillWeightsSmithing','skillWeightsHeavyArmor',
                  'skillWeightsLightArmor','skillWeightsPickpocket',
                  'skillWeightsLockpicking','skillWeightsSneak',
                  'skillWeightsAlchemy','skillWeightsSpeech',
                  'skillWeightsAlteration','skillWeightsConjuration',
                  'skillWeightsDestruction','skillWeightsIllusion',
                  'skillWeightsRestoration','skillWeightsEnchanting',
                  'bleedoutDefault','voicePoints',
                  'attributeWeightsHealth','attributeWeightsMagicka',
                  'attributeWeightsStamina','attributeWeightsUnknown',),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreClfm(MelRecord):
    """Color."""
    classType = 'CLFM'
    melSet = MelSet(
        MelString('EDID','eid'),
        MelLString('FULL','full'),
        MelColorO(),
        MelUInt32('FNAM', 'playable'), # actually a bool, stored as uint32
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreClmt(MelRecord):
    """Climate."""
    classType = 'CLMT'
    melSet = MelSet(
        MelString('EDID','eid',),
        MelStructA('WLST','IiI','weatherTypes',(FID,'weather',None),'chance',(FID,'global',None),),
        MelString('FNAM','sunPath',),
        MelString('GNAM','glarePath',),
        MelModel(),
        MelStruct('TNAM','6B','riseBegin','riseEnd','setBegin','setEnd','volatility','phaseLength',),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreCobj(MelRecord):
    """Constructible Object (Recipes)."""
    classType = 'COBJ'
    isKeyedByEid = True # NULL fids are acceptable

    melSet = MelSet(
        MelString('EDID','eid'),
        MelItemsCounter(),
        MelItems(),
        MelConditions(),
        MelFid('CNAM','resultingItem'),
        MelFid('BNAM','craftingStation'),
        MelUInt16('NAM1', 'resultingQuantity'),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreColl(MelRecord):
    """Collision Layer."""
    classType = 'COLL'

    CollisionLayerFlags = Flags(0L,Flags.getNames(
        (0,'triggerVolume'),
        (1,'sensor'),
        (2,'navmeshObstacle'),
    ))

    melSet = MelSet(
        MelString('EDID','eid'),
        MelLString('DESC','description'),
        MelUInt32('BNAM', 'layerID'),
        MelColor('FNAM'),
        MelUInt32('GNAM', (CollisionLayerFlags,'flags',0L),),
        MelString('MNAM','name',),
        MelUInt32('INTV', 'interactablesCount'),
        MelFidList('CNAM','collidesWith',),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreCont(MelRecord):
    """Container."""
    classType = 'CONT'

    ContTypeFlags = Flags(0L,Flags.getNames(
        (0, 'allowSoundsWhenAnimation'),
        (1, 'respawns'),
        (2, 'showOwner'),
    ))

    melSet = MelSet(
        MelString('EDID','eid'),
        MelVmad(),
        MelBounds(),
        MelLString('FULL','full'),
        MelModel(),
        MelItemsCounter(),
        MelItems(),
        MelDestructible(),
        MelStruct('DATA','=Bf',(ContTypeFlags,'flags',0L),'weight'),
        MelFid('SNAM','soundOpen'),
        MelFid('QNAM','soundClose'),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreCpth(MelRecord):
    """Camera Path"""
    classType = 'CPTH'

    melSet = MelSet(
        MelString('EDID','eid'),
        MelConditions(),
        MelFidList('ANAM','relatedCameraPaths',),
        MelUInt8('DATA', 'cameraZoom'),
        MelFids('SNAM','cameraShots',),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreCsty(MelRecord):
    """Combat Style."""
    classType = 'CSTY'

    CstyTypeFlags = Flags(0L,Flags.getNames(
        (0, 'dueling'),
        (1, 'flanking'),
        (2, 'allowDualWielding'),
    ))

    melSet = MelSet(
        MelString('EDID','eid'),
        # esm = Equipment Score Mult
        MelStruct('CSGD','10f','offensiveMult','defensiveMult','groupOffensiveMult',
        'esmMelee','esmMagic','esmRanged','esmShout','esmUnarmed','esmStaff',
        'avoidThreatChance',),
        MelBase('CSMD','unknownValue'),
        MelStruct('CSME','8f','atkStaggeredMult','powerAtkStaggeredMult','powerAtkBlockingMult',
        'bashMult','bashRecoilMult','bashAttackMult','bashPowerAtkMult','specialAtkMult',),
        MelStruct('CSCR','4f','circleMult','fallbackMult','flankDistance','stalkTime',),
        MelFloat('CSLR', 'strafeMult'),
        MelStruct('CSFL','8f','hoverChance','diveBombChance','groundAttackChance','hoverTime',
        'groundAttackTime','perchAttackChance','perchAttackTime','flyingAttackChance',),
        MelUInt32('DATA', (CstyTypeFlags, 'flags', 0L)),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreDebr(MelRecord):
    """Debris."""
    classType = 'DEBR'

    dataFlags = Flags(0L,Flags.getNames('hasCollissionData'))

    class MelDebrData(MelStruct):
        subType = 'DATA'
        _elements = (('percentage',0),('modPath',null1),('flags',0),)

        def __init__(self):
            self.attrs,self.defaults,self.actions,self.formAttrs = MelBase.parseElements(*self._elements)
            self._debug = False

        def loadData(self, record, ins, sub_type, size_, readId):
            """Reads data from ins into record attribute."""
            data = ins.read(size_, readId)
            (record.percentage,) = struct_unpack('B',data[0:1])
            record.modPath = data[1:-2]
            if data[-2] != null1:
                raise ModError(ins.inName,_('Unexpected subrecord: ')+readId)
            (record.flags,) = struct_unpack('B',data[-1])

        def dumpData(self,record,out):
            """Dumps data from record to outstream."""
            data = ''
            data += struct_pack('B',record.percentage)
            data += record.modPath
            data += null1
            data += struct_pack('B',record.flags)
            out.packSub('DATA',data)

    melSet = MelSet(
        MelString('EDID','eid'),
        MelGroups('models',
            MelDebrData(),
            MelBase('MODT','modt_p'),
        ),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreDial(brec.MreDial):
    """Dialogue."""

    DialTopicFlags = Flags(0L,Flags.getNames(
        (0, 'doAllBeforeRepeating'),
    ))

    melSet = MelSet(
        MelString('EDID','eid'),
        MelLString('FULL','full'),
        MelFloat('PNAM', 'priority',),
        MelFid('BNAM','branch',),
        MelFid('QNAM','quest',),
        MelStruct('DATA','2BH',(DialTopicFlags,'flags_dt',0L),'category',
                  'subtype',),
        # SNAM is a 4 byte string no length byte - TODO(inf) MelFixedString?
        MelStruct('SNAM', '4s', 'subtypeName',),
        ##: Check if this works - if not, move back to method
        MelCounter(MelUInt32('TIFC', 'infoCount'), counts='infos'),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreDlbr(MelRecord):
    """Dialog Branch."""
    classType = 'DLBR'

    DialogBranchFlags = Flags(0L,Flags.getNames(
        (0,'topLevel'),
        (1,'blocking'),
        (2,'exclusive'),
    ))

    melSet = MelSet(
        MelString('EDID','eid'),
        MelFid('QNAM','quest',),
        MelUInt32('TNAM', 'unknown'),
        MelUInt32('DNAM', (DialogBranchFlags, 'flags', 0L)),
        MelFid('SNAM','startingTopic',),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreDlvw(MelRecord):
    """Dialog View"""
    classType = 'DLVW'

    melSet = MelSet(
        MelString('EDID','eid'),
        MelFid('QNAM','quest',),
        MelFids('BNAM','branches',),
        MelGroups('unknownTNAM',
            MelBase('TNAM','unknown',),
        ),
        MelBase('ENAM','unknownENAM'),
        MelBase('DNAM','unknownDNAM'),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreDobj(MelRecord):
    """Default Object Manager."""
    classType = 'DOBJ'

    class MelDobjDnam(MelStructA):
        """This DNAM can have < 8 bytes of noise at the end, so store those
        in a variable and dump them out again when writing."""
        def __init__(self):
            MelStructA.__init__(self, 'DNAM', '2I', 'objects', 'objectUse',
                                (FID, 'objectID'))

        def loadData(self, record, ins, sub_type, size_, readId):
            # Load everything but the noise
            start_pos = ins.tell()
            MelStructA.loadData(self, record, ins, sub_type, size_, readId)
            # Now, read the remainder of the subrecord and store it
            read_size = ins.tell() - start_pos
            record.unknownDNAM = ins.read(size_ - read_size)

        def dumpData(self, record, out):
            # We need to fully override this to attach unknownDNAM to the data
            # we'll be writing out
            if record.__getattribute__(self.attr) is not None:
                to_write = ''
                attrs = self.attrs
                format = self.format
                for x in record.objects:
                    to_write += struct_pack(
                        format, *[getattr(x, item) for item in attrs])
                to_write += record.unknownDNAM
                out.packSub(self.subType, to_write)

        def getSlotsUsed(self):
            return MelStructA.getSlotsUsed(self) + ('unknownDNAM',)

    melSet = MelSet(
        MelString('EDID', 'eid'),
        MelDobjDnam(),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreDoor(MelRecord):
    """Door."""
    classType = 'DOOR'

    DoorTypeFlags = Flags(0L,Flags.getNames(
        (1, 'automatic'),
        (2, 'hidden'),
        (3, 'minimalUse'),
        (4, 'slidingDoor'),
        (5, 'doNotOpenInCombatSearch'),
    ))

    melSet = MelSet(
        MelString('EDID','eid'),
        MelVmad(),
        MelBounds(),
        MelLString('FULL','full'),
        MelModel(),
        MelDestructible(),
        MelFid('SNAM','soundOpen'),
        MelFid('ANAM','soundClose'),
        MelFid('BNAM','soundLoop'),
        MelUInt8('FNAM', (DoorTypeFlags, 'flags', 0L)),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreDual(MelRecord):
    """Dual Cast Data."""
    classType = 'DUAL'

    DualCastDataFlags = Flags(0L,Flags.getNames(
        (0,'hitEffectArt'),
        (1,'projectile'),
        (2,'explosion'),
    ))

    melSet = MelSet(
        MelString('EDID','eid'),
        MelBounds(),
        MelStruct('DATA','6I',(FID,'projectile'),(FID,'explosion'),(FID,'effectShader'),
                  (FID,'hitEffectArt'),(FID,'impactDataSet'),(DualCastDataFlags,'flags',0L),),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreEczn(MelRecord):
    """Encounter Zone."""
    classType = 'ECZN'

    EcznTypeFlags = Flags(0L,Flags.getNames(
            (0, 'neverResets'),
            (1, 'matchPCBelowMinimumLevel'),
            (2, 'disableCombatBoundary'),
        ))

    class MelEcznData(MelStruct):
        """Handle older truncated DATA for ECZN subrecord."""
        def loadData(self, record, ins, sub_type, size_, readId):
            if size_ == 12:
                MelStruct.loadData(self, record, ins, sub_type, size_, readId)
                return
            elif size_ == 8:
                unpacked = ins.unpack('II', size_, readId)
            else:
                raise ModSizeError(record.inName, readId, 12, size_, True)
            unpacked += self.defaults[len(unpacked):]
            setter = record.__setattr__
            for attr,value,action in zip(self.attrs,unpacked,self.actions):
                if callable(action): value = action(value)
                setter(attr,value)
            if self._debug: print unpacked

    melSet = MelSet(
        MelString('EDID','eid'),
        MelEcznData('DATA','2I2bBb',(FID,'owner',None),(FID,'location',None),
                    ('rank',0),('minimumLevel',0),(EcznTypeFlags,'flags',0L),
                    ('maxLevel',0)),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreEfsh(MelRecord):
    """Effect Shader."""
    classType = 'EFSH'

    EfshGeneralFlags = Flags(0L,Flags.getNames(
        (0, 'noMembraneShader'),
        (1, 'membraneGrayscaleColor'),
        (2, 'membraneGrayscaleAlpha'),
        (3, 'noParticleShader'),
        (4, 'edgeEffectInverse'),
        (5, 'affectSkinOnly'),
        (6, 'ignoreAlpha'),
        (7, 'projectUVs'),
        (8, 'ignoreBaseGeometryAlpha'),
        (9, 'lighting'),
        (10, 'noWeapons'),
        (11, 'unknown11'),
        (12, 'unknown12'),
        (13, 'unknown13'),
        (14, 'unknown14'),
        (15, 'particleAnimated'),
        (16, 'particleGrayscaleColor'),
        (17, 'particleGrayscaleAlpha'),
        (18, 'unknown18'),
        (19, 'unknown19'),
        (20, 'unknown20'),
        (21, 'unknown21'),
        (22, 'unknown22'),
        (23, 'unknown23'),
        (24, 'useBloodGeometry'),
    ))

    class MelEfshData(MelStruct):
        """Handle older truncated DATA for EFSH subrecord."""
        def loadData(self, record, ins, sub_type, size_, readId):
            if size_ == 400:
                MelStruct.loadData(self, record, ins, sub_type, size_, readId)
                return
            elif size_ == 396:
                unpacked = ins.unpack('4s3I3Bs9f3Bs8f5I19f3Bs3Bs3Bs11fI5f3Bsf2I6fI3Bs3Bs9f8I2f', size_, readId)
            elif size_ == 344:
                unpacked = ins.unpack('4s3I3Bs9f3Bs8f5I19f3Bs3Bs3Bs11fI5f3Bsf2I6fI3Bs3Bs6f', size_, readId)
            elif size_ == 312:
                unpacked = ins.unpack('4s3I3Bs9f3Bs8f5I19f3Bs3Bs3Bs11fI5f3Bsf2I6fI', size_, readId)
            elif size_ == 308:
                unpacked = ins.unpack('4s3I3Bs9f3Bs8f5I19f3Bs3Bs3Bs11fI5f3Bsf2I6f', size_, readId)
            else:
                raise ModSizeError(record.inName, readId, 400, size_, True)
            unpacked += self.defaults[len(unpacked):]
            setter = record.__setattr__
            for attr,value,action in zip(self.attrs,unpacked,self.actions):
                if callable(action): value = action(value)
                setter(attr,value)
            if self._debug: print unpacked

    melSet = MelSet(
        MelString('EDID','eid'),
        MelString('ICON','fillTexture'),
        MelString('ICO2','particleShaderTexture'),
        MelString('NAM7','holesTexture'),
        MelString('NAM8','membranePaletteTexture'),
        MelString('NAM9','particlePaletteTexture'),
        MelEfshData('DATA','4s3I3Bs9f3Bs8f5I19f3Bs3Bs3Bs11fI5f3Bsf2I6fI3Bs3Bs9f8I2fI',
                  'unused1','memSBlend','memBlendOp','memZFunc','fillRed',
                  'fillGreen','fillBlue','unused2','fillAlphaIn','fillFullAlpha',
                  'fillAlphaOut','fillAlphaRatio','fillAlphaAmp','fillAlphaPulse',
                  'fillAnimSpeedU','fillAnimSpeedV','edgeEffectOff','edgeRed',
                  'edgeGreen','edgeBlue','unused3','edgeAlphaIn','edgeFullAlpha',
                  'edgeAlphaOut','edgeAlphaRatio','edgeAlphaAmp','edgeAlphaPulse',
                  'fillFullAlphaRatio','edgeFullAlphaRatio','memDestBlend',
                  'partSourceBlend','partBlendOp','partZTestFunc','partDestBlend',
                  'partBSRampUp','partBSFull','partBSRampDown','partBSRatio',
                  'partBSPartCount','partBSLifetime','partBSLifetimeDelta',
                  'partSSpeedNorm','partSAccNorm','partSVel1','partSVel2',
                  'partSVel3','partSAccel1','partSAccel2','partSAccel3',
                  'partSKey1','partSKey2','partSKey1Time','partSKey2Time',
                  'key1Red','key1Green','key1Blue','unused4','key2Red',
                  'key2Green','key2Blue','unused5','key3Red','key3Green',
                  'key3Blue','unused6','colorKey1Alpha','colorKey2Alpha',
                  'colorKey3Alpha','colorKey1KeyTime','colorKey2KeyTime',
                  'colorKey3KeyTime','partSSpeedNormDelta','partSSpeedRotDeg',
                  'partSSpeedRotDegDelta','partSRotDeg','partSRotDegDelta',
                  (FID,'addonModels'),'holesStart','holesEnd','holesStartVal',
                  'holesEndVal','edgeWidthAlphaUnit','edgeAlphRed',
                  'edgeAlphGreen','edgeAlphBlue','unused7','expWindSpeed',
                  'textCountU','textCountV','addonModelIn','addonModelOut',
                  'addonScaleStart','addonScaleEnd','addonScaleIn','addonScaleOut',
                  (FID,'ambientSound'),'key2FillRed','key2FillGreen',
                  'key2FillBlue','unused8','key3FillRed','key3FillGreen',
                  'key3FillBlue','unused9','key1ScaleFill','key2ScaleFill',
                  'key3ScaleFill','key1FillTime','key2FillTime','key3FillTime',
                  'colorScale','birthPosOffset','birthPosOffsetRange','startFrame',
                  'startFrameVariation','endFrame','loopStartFrame',
                  'loopStartVariation','frameCount','frameCountVariation',
                  (EfshGeneralFlags,'flags',0L),'fillTextScaleU',
                  'fillTextScaleV','sceneGraphDepthLimit',),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreEnch(MelRecord,MreHasEffects):
    """Object Effect."""
    classType = 'ENCH'

    EnchGeneralFlags = Flags(0L,Flags.getNames(
        (0, 'noAutoCalc'),
        (1, 'unknownTwo'),
        (2, 'extendDurationOnRecast'),
    ))

    class MelEnchEnit(MelStruct):
        """Handle older truncated ENIT for ENCH subrecord."""
        def loadData(self, record, ins, sub_type, size_, readId):
            if size_ == 36:
                MelStruct.loadData(self, record, ins, sub_type, size_, readId)
                return
            elif size_ == 32:
                unpacked = ins.unpack('i2Ii2IfI', size_, readId)
            else:
                raise ModSizeError(record.inName, readId, 36, size_, True)
            unpacked += self.defaults[len(unpacked):]
            setter = record.__setattr__
            for attr,value,action in zip(self.attrs,unpacked,self.actions):
                if callable(action): value = action(value)
                setter(attr,value)
            if self._debug: print unpacked

    melSet = MelSet(
        MelString('EDID','eid'),
        MelBounds(),
        MelLString('FULL','full'),
        MelEnchEnit('ENIT','i2Ii2If2I','enchantmentCost',(EnchGeneralFlags,
                  'generalFlags',0L),'castType','enchantmentAmount','targetType',
                  'enchantType','chargeTime',(FID,'baseEnchantment'),
                  (FID,'wornRestrictions'),),
        MelEffects(),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreEqup(MelRecord):
    """Equip Type."""
    classType = 'EQUP'
    melSet = MelSet(
        MelString('EDID','eid'),
        MelFidList('PNAM','canBeEquipped'),
        MelUInt32('DATA', 'useAllParents'), # actually a bool
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreExpl(MelRecord):
    """Explosion."""
    classType = 'EXPL'

    ExplTypeFlags = Flags(0L,Flags.getNames(
        (1, 'alwaysUsesWorldOrientation'),
        (2, 'knockDownAlways'),
        (3, 'knockDownByFormular'),
        (4, 'ignoreLosCheck'),
        (5, 'pushExplosionSourceRefOnly'),
        (6, 'ignoreImageSpaceSwap'),
        (7, 'chain'),
        (8, 'noControllerVibration'),
    ))

    class MelExplData(MelStruct):
        """Handle older truncated DATA for EXPL subrecord."""
        def loadData(self, record, ins, sub_type, size_, readId):
            if size_ == 52:
                MelStruct.loadData(self, record, ins, sub_type, size_, readId)
                return
            elif size_ == 48:
                unpacked = ins.unpack('6I5fI', size_, readId)
            elif size_ == 44:
                unpacked = ins.unpack('6I5f', size_, readId)
            elif size_ == 40:
                unpacked = ins.unpack('6I4f', size_, readId)
            else:
                raise ModSizeError(record.inName, readId, 52, size_, True)
            unpacked += self.defaults[len(unpacked):]
            setter = record.__setattr__
            for attr,value,action in zip(self.attrs,unpacked,self.actions):
                if callable(action): value = action(value)
                setter(attr,value)
            if self._debug: print unpacked, record.flags.getTrueAttrs()

    melSet = MelSet(
        MelString('EDID','eid'),
        MelBounds(),
        MelLString('FULL','full'),
        MelModel(),
        MelFid('EITM','objectEffect'),
        MelFid('MNAM','imageSpaceModifier'),
        MelExplData('DATA','6I5f2I',(FID,'light',None),(FID,'sound1',None),(FID,'sound2',None),
                  (FID,'impactDataset',None),(FID,'placedObject',None),(FID,'spawnProjectile',None),
                  'force','damage','radius','isRadius','verticalOffsetMult',
                  (ExplTypeFlags,'flags',0L),'soundLevel',),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreEyes(MelRecord):
    """Eyes."""
    classType = 'EYES'

    EyesTypeFlags = Flags(0L,Flags.getNames(
            (0, 'playable'),
            (1, 'notMale'),
            (2, 'notFemale'),
        ))

    melSet = MelSet(
        MelString('EDID','eid'),
        MelLString('FULL','full'),
        MelString('ICON','iconPath'),
        MelString('MICO','smallIconPath'),
        MelUInt8('DATA', (EyesTypeFlags, 'flags', 0L)),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreFact(MelRecord):
    """Faction."""
    classType = 'FACT'

    FactGeneralTypeFlags = Flags(0L,Flags.getNames(
        (0, 'hiddenFromPC'),
        (1, 'specialCombat'),
        (2, 'unknown3'),
        (3, 'unknown4'),
        (4, 'unknown5'),
        (5, 'unknown6'),
        (6, 'trackCrime'),
        (7, 'ignoreCrimesMurder'),
        (8, 'ignoreCrimesAssult'),
        (9, 'ignoreCrimesStealing'),
        (10, 'ignoreCrimesTrespass'),
        (11, 'doNotReportCrimesAgainstMembers'),
        (12, 'crimeGold-UseDefaults'),
        (13, 'ignoreCrimesPickpocket'),
        (14, 'allowSell'), # vendor
        (15, 'canBeOwner'),
        (16, 'ignoreCrimesWerewolf'),
    ))

#   wbPLVD := wbStruct(PLVD, 'Location', [
#     wbInteger('Type', itS32, wbLocationEnum),
#     wbUnion('Location Value', wbTypeDecider, [
#       {0} wbFormIDCkNoReach('Reference', [NULL, DOOR, PLYR, ACHR, REFR, PGRE, PHZD, PARW, PBAR, PBEA, PCON, PFLA]),
#       {1} wbFormIDCkNoReach('Cell', [NULL, CELL]),
#       {2} wbByteArray('Near Package Start Location', 4, cpIgnore),
#       {3} wbByteArray('Near Editor Location', 4, cpIgnore),
#       {4} wbFormIDCkNoReach('Object ID', [NULL, ACTI, DOOR, STAT, FURN, SPEL, SCRL, NPC_, CONT, ARMO, AMMO, MISC, WEAP, BOOK, KEYM, ALCH, INGR, LIGH, FACT, FLST, IDLM, SHOU]),
#       {5} wbInteger('Object Type', itU32, wbObjectTypeEnum),
#       {6} wbFormIDCk('Keyword', [NULL, KYWD]),
#       {7} wbByteArray('Unknown', 4, cpIgnore),
#       {8} wbInteger('Alias ID', itU32),
#       {9} wbFormIDCkNoReach('Reference', [NULL, DOOR, PLYR, ACHR, REFR, PGRE, PHZD, PARW, PBAR, PBEA, PCON, PFLA]),
#      {10} wbByteArray('Unknown', 4, cpIgnore),
#      {11} wbByteArray('Unknown', 4, cpIgnore),
#      {12} wbByteArray('Unknown', 4, cpIgnore)
#     ]),
#     wbInteger('Radius', itS32)
#   ]);

    class MelFactCrva(MelStruct):
        """Handle older truncated CRVA for FACT subrecord."""
        def loadData(self, record, ins, sub_type, size_, readId):
            if size_ == 20:
                MelStruct.loadData(self, record, ins, sub_type, size_, readId)
                return
            elif size_ == 16:
                unpacked = ins.unpack('2B5Hf', size_, readId)
            elif size_ == 12:
                unpacked = ins.unpack('2B5H', size_, readId)
            else:
                raise ModSizeError(record.inName, readId, 20, size_, True)
            unpacked += self.defaults[len(unpacked):]
            setter = record.__setattr__
            for attr,value,action in zip(self.attrs,unpacked,self.actions):
                if callable(action): value = action(value)
                setter(attr,value)
            if self._debug: print unpacked

    melSet = MelSet(
        MelString('EDID','eid'),
        MelLString('FULL','full'),
        MelStructs('XNAM','IiI','relations',(FID,'faction'),'mod','combatReaction',),
        MelUInt32('DATA', (FactGeneralTypeFlags, 'flags', 0L)),
        MelFid('JAIL','exteriorJailMarker'),
        MelFid('WAIT','followerWaitMarker'),
        MelFid('STOL','stolenGoodsContainer'),
        MelFid('PLCN','playerInventoryContainer'),
        MelFid('CRGR','sharedCrimeFactionList'),
        MelFid('JOUT','jailOutfit'),
        # 'arrest' and 'attackOnSight' are actually bools
        MelFactCrva('CRVA','2B5Hf2H','arrest','attackOnSight','murder','assult',
        'trespass','pickpocket','unknown','stealMultiplier','escape','werewolf'),
        MelGroups('ranks',
            MelUInt32('RNAM', 'rank'),
            MelLString('MNAM','maleTitle'),
            MelLString('FNAM','femaleTitle'),
            MelString('INAM','insigniaPath'),
        ),
        MelFid('VEND','vendorBuySellList'),
        MelFid('VENC','merchantContainer'),
        MelStruct('VENV','3H2s2B2s','startHour','endHour','radius','unknownOne',
                  'onlyBuysStolenItems','notSellBuy','UnknownTwo'),
        MelOptStruct('PLVD','iIi','type',(FID,'locationValue'),'radius',),
        MelConditionCounter(),
        MelConditions(),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreFlor(MelRecord):
    """Flora."""
    classType = 'FLOR'

    melSet = MelSet(
        MelString('EDID','eid'),
        MelVmad(),
        MelBounds(),
        MelLString('FULL','full'),
        MelModel(),
        MelDestructible(),
        MelKeywords(),
        MelBase('PNAM','unknown01'),
        MelLString('RNAM','activateTextOverride'),
        MelBase('FNAM','unknown02'),
        MelFid('PFIG','ingredient'),
        MelFid('SNAM','harvestSound'),
        MelStruct('PFPC','4B','spring','summer','fall','winter',),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreFlst(MelRecord):
    """FormID List."""
    classType = 'FLST'

    melSet = MelSet(
        MelString('EDID','eid'),
        MelFids('LNAM','formIDInList'),
    )
    __slots__ = melSet.getSlotsUsed() + ['mergeOverLast', 'mergeSources',
                                         'items', 'deflsts', 'canListMerge']

    """ Skyrim's FLST can't always be merged if a mod depends on the order of
    the LNAM records for the Papyrus scripts.

    Solution: Create a Bash tag that indicates when a list cannot be merged.
    If even one mod has this tag then the list is not merged into the
    Bash Patch."""

    # The same with Relev, Delev the 'NoFlstMerge' tag applies to the entire mod
    # even if only one FLST requires it.  When parsing the FLSTs from other mods
    # Wrye Bash should skip any FLST from a mod with the 'NoFlstMerge' tag.
    # Example, ModA has 10 FLST, MODB has 11 FLST.  Ten of the lists are the same
    # Between the two mods.  Since only one list is different, only one FLST is
    # different then only one FLST would be mergable.

    # New Bash Tag 'NoFlstMerge'
    def __init__(self, header, ins=None, do_unpack=False):
        MelRecord.__init__(self, header, ins, do_unpack)
        self.mergeOverLast = False #--Merge overrides last mod merged
        self.mergeSources = None #--Set to list by other functions
        self.items  = None #--Set of items included in list
        #--Set of items deleted by list (Deflst mods) unused for Skyrim
        self.deflsts = None

    def mergeFilter(self,modSet):
        """Filter out items that don't come from specified modSet."""
        if not self.longFids: raise StateError(_("Fids not in long format"))
        self.formIDInList = [fid for fid in self.formIDInList if fid[0] in modSet]

    def mergeWith(self,other,otherMod):
        """Merges newLevl settings and entries with self.
        Requires that: self.items, other.deflsts be defined."""
        if not self.longFids: raise StateError(_("Fids not in long format"))
        if not other.longFids: raise StateError(_("Fids not in long format"))
        #--Remove items based on other.removes
        if other.deflsts:
            removeItems = self.items & other.deflsts
            self.formIDInList = [fid for fid in self.formIDInList if fid not in removeItems]
            self.items = (self.items | other.deflsts)
        #--Add new items from other
        newItems = set()
        formIDInListAppend = self.formIDInList.append
        newItemsAdd = newItems.add
        for fid in other.formIDInList:
            if fid not in self.items:
                formIDInListAppend(fid)
                newItemsAdd(fid)
        if newItems:
            self.items |= newItems
        #--Is merged list different from other? (And thus written to patch.)
        if len(self.formIDInList) != len(other.formIDInList):
            self.mergeOverLast = True
        else:
            for selfEntry,otherEntry in zip(self.formIDInList,other.formIDInList):
                if selfEntry != otherEntry:
                    self.mergeOverLast = True
                    break
            else:
                self.mergeOverLast = False
        if self.mergeOverLast:
            self.mergeSources.append(otherMod)
        else:
            self.mergeSources = [otherMod]
        self.setChanged()

#------------------------------------------------------------------------------
class MreFstp(MelRecord):
    """Footstep."""
    classType = 'FSTP'

    melSet = MelSet(
        MelString('EDID','eid'),
        MelFid('DATA','impactSet'),
        MelString('ANAM','tag'),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreFsts(MelRecord):
    """Footstep Set."""
    classType = 'FSTS'

    melSet = MelSet(
        MelString('EDID','eid'),
        MelStruct('XCNT','5I','walkForward','runForward','walkForwardAlt',
                  'runForwardAlt','walkForwardAlternate2',),
        MelFidList('DATA','footstepSets'),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreFurn(MelRecord):
    """Furniture."""
    classType = 'FURN'

    FurnGeneralFlags = Flags(0L,Flags.getNames(
        (1, 'ignoredBySandbox'),
    ))

    FurnActiveMarkerFlags = Flags(0L,Flags.getNames(
        (0, 'sit0'),
        (1, 'sit1'),
        (2, 'sit2'),
        (3, 'sit3'),
        (4, 'sit4'),
        (5, 'sit5'),
        (6, 'sit6'),
        (7, 'sit7'),
        (8, 'sit8'),
        (9, 'sit9'),
        (10, 'sit10'),
        (11, 'sit11'),
        (12, 'sit12'),
        (13, 'sit13'),
        (14, 'sit14'),
        (15, 'sit15'),
        (16, 'sit16'),
        (17, 'sit17'),
        (18, 'sit18'),
        (19, 'sit19'),
        (20, 'sit20'),
        (21, 'Sit21'),
        (22, 'Sit22'),
        (23, 'sit23'),
        (24, 'unknown25'),
        (25, 'disablesActivation'),
        (26, 'isPerch'),
        (27, 'mustExittoTalk'),
        (28, 'unknown29'),
        (29, 'unknown30'),
        (30, 'unknown31'),
        (31, 'unknown32'),
    ))

    MarkerEntryPointFlags = Flags(0L,Flags.getNames(
            (0, 'front'),
            (1, 'behind'),
            (2, 'right'),
            (3, 'left'),
            (4, 'up'),
        ))

    melSet = MelSet(
        MelString('EDID','eid'),
        MelVmad(),
        MelBounds(),
        MelLString('FULL','full'),
        MelModel(),
        MelDestructible(),
        MelKeywords(),
        MelBase('PNAM','pnam_p'),
        MelUInt16('FNAM', (FurnGeneralFlags, 'general_f', None)),
        MelFid('KNAM','interactionKeyword'),
        MelUInt32('MNAM', (FurnActiveMarkerFlags, 'activeMarkers', None)),
        MelStruct('WBDT','Bb','benchType','usesSkill',),
        MelFid('NAM1','associatedSpell'),
        MelGroups('markers',
            MelUInt32('ENAM', 'markerIndex',),
            MelStruct('NAM0','2sH','unknown',(MarkerEntryPointFlags,'disabledPoints_f',None),),
            MelFid('FNMK','markerKeyword',),
        ),
        MelStructs('FNPR','2H','entryPoints','markerType',(MarkerEntryPointFlags,'entryPointsFlags',None),),
        MelString('XMRK','modelFilename'),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
# Marker for organization please don't remove ---------------------------------
# GLOB ------------------------------------------------------------------------
# Defined in brec.py as class MreGlob(MelRecord) ------------------------------
#------------------------------------------------------------------------------
class MreGmst(MreGmstBase):
    """Game Setting."""
    isKeyedByEid = True # NULL fids are acceptable.

#------------------------------------------------------------------------------
class MreGras(MelRecord):
    """Grass."""
    classType = 'GRAS'

    GrasTypeFlags = Flags(0L,Flags.getNames(
            (0, 'vertexLighting'),
            (1, 'uniformScaling'),
            (2, 'fitToSlope'),
        ))

    melSet = MelSet(
        MelString('EDID','eid'),
        MelBounds(),
        MelModel(),
        MelStruct('DATA','3BsH2sI4fB3s','density','minSlope','maxSlope',
                  ('unkGras1', null1),'unitsFromWater',('unkGras2', null2),
                  'unitsFromWaterType','positionRange','heightRange',
                  'colorRange','wavePeriod',(GrasTypeFlags,'flags',0L),
                  ('unkGras3', null3),),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreHazd(MelRecord):
    """Hazard."""
    classType = 'HAZD'

    HazdTypeFlags = Flags(0L,Flags.getNames(
        (0, 'affectsPlayerOnly'),
        (1, 'inheritDurationFromSpawnSpell'),
        (2, 'alignToImpactNormal'),
        (3, 'inheritRadiusFromSpawnSpell'),
        (4, 'dropToGround'),
    ))

    melSet = MelSet(
        MelString('EDID','eid'),
        MelBounds(),
        MelLString('FULL','full'),
        MelModel(),
        MelFid('MNAM','imageSpaceModifier'),
        MelStruct('DATA','I4f5I','limit','radius','lifetime',
                  'imageSpaceRadius','targetInterval',(HazdTypeFlags,'flags',0L),
                  (FID,'spell'),(FID,'light'),(FID,'impactDataSet'),(FID,'sound'),),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreHdpt(MelRecord):
    """Head Part."""
    classType = 'HDPT'

    HdptTypeFlags = Flags(0L,Flags.getNames(
        (0, 'playable'),
        (1, 'male'),
        (2, 'female'),
        (3, 'isExtraPart'),
        (4, 'useSolidTint'),
    ))

    melSet = MelSet(
        MelString('EDID','eid'),
        MelLString('FULL','full'),
        MelModel(),
        MelUInt8('DATA', (HdptTypeFlags, 'flags', 0L)),
        MelUInt32('PNAM', 'hdptTypes'),
        MelFids('HNAM','extraParts'),
        MelGroups('partsData',
            MelUInt32('NAM0', 'headPartType',),
            MelString('NAM1','filename'),
        ),
        MelFid('TNAM','textureSet'),
        MelFid('CNAM','color'),
        MelFid('RNAM','validRaces'),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreIdle(MelRecord):
    """Idle Animation."""
    classType = 'IDLE'

    IdleTypeFlags = Flags(0L,Flags.getNames(
            (0, 'parent'),
            (1, 'sequence'),
            (2, 'noAttacking'),
            (3, 'blocking'),
        ))

    melSet = MelSet(
        MelString('EDID','eid'),
        MelConditions(),
        MelString('DNAM','filename'),
        MelString('ENAM','animationEvent'),
        MelGroups('idleAnimations',
            MelStruct('ANAM','II',(FID,'parent'),(FID,'prevId'),),
        ),
        MelStruct('DATA','4BH','loopMin','loopMax',(IdleTypeFlags,'flags',0L),
                  'animationGroupSection','replayDelay',),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreIdlm(MelRecord):
    """Idle Marker."""
    classType = 'IDLM'

    IdlmTypeFlags = Flags(0L,Flags.getNames(
        (0, 'runInSequence'),
        (1, 'unknown1'),
        (2, 'doOnce'),
        (3, 'unknown3'),
        (4, 'ignoredBySandbox'),
    ))

    melSet = MelSet(
        MelString('EDID','eid'),
        MelBounds(),
        MelUInt8('IDLF', (IdlmTypeFlags, 'flags', 0L)),
        MelCounter(MelUInt8('IDLC', 'animation_count'), counts='animations'),
        MelFloat('IDLT', 'idleTimerSetting'),
        MelFidList('IDLA','animations'),
        MelModel(),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreInfo(MelRecord):
    """Dialog Response."""
    classType = 'INFO'

    _InfoResponsesFlags = Flags(0L, Flags.getNames(
            (0, 'useEmotionAnimation'),
        ))

    _EnamResponseFlags = Flags(0L, Flags.getNames(
            (0, 'goodbye'),
            (1, 'random'),
            (2, 'sayonce'),
            (3, 'unknown4'),
            (4, 'unknown5'),
            (5, 'randomend'),
            (6, 'invisiblecontinue'),
            (7, 'walkAway'),
            (8, 'walkAwayInvisibleinMenu'),
            (9, 'forcesubtitle'),
            (10, 'canmovewhilegreeting'),
            (11, 'noLIPFile'),
            (12, 'requirespostprocessing'),
            (13, 'audioOutputOverride'),
            (14, 'spendsfavorpoints'),
            (15, 'unknown16'),
        ))

    melSet = MelSet(
        MelString('EDID','eid'),
        MelVmad(),
        MelBase('DATA','unknownDATA'),
        MelStruct('ENAM','2H', (_EnamResponseFlags, 'flags', 0L),
                  'resetHours',),
        MelFid('TPIC','topic',),
        MelFid('PNAM','prevInfo',),
        MelUInt8('CNAM', 'favorLevel'),
        MelFids('TCLT','linkTo',),
        MelFid('DNAM','responseData',),
        MelGroups('responses',
            MelStruct('TRDT', '2I4sB3sIB3s', 'emotionType', 'emotionValue',
                      ('unused1', null4), 'responseNumber', ('unused2', null3),
                      (FID, 'sound', None),
                      (_InfoResponsesFlags, 'responseFlags', 0L),
                      ('unused3', null3),),
            MelLString('NAM1','responseText'),
            MelString('NAM2','scriptNotes'),
            MelString('NAM3','edits'),
            MelFid('SNAM','idleAnimationsSpeaker',),
            MelFid('LNAM','idleAnimationsListener',),
        ),
        MelConditions(),
        MelGroups('leftOver',
            MelBase('SCHR','unknown1'),
            MelFid('QNAM','unknown2'),
            MelNull('NEXT'),
        ),
        MelLString('RNAM','prompt'),
        MelFid('ANAM','speaker',),
        MelFid('TWAT','walkAwayTopic',),
        MelFid('ONAM','audioOutputOverride',),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreImad(MelRecord):
    """Image Space Adapter."""
    classType = 'IMAD'

    _ImadDofFlags = Flags(0L, Flags.getNames(
        (0, 'useTarget'),
        (1, 'unknown2'),
        (2, 'unknown3'),
        (3, 'unknown4'),
        (4, 'unknown5'),
        (5, 'unknown6'),
        (6, 'unknown7'),
        (7, 'unknown8'),
        (8, 'modeFront'),
        (9, 'modeBack'),
        (10, 'noSky'),
        (11, 'blurRadiusBit2'),
        (12, 'blurRadiusBit1'),
        (13, 'blurRadiusBit0'),
    ))
    _ImadAnimatableFlags = Flags(0L, Flags.getNames(
        (0, 'animatable'),
    ))
    _ImadRadialBlurFlags = Flags(0L, Flags.getNames(
        (0, 'useTarget')
    ))

    melSet = MelSet(
        MelString('EDID', 'eid'),
        MelStruct('DNAM', 'If49I2f8I', (_ImadAnimatableFlags, 'aniFlags', 0L),
                  'duration', 'eyeAdaptSpeedMult', 'eyeAdaptSpeedAdd',
                  'bloomBlurRadiusMult', 'bloomBlurRadiusAdd',
                  'bloomThresholdMult', 'bloomThresholdAdd', 'bloomScaleMult',
                  'bloomScaleAdd', 'targetLumMinMult', 'targetLumMinAdd',
                  'targetLumMaxMult', 'targetLumMaxAdd', 'sunlightScaleMult',
                  'sunlightScaleAdd', 'skyScaleMult', 'skyScaleAdd',
                  'unknown08Mult', 'unknown48Add', 'unknown09Mult',
                  'unknown49Add', 'unknown0AMult', 'unknown4AAdd',
                  'unknown0BMult', 'unknown4BAdd', 'unknown0CMult',
                  'unknown4CAdd', 'unknown0DMult', 'unknown4DAdd',
                  'unknown0EMult', 'unknown4EAdd', 'unknown0FMult',
                  'unknown4FAdd', 'unknown10Mult', 'unknown50Add',
                  'saturationMult', 'saturationAdd', 'brightnessMult',
                  'brightnessAdd', 'contrastMult', 'contrastAdd',
                  'unknown14Mult', 'unknown54Add',
                  'tintColor', 'blurRadius', 'doubleVisionStrength',
                  'radialBlurStrength', 'radialBlurRampUp', 'radialBlurStart',
                  (_ImadRadialBlurFlags, 'radialBlurFlags', 0L),
                  'radialBlurCenterX', 'radialBlurCenterY', 'dofStrength',
                  'dofDistance', 'dofRange', (_ImadDofFlags, 'dofFlags', 0L),
                  'radialBlurRampDown', 'radialBlurDownStart', 'fadeColor',
                  'motionBlurStrength'),
        MelValueInterpolator('BNAM', 'blurRadiusInterp'),
        MelValueInterpolator('VNAM', 'doubleVisionStrengthInterp'),
        MelColorInterpolator('TNAM', 'tintColorInterp'),
        MelColorInterpolator('NAM3', 'fadeColorInterp'),
        MelValueInterpolator('RNAM', 'radialBlurStrengthInterp'),
        MelValueInterpolator('SNAM', 'radialBlurRampUpInterp'),
        MelValueInterpolator('UNAM', 'radialBlurStartInterp'),
        MelValueInterpolator('NAM1', 'radialBlurRampDownInterp'),
        MelValueInterpolator('NAM2', 'radialBlurDownStartInterp'),
        MelValueInterpolator('WNAM', 'dofStrengthInterp'),
        MelValueInterpolator('XNAM', 'dofDistanceInterp'),
        MelValueInterpolator('YNAM', 'dofRangeInterp'),
        MelValueInterpolator('NAM4', 'motionBlurStrengthInterp'),
        MelValueInterpolator('\x00IAD', 'eyeAdaptSpeedMultInterp'),
        MelValueInterpolator('\x40IAD', 'eyeAdaptSpeedAddInterp'),
        MelValueInterpolator('\x01IAD', 'bloomBlurRadiusMultInterp'),
        MelValueInterpolator('\x41IAD', 'bloomBlurRadiusAddInterp'),
        MelValueInterpolator('\x02IAD', 'bloomThresholdMultInterp'),
        MelValueInterpolator('\x42IAD', 'bloomThresholdAddInterp'),
        MelValueInterpolator('\x03IAD', 'bloomScaleMultInterp'),
        MelValueInterpolator('\x43IAD', 'bloomScaleAddInterp'),
        MelValueInterpolator('\x04IAD', 'targetLumMinMultInterp'),
        MelValueInterpolator('\x44IAD', 'targetLumMinAddInterp'),
        MelValueInterpolator('\x05IAD', 'targetLumMaxMultInterp'),
        MelValueInterpolator('\x45IAD', 'targetLumMaxAddInterp'),
        MelValueInterpolator('\x06IAD', 'sunlightScaleMultInterp'),
        MelValueInterpolator('\x46IAD', 'sunlightScaleAddInterp'),
        MelValueInterpolator('\x07IAD', 'skyScaleMultInterp'),
        MelValueInterpolator('\x47IAD', 'skyScaleAddInterp'),
        MelBase('\x08IAD', 'unknown08IAD'),
        MelBase('\x48IAD', 'unknown48IAD'),
        MelBase('\x09IAD', 'unknown09IAD'),
        MelBase('\x49IAD', 'unknown49IAD'),
        MelBase('\x0AIAD', 'unknown0aIAD'),
        MelBase('\x4AIAD', 'unknown4aIAD'),
        MelBase('\x0BIAD', 'unknown0bIAD'),
        MelBase('\x4BIAD', 'unknown4bIAD'),
        MelBase('\x0CIAD', 'unknown0cIAD'),
        MelBase('\x4CIAD', 'unknown4cIAD'),
        MelBase('\x0DIAD', 'unknown0dIAD'),
        MelBase('\x4DIAD', 'unknown4dIAD'),
        MelBase('\x0EIAD', 'unknown0eIAD'),
        MelBase('\x4EIAD', 'unknown4eIAD'),
        MelBase('\x0FIAD', 'unknown0fIAD'),
        MelBase('\x4FIAD', 'unknown4fIAD'),
        MelBase('\x10IAD', 'unknown10IAD'),
        MelBase('\x50IAD', 'unknown50IAD'),
        MelValueInterpolator('\x11IAD', 'saturationMultInterp'),
        MelValueInterpolator('\x51IAD', 'saturationAddInterp'),
        MelValueInterpolator('\x12IAD', 'brightnessMultInterp'),
        MelValueInterpolator('\x52IAD', 'brightnessAddInterp'),
        MelValueInterpolator('\x13IAD', 'contrastMultInterp'),
        MelValueInterpolator('\x53IAD', 'contrastAddInterp'),
        MelBase('\x14IAD', 'unknown14IAD'),
        MelBase('\x54IAD', 'unknown54IAD'),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreImgs(MelRecord):
    """Image Space."""
    classType = 'IMGS'

    melSet = MelSet(
        MelString('EDID','eid'),
        MelBase('ENAM','eman_p'),
        MelStruct('HNAM','9f','eyeAdaptSpeed','bloomBlurRadius','bloomThreshold','bloomScale',
                  'receiveBloomThreshold','white','sunlightScale','skyScale',
                  'eyeAdaptStrength',),
        MelStruct('CNAM','3f','Saturation','Brightness','Contrast',),
        MelStruct('TNAM','4f','tintAmount','tintRed','tintGreen','tintBlue',),
        MelStruct('DNAM','3f2sH','dofStrength','dofDistance','dofRange','unknown',
                  'skyBlurRadius',),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreIngr(MelRecord,MreHasEffects):
    """Ingredient."""
    classType = 'INGR'

    IngrTypeFlags = Flags(0L, Flags.getNames(
        (0, 'no_auto_calc'),
        (1, 'food_item'),
        (8, 'references_persist'),
    ))

    melSet = MelSet(
        MelString('EDID','eid'),
        MelVmad(),
        MelBounds(),
        MelLString('FULL','full'),
        MelKeywords(),
        MelModel(),
        MelString('ICON','iconPath'),
        MelString('MICO','smallIconPath'),
        MelFid('ETYP','equipmentType',),
        MelFid('YNAM','pickupSound'),
        MelFid('ZNAM','dropSound'),
        MelStruct('DATA','if','value','weight'),
        MelStruct('ENIT','iI','ingrValue',(IngrTypeFlags,'flags',0L),),
        MelEffects(),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreIpct(MelRecord):
    """Impact."""
    classType = 'IPCT'

    class MelIpctData(MelStruct):
        """Handles truncated IPCD/DATA subrecords."""
        _IpctTypeFlags = Flags(0L,Flags.getNames(
            (0, 'noDecalData'),
        ))

        def __init__(self):
            MelStruct.__init__(
                self, 'DATA', 'fI2fI2B2s', 'effectDuration',
                'effectOrientation', 'angleThreshold', 'placementRadius',
                'soundLevel',
                (self._IpctTypeFlags, 'ipctFlags', 0L), 'impactResult',
                ('unkIpct1', null1)),

        def loadData(self, record, ins, sub_type, size_, readId):
            """Handle older truncated DATA for IPCT subrecord."""
            if size_ == 24:
                MelStruct.loadData(self, record, ins, sub_type, size_, readId)
                return
            elif size_ == 16:
                unpacked = ins.unpack('=fI2f', size_, readId) #  + (0,0,0,0,)
            else:
                raise ModSizeError(record.inName, readId, 24, size_, True)
            unpacked += self.defaults[len(unpacked):]
            setter = record.__setattr__
            for attr,value,action in zip(self.attrs,unpacked,self.actions):
                if callable(action): value = action(value)
                setter(attr,value)
            if self._debug:
                print u' ',zip(self.attrs,unpacked)
                if len(unpacked) != len(self.attrs):
                    print u' ',unpacked

    melSet = MelSet(
        MelString('EDID','eid'),
        MelModel(),
        MelIpctData(),
        MelDecalData(),
        MelFid('DNAM','textureSet'),
        MelFid('ENAM','secondarytextureSet'),
        MelFid('SNAM','sound1'),
        MelFid('NAM1','sound2'),
        MelFid('NAM2','hazard'),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreIpds(MelRecord):
    """Impact Dataset."""
    classType = 'IPDS'

    melSet = MelSet(
        MelString('EDID','eid'),
        MelStructs('PNAM','2I','impactData',(FID,'material'),(FID,'impact'),),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreKeym(MelRecord):
    """Key."""
    classType = 'KEYM'

    melSet = MelSet(
        MelString('EDID','eid'),
        MelVmad(),
        MelBounds(),
        MelLString('FULL','full'),
        MelModel(),
        MelString('ICON','iconPath'),
        MelString('MICO','smallIconPath'),
        MelDestructible(),
        MelFid('YNAM','pickupSound'),
        MelFid('ZNAM','dropSound'),
        MelKeywords(),
        MelStruct('DATA','if','value','weight'),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreKywd(MelRecord):
    """Keyword record."""
    classType = 'KYWD'

    melSet = MelSet(
        MelString('EDID','eid'),
        MelColorO(),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreLcrt(MelRecord):
    """Location Reference Type."""
    classType = 'LCRT'

    melSet = MelSet(
        MelString('EDID','eid'),
        MelColorO(),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreLctn(MelRecord):
    """Location"""
    classType = 'LCTN'

    melSet = MelSet(
        MelString('EDID','eid'),
        MelStructA('ACPR','2I2h','actorCellPersistentReference',
                   (FID,'actor'),(FID,'location'),'gridX','gridY',),
        MelStructA('LCPR','2I2h','locationCellPersistentReference',
                     (FID,'actor'),(FID,'location'),'gridX','gridY',),
        MelFidList('RCPR','referenceCellPersistentReference',),
        MelStructA('ACUN','3I','actorCellUnique',
                     (FID,'actor'),(FID,'eef'),(FID,'location'),),
        MelStructA('LCUN','3I','locationCellUnique',
                     (FID,'actor'),(FID,'ref'),(FID,'location'),),
        MelFidList('RCUN','referenceCellUnique',),
        MelStructA('ACSR','3I2h','actorCellStaticReference',
                     (FID,'locRefType'),(FID,'marker'),(FID,'location'),
                     'gridX','gridY',),
        MelStructA('LCSR','3I2h','locationCellStaticReference',
                     (FID,'locRefType'),(FID,'marker'),(FID,'location'),
                     'gridX','gridY',),
        MelFidList('RCSR','referenceCellStaticReference',),
        MelStructs('ACEC','I','actorCellEncounterCell',
                  (FID,'actor'), dumpExtra='gridsXYAcec',),
        MelStructs('LCEC','I','locationCellEncounterCell',
                  (FID,'actor'), dumpExtra='gridsXYLcec',),
        MelStructs('RCEC','I','referenceCellEncounterCell',
                  (FID,'actor'), dumpExtra='gridsXYRcec',),
        MelFidList('ACID','actorCellMarkerReference',),
        MelFidList('LCID','locationCellMarkerReference',),
        MelStructA('ACEP','2I2h','actorCellEnablePoint',
                     (FID,'actor'),(FID,'ref'),'gridX','gridY',),
        MelStructA('LCEP','2I2h','locationCellEnablePoint',
                     (FID,'actor'),(FID,'ref'),'gridX','gridY',),
        MelLString('FULL','full'),
        MelKeywords(),
        MelFid('PNAM','parentLocation',),
        MelFid('NAM1','music',),
        MelFid('FNAM','unreportedCrimeFaction',),
        MelFid('MNAM','worldLocationMarkerRef',),
        MelFloat('RNAM', 'worldLocationRadius'),
        MelFid('NAM0','horseMarkerRef',),
        MelColorO(),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreLgtm(MelRecord):
    """Lighting Template."""
    classType = 'LGTM'

    class MelLgtmDalc(MelStruct):
        """Handle older truncated DALC subrecord for LGTM."""
        def loadData(self, record, ins, sub_type, size_, readId):
            if size_ == 32:
                MelStruct.loadData(self, record, ins, sub_type, size_, readId)
                return
            elif size_ == 24:
                unpacked = ins.unpack('=4B4B4B4B4B4B', size_, readId)
            else:
                raise ModSizeError(record.inName, readId, 32, size_, True)
            unpacked += self.defaults[len(unpacked):]
            setter = record.__setattr__
            for attr,value,action in zip(self.attrs,unpacked,self.actions):
                if callable(action): value = action(value)
                setter(attr,value)
            if self._debug: print unpacked

    class MelLgtmData(MelStruct):
        """Handle older truncated DATA subrecord for LGTM."""
        def loadData(self, record, ins, sub_type, size_, readId):
            if size_ == 92:
                MelStruct.loadData(self, record, ins, sub_type, size_, readId)
                return
            elif size_ == 84:
                # Pad it with 8 null bytes in the middle
                unpacked = ins.unpack('3Bs3Bs3Bs2f2i3f24s', 64, readId)
                unpacked += null4 + null4
                unpacked += ins.unpack('3Bs3f4s', 20, readId)
            else:
                raise ModSizeError(record.inName, readId, 92, size_, True)
            setter = record.__setattr__
            for attr, value, action in zip(self.attrs, unpacked, self.actions):
                if callable(action):
                    value = action(value)
                setter(attr, value)
            if self._debug: print unpacked

    melSet = MelSet(
        MelString('EDID','eid'),
        MelLgtmData('DATA','3Bs3Bs3Bs2f2i3f32s3Bs3f4s',
            'redLigh','greenLigh','blueLigh','unknownLigh',
            'redDirect','greenDirect','blueDirect','unknownDirect',
            'redFog','greenFog','blueFog','unknownFog',
            'fogNear','fogFar','dirRotXY','dirRotZ',
            'directionalFade','fogClipDist','fogPower',
            ('ambientColors',null4+null4+null4+null4+null4+null4+null4+null4),
            'redFogFar','greenFogFar','blueFogFar','unknownFogFar',
            'fogMax','lightFaceStart','lightFadeEnd',
            ('unknownData2',null4),),
        MelLgtmDalc('DALC','=4B4B4B4B4B4B4Bf',
            'redXplus','greenXplus','blueXplus','unknownXplus',
            'redXminus','greenXminus','blueXminus','unknownXminus',
            'redYplus','greenYplus','blueYplus','unknownYplus',
            'redYminus','greenYminus','blueYminus','unknownYminus',
            'redZplus','greenZplus','blueZplus','unknownZplus',
            'redZminus','greenZminus','blueZminus','unknownZminus',
            'redSpec','greenSpec','blueSpec','unknownSpec',
            'fresnelPower',),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreLigh(MelRecord):
    """Light."""
    classType = 'LIGH'

    LighTypeFlags = Flags(0L,Flags.getNames(
            (0, 'dynamic'),
            (1, 'canbeCarried'),
            (2, 'negative'),
            (3, 'flicker'),
            (4, 'unknown'),
            (5, 'offByDefault'),
            (6, 'flickerSlow'),
            (7, 'pulse'),
            (8, 'pulseSlow'),
            (9, 'spotLight'),
            (10, 'shadowSpotlight'),
            (11, 'shadowHemisphere'),
            (12, 'shadowOmnidirectional'),
            (13, 'portalstrict'),
        ))

    melSet = MelSet(
        MelString('EDID','eid'),
        MelVmad(),
        MelBounds(),
        MelModel(),
        MelDestructible(),
        MelLString('FULL','full'),
        MelString('ICON','iconPath'),
        MelString('MICO','smallIconPath'),
        # fe = 'Flicker Effect'
        MelStruct('DATA','iI4BI6fIf','duration','radius','red','green','blue',
                  'unknown',(LighTypeFlags,'flags',0L),'falloffExponent','fov',
                  'nearClip','fePeriod','feIntensityAmplitude',
                  'feMovementAmplitude','value','weight',),
        MelFloat('FNAM', 'fade'),
        MelFid('SNAM','sound'),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreLscr(MelRecord):
    """Load Screen."""
    classType = 'LSCR'

    melSet = MelSet(
        MelString('EDID','eid'),
        MelString('ICON','iconPath'),
        MelString('MICO','smallIconPath'),
        MelLString('DESC','description'),
        MelConditions(),
        MelFid('NNAM','loadingScreenNIF'),
        MelFloat('SNAM', 'initialScale'),
        MelStruct('RNAM','3h','rotGridY','rotGridX','rotGridZ',),
        MelStruct('ONAM','2h','rotOffsetMin','rotOffsetMax',),
        MelStruct('XNAM','3f','transGridY','transGridX','transGridZ',),
        MelString('MOD2','cameraPath'),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreLtex(MelRecord):
    """Landscape Texture."""
    classType = 'LTEX'

    melSet = MelSet(
        MelString('EDID','eid'),
        MelFid('TNAM','textureSet',),
        MelFid('MNAM','materialType',),
        MelStruct('HNAM','BB','friction','restitution',),
        MelUInt8('SNAM', 'textureSpecularExponent'),
        MelFids('GNAM','grasses'),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreLeveledList(MreLeveledListBase):
    """Skyrim Leveled item/creature/spell list. Defines some common
    subrecords."""
    __slots__ = []

    class MelLlct(MelCounter):
        def __init__(self):
            MelCounter.__init__(
                self, MelUInt8('LLCT', 'entry_count'), counts='entries')

    class MelLvlo(MelGroups):
        def __init__(self):
            MelGroups.__init__(self,'entries',
                MelStruct('LVLO','=HHIHH','level',('unknown1',null2),
                          (FID,'listId',None),('count',1),('unknown2',null2)),
                MelCoed(),
            )

#------------------------------------------------------------------------------
class MreLvli(MreLeveledList):
    """Leveled Item."""
    classType = 'LVLI'
    copyAttrs = ('chanceNone','glob',)

    melSet = MelSet(
        MelString('EDID','eid'),
        MelBounds(),
        MelUInt8('LVLD', 'chanceNone'),
        MelUInt8('LVLF', (MreLeveledListBase._flags, 'flags', 0L)),
        MelOptFid('LVLG', 'glob'),
        MreLeveledList.MelLlct(),
        MreLeveledList.MelLvlo(),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreLvln(MreLeveledList):
    """Leveled NPC."""
    classType = 'LVLN'
    copyAttrs = ('chanceNone','model','modt_p',)

    melSet = MelSet(
        MelString('EDID','eid'),
        MelBounds(),
        MelUInt8('LVLD', 'chanceNone'),
        MelUInt8('LVLF', (MreLeveledListBase._flags, 'flags', 0L)),
        MelOptFid('LVLG', 'glob'),
        MreLeveledList.MelLlct(),
        MreLeveledList.MelLvlo(),
        MelString('MODL','model'),
        MelBase('MODT','modt_p'),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreLvsp(MreLeveledList):
    """Leveled Spell."""
    classType = 'LVSP'

    copyAttrs = ('chanceNone',)

    melSet = MelSet(
        MelString('EDID','eid'),
        MelBounds(),
        MelUInt8('LVLD', 'chanceNone'),
        MelUInt8('LVLF', (MreLeveledListBase._flags, 'flags', 0L)),
        MreLeveledList.MelLlct(),
        MreLeveledList.MelLvlo(),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreMato(MelRecord):
    """Material Object."""
    classType = 'MATO'

    MatoTypeFlags = Flags(0L,Flags.getNames(
            (0, 'singlePass'),
        ))

    class MelMatoData(MelStruct):
        """Handle older truncated DATA for MATO subrecord."""
        def loadData(self, record, ins, sub_type, size_, readId):
            if size_ == 48:
                MelStruct.loadData(self, record, ins, sub_type, size_, readId)
                return
            elif size_ == 28:
                unpacked = ins.unpack('fffffff', size_, readId)
            else:
                raise ModSizeError(record.inName, readId, 48, size_, True)
            unpacked += self.defaults[len(unpacked):]
            setter = record.__setattr__
            for attr,value,action in zip(self.attrs,unpacked,self.actions):
                if callable(action): value = action(value)
                setter(attr,value)
            if self._debug: print unpacked

    melSet = MelSet(
        MelString('EDID','eid'),
        MelModel(),
        MelGroups('property_data',
            MelBase('DNAM', 'data_entry'),
        ),
        MelMatoData('DATA','11fI','falloffScale','falloffBias','noiseUVScale',
                  'materialUVScale','projectionVectorX','projectionVectorY',
                  'projectionVectorZ','normalDampener',
                  'singlePassColor','singlePassColor',
                  'singlePassColor',(MatoTypeFlags,'flags',0L),),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreMatt(MelRecord):
    """Material Type."""
    classType = 'MATT'

    MattTypeFlags = Flags(0L,Flags.getNames(
            (0, 'stairMaterial'),
            (1, 'arrowsStick'),
        ))

    melSet = MelSet(
        MelString('EDID','eid'),
        MelFid('PNAM', 'materialParent',),
        MelString('MNAM','materialName'),
        MelStruct('CNAM', '3f', 'red', 'green', 'blue'),
        MelFloat('BNAM', 'buoyancy'),
        MelUInt32('FNAM', (MattTypeFlags, 'flags', 0L)),
        MelFid('HNAM', 'havokImpactDataSet',),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreMesg(MelRecord):
    """Message."""
    classType = 'MESG'

    MesgTypeFlags = Flags(0L,Flags.getNames(
            (0, 'messageBox'),
            (1, 'autoDisplay'),
        ))

    melSet = MelSet(
        MelString('EDID','eid'),
        MelLString('DESC','description'),
        MelLString('FULL','full'),
        MelFid('INAM','iconUnused'), # leftover
        MelFid('QNAM','materialParent'),
        MelUInt32('DNAM', (MesgTypeFlags, 'flags', 0L)),
        MelUInt32('TNAM', 'displayTime'),
        MelGroups('menuButtons',
            MelLString('ITXT','buttonText'),
            MelConditions(),
        ),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreMgef(MelRecord):
    """Magic Effect."""
    classType = 'MGEF'

    MgefGeneralFlags = Flags(0L,Flags.getNames(
            (0, 'hostile'),
            (1, 'recover'),
            (2, 'detrimental'),
            (3, 'snaptoNavmesh'),
            (4, 'noHitEvent'),
            (5, 'unknown6'),
            (6, 'unknown7'),
            (7, 'unknown8'),
            (8, 'dispellwithKeywords'),
            (9, 'noDuration'),
            (10, 'noMagnitude'),
            (11, 'noArea'),
            (12, 'fXPersist'),
            (13, 'unknown14'),
            (14, 'goryVisuals'),
            (15, 'hideinUI'),
            (16, 'unknown17'),
            (17, 'noRecast'),
            (18, 'unknown19'),
            (19, 'unknown20'),
            (20, 'unknown21'),
            (21, 'powerAffectsMagnitude'),
            (22, 'powerAffectsDuration'),
            (23, 'unknown24'),
            (24, 'unknown25'),
            (25, 'unknown26'),
            (26, 'painless'),
            (27, 'noHitEffect'),
            (28, 'noDeathDispel'),
            (29, 'unknown30'),
            (30, 'unknown31'),
            (31, 'unknown32'),
    ))

    melSet = MelSet(
        MelString('EDID','eid'),
        MelVmad(),
        MelLString('FULL','full'),
        MelFid('MDOB','harvestIngredient'),
        MelKeywords(),
        MelPartialCounter(MelStruct(
            'DATA', 'IfI2iH2sIf4I4fIi4Ii3IfIfI4s4s4I2f',
            (MgefGeneralFlags, 'flags', 0L), 'baseCost', (FID, 'assocItem'),
            'magicSkill', 'resistValue', 'counterEffectCount',
            ('unknown1', null2), (FID, 'castingLight'), 'taperWeight',
            (FID, 'hitShader'), (FID, 'enchantShader'), 'minimumSkillLevel',
            'spellmakingArea', 'spellmakingCastingTime', 'taperCurve',
            'taperDuration', 'secondAvWeight', 'mgefArchtype', 'actorValue',
            (FID, 'projectile'), (FID, 'explosion'), 'castingType', 'delivery',
            'secondActorValue', (FID, 'castingArt'), (FID, 'hitEffectArt'),
            (FID, 'impactData'), 'skillUsageMultiplier',
            (FID, 'dualCastingArt'), 'dualCastingScale', (FID,'enchantArt'),
            ('unknown2', null4), ('unknown3', null4), (FID, 'equipAbility'),
            (FID, 'imageSpaceModifier'), (FID, 'perkToApply'),
            'castingSoundLevel', 'scriptEffectAiScore',
            'scriptEffectAiDelayTime'),
            counter='counterEffectCount', counts='counterEffects'),
        MelFids('ESCE','counterEffects'),
        MelStructA('SNDD','2I','sounds','soundType',(FID,'sound')),
        MelLString('DNAM','magicItemDescription'),
        MelConditions(),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreMisc(MelRecord):
    """Misc. Item."""
    classType = 'MISC'

    melSet = MelSet(
        MelString('EDID','eid'),
        MelVmad(),
        MelBounds(),
        MelLString('FULL','full'),
        MelModel(),
        MelString('ICON','iconPath'),
        MelString('MICO','smallIconPath'),
        MelDestructible(),
        MelOptFid('YNAM', 'pickupSound'),
        MelOptFid('ZNAM', 'dropSound'),
        MelKeywords(),
        MelStruct('DATA','=If','value','weight'),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreMovt(MelRecord):
    """Movement Type."""
    classType = 'MOVT'
    class MelMovtSped(MelStruct):
        """Handle older truncated SPED for MOVT subrecord."""
        def loadData(self, record, ins, sub_type, size_, readId):
            if size_ == 44:
                MelStruct.loadData(self, record, ins, sub_type, size_, readId)
                return
            elif size_ == 40:
                unpacked = ins.unpack('10f', size_, readId)
            else:
                raise ModSizeError(record.inName, readId, 44, size_, True)
            unpacked += self.defaults[len(unpacked):]
            setter = record.__setattr__
            for attr,value,action in zip(self.attrs,unpacked,self.actions):
                if callable(action): value = action(value)
                setter(attr,value)
            if self._debug: print unpacked

    melSet = MelSet(
        MelString('EDID','eid'),
        MelString('MNAM','mnam_n'),
        MelMovtSped('SPED','11f','leftWalk','leftRun','rightWalk','rightRun',
                  'forwardWalk','forwardRun','backWalk','backRun',
                  'rotateInPlaceWalk','rotateInPlaceRun',
                  'rotateWhileMovingRun'),
        MelOptStruct('INAM','3f','directional','movementSpeed','rotationSpeed'),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreMstt(MelRecord):
    """Moveable Static."""
    classType = 'MSTT'

    MsttTypeFlags = Flags(0L,Flags.getNames(
        (0, 'onLocalMap'),
        (1, 'unknown2'),
    ))

    melSet = MelSet(
        MelString('EDID','eid'),
        MelBounds(),
        MelLString('FULL','full'),
        MelModel(),
        MelDestructible(),
        MelUInt8('DATA', (MsttTypeFlags, 'flags', 0L)),
        MelFid('SNAM','sound'),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreMusc(MelRecord):
    """Music Type."""
    classType = 'MUSC'

    MuscTypeFlags = Flags(0L,Flags.getNames(
            (0,'playsOneSelection'),
            (1,'abruptTransition'),
            (2,'cycleTracks'),
            (3,'maintainTrackOrder'),
            (4,'unknown5'),
            (5,'ducksCurrentTrack'),
        ))

    melSet = MelSet(
        MelString('EDID','eid'),
        MelUInt32('FNAM', (MuscTypeFlags, 'flags', 0L)),
        # Divided by 100 in TES5Edit, probably for editing only
        MelStruct('PNAM','2H','priority','duckingDB'),
        MelFloat('WNAM', 'fadeDuration'),
        MelFidList('TNAM','musicTracks'),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreMust(MelRecord):
    """Music Track."""
    classType = 'MUST'

    melSet = MelSet(
        MelString('EDID','eid'),
        MelUInt32('CNAM', 'trackType'),
        MelOptFloat('FLTV', 'duration'),
        MelOptUInt32('DNAM', 'fadeOut'),
        MelString('ANAM','trackFilename'),
        MelString('BNAM','finaleFilename'),
        MelStructA('FNAM','f','points',('cuePoints',0.0)),
        MelOptStruct('LNAM','2fI','loopBegins','loopEnds','loopCount',),
        MelConditionCounter(),
        MelConditions(),
        MelFidList('SNAM','tracks',),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
# Not Mergable - FormIDs unaccounted for
class MreNavi(MelRecord):
    """Navigation Mesh Info Map."""
    classType = 'NAVI'

    melSet = MelSet(
        MelString('EDID','eid'),
        MelUInt32('NVER', 'version'),
        # NVMI and NVPP would need special routines to handle them
        # If no mitigation is needed, then leave it as MelBase
        MelBase('NVMI','navigationMapInfos',),
        MelBase('NVPP','preferredPathing',),
        MelFidList('NVSI','navigationMesh'),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
# Not Mergable - FormIDs unaccounted for
class MreNavm(MelRecord):
    """Navigation Mesh."""
    classType = 'NAVM'

    NavmTrianglesFlags = Flags(0L,Flags.getNames(
            (0, 'edge01link'),
            (1, 'edge12link'),
            (2, 'edge20link'),
            (3, 'unknown4'),
            (4, 'unknown5'),
            (5, 'unknown6'),
            (6, 'preferred'),
            (7, 'unknown8'),
            (8, 'unknown9'),
            (9, 'water'),
            (10, 'door'),
            (11, 'found'),
            (12, 'unknown13'),
            (13, 'unknown14'),
            (14, 'unknown15'),
            (15, 'unknown16'),
        ))

    NavmCoverFlags = Flags(0L,Flags.getNames(
            (0, 'edge01wall'),
            (1, 'edge01ledgecover'),
            (2, 'unknown3'),
            (3, 'unknown4'),
            (4, 'edge01left'),
            (5, 'edge01right'),
            (6, 'edge12wall'),
            (7, 'edge12ledgecover'),
            (8, 'unknown9'),
            (9, 'unknown10'),
            (10, 'edge12left'),
            (11, 'edge12right'),
            (12, 'unknown13'),
            (13, 'unknown14'),
            (14, 'unknown15'),
            (15, 'unknown16'),
        ))

    melSet = MelSet(
        MelString('EDID','eid'),
        # NVNM, ONAM, PNAM, NNAM would need special routines to handle them
        # If no mitigation is needed, then leave it as MelBase
        MelBase('NVNM','navMeshGeometry'),
        MelBase('ONAM','onam_p'),
        MelBase('PNAM','pnam_p'),
        MelBase('NNAM','nnam_p'),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreNpc(MelRecord):
    """Non-Player Character."""
    classType = 'NPC_'

    NpcFlags2 = Flags(0L,Flags.getNames(
            (0, 'useTraits'),
            (1, 'useStats'),
            (2, 'useFactions'),
            (3, 'useSpellList'),
            (4, 'useAIData'),
            (5, 'useAIPackages'),
            (6, 'useModelAnimation?'),
            (7, 'useBaseData'),
            (8, 'useInventory'),
            (9, 'useScript'),
            (10, 'useDefPackList'),
            (11, 'useAttackData'),
            (12, 'useKeywords'),
        ))

    NpcFlags1 = Flags(0L,Flags.getNames(
            (0, 'female'),
            (1, 'essential'),
            (2, 'isCharGenFacePreset'),
            (3, 'respawn'),
            (4, 'autoCalc'),
            (5, 'unique'),
            (6, 'doesNotAffectStealth'),
            (7, 'pcLevelMult'),
            (8, 'useTemplate?'),
            (9, 'unknown9'),
            (10, 'unknown10'),
            (11, 'protected'),
            (12, 'unknown12'),
            (13, 'unknown13'),
            (14, 'summonable'),
            (15, 'unknown15'),
            (16, 'doesNotBleed'),
            (17, 'unknown17'),
            (18, 'bleedoutOverride'),
            (19, 'oppositeGenderAnims'),
            (20, 'simpleActor'),
            (21, 'loopedscript?'),
            (22, 'unknown22'),
            (23, 'unknown23'),
            (24, 'unknown24'),
            (25, 'unknown25'),
            (26, 'unknown26'),
            (27, 'unknown27'),
            (28, 'loopedaudio?'),
            (29, 'isGhost'),
            (30, 'unknown30'),
            (31, 'invulnerable'),
        ))

    melSet = MelSet(
        MelString('EDID', 'eid'),
        MelVmad(),
        MelBounds(),
        MelStruct('ACBS','I2Hh3Hh3H',
                  (NpcFlags1,'flags',0L),'magickaOffset',
                  'staminaOffset','level','calcMin',
                  'calcMax','speedMultiplier','dispotionBase',
                  (NpcFlags2,'npcFlags2',0L),'healthOffset','bleedoutOverride',
                  ),
        MelStructs('SNAM','IB3s','factions',(FID, 'faction'), 'rank', 'snamUnused'),
        MelOptFid('INAM', 'deathItem'),
        MelOptFid('VTCK', 'voice'),
        MelOptFid('TPLT', 'template'),
        MelFid('RNAM','race'),
        # TODO(inf) Kept it as such, why little-endian?
        MelCounter(MelStruct('SPCT', '<I', 'spell_count'), counts='spells'),
        MelFids('SPLO', 'spells'),
        MelDestructible(),
        MelOptFid('WNAM', 'wormArmor'),
        MelOptFid('ANAM', 'farawaymodel'),
        MelOptFid('ATKR', 'attackRace'),
        MelGroups('attacks',
            MelAttackData(),
            MelString('ATKE', 'attackEvents')
        ),
        MelOptFid('SPOR', 'spectator'),
        MelOptFid('OCOR', 'observe'),
        MelOptFid('GWOR', 'guardWarn'),
        MelOptFid('ECOR', 'combat'),
        MelCounter(MelUInt32('PRKZ', 'perk_count'), counts='perks'),
        MelGroups('perks',
            MelOptStruct('PRKR','IB3s',(FID, 'perk'),'rank','prkrUnused'),
        ),
        MelItemsCounter(),
        MelItems(),
        MelStruct('AIDT', 'BBBBBBBBIII', 'aggression', 'confidence',
                  'engergy', 'responsibility', 'mood', 'assistance',
                  'aggroRadiusBehavior',
                  'aidtUnknown', 'warn', 'warnAttack', 'attack'),
        MelFids('PKID', 'packages',),
        MelKeywords(),
        MelFid('CNAM', 'class'),
        MelLString('FULL','full'),
        MelLString('SHRT', 'shortName'),
        MelBase('DATA', 'marker'),
        MelStruct('DNAM','36BHHH2sfB3s',
            'oneHandedSV','twoHandedSV','marksmanSV','blockSV','smithingSV',
            'heavyArmorSV','lightArmorSV','pickpocketSV','lockpickingSV',
            'sneakSV','alchemySV','speechcraftSV','alterationSV','conjurationSV',
            'destructionSV','illusionSV','restorationSV','enchantingSV',
            'oneHandedSO','twoHandedSO','marksmanSO','blockSO','smithingSO',
            'heavyArmorSO','lightArmorSO','pickpocketSO','lockpickingSO',
            'sneakSO','alchemySO','speechcraftSO','alterationSO','conjurationSO',
            'destructionSO','illusionSO','restorationSO','enchantingSO',
            'health','magicka','stamina',('dnamUnused1',null2),
            'farawaymodeldistance','gearedupweapons',('dnamUnused2',null3)),
        MelFids('PNAM', 'head_part_addons',),
        # TODO(inf) Left everything starting from here alone because it uses
        #  little-endian - why?
        MelOptStruct('HCLF', '<I', (FID, 'hair_color')),
        MelOptStruct('ZNAM', '<I', (FID, 'combat_style')),
        MelOptStruct('GNAM', '<I', (FID, 'gifts')),
        MelBase('NAM5', 'nam5_p'),
        MelStruct('NAM6', '<f', 'height'),
        MelStruct('NAM7', '<f', 'weight'),
        MelStruct('NAM8', '<I', 'sound_level'),
        MelGroups('event_sound',
            MelStruct('CSDT', '<I', 'sound_type'),
            MelGroups('sound',
                MelStruct('CSDI', '<I', (FID, 'sound')),
                MelStruct('CSDC', '<B', 'chance')
            )
        ),
        MelOptStruct('CSCR', '<I', (FID, 'audio_template')),
        MelOptStruct('DOFT', '<I', (FID, 'default_outfit')),
        MelOptStruct('SOFT', '<I', (FID, 'sleep_outfit')),
        MelOptStruct('DPLT', '<I', (FID, 'default_package')),
        MelOptStruct('CRIF', '<I', (FID, 'crime_faction')),
        MelOptStruct('FTST', '<I', (FID, 'face_texture')),
        MelOptStruct('QNAM', '<fff', 'skin_tone_r' ,'skin_tone_g', 'skin_tone_b'),
        MelOptStruct('NAM9', '<fffffffffffffffffff', 'nose_long', 'nose_up',
                     'jaw_up', 'jaw_wide', 'jaw_forward', 'cheeks_up', 'cheeks_back',
                     'eyes_up', 'eyes_out', 'brows_up', 'brows_out', 'brows_forward',
                     'lips_up', 'lips_out', 'chin_wide', 'chin_down', 'chin_underbite',
                     'eyes_back', 'nam9_unused'),
        MelOptStruct('NAMA', '<IiII', 'nose', 'unknown', 'eyes', 'mouth'),
        MelGroups('face_tint_layer',
            MelStruct('TINI', '<H', 'tint_item'),
            MelStruct('TINC', '<4B', 'tintRed', 'tintGreen', 'tintBlue' ,'tintAlpha'),
            MelStruct('TINV', '<i', 'tint_value'),
            MelStruct('TIAS', '<h', 'preset'),
        ),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreOtft(MelRecord):
    """Outfit."""
    classType = 'OTFT'
    melSet = MelSet(
        MelString('EDID','eid'),
        MelFidList('INAM','items'),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
# Marker for organization please don't remove ---------------------------------
# PACK ------------------------------------------------------------------------
class MrePack(MelRecord):
    """Package."""
    classType = 'PACK'

    PackFlags10 = Flags(0L,Flags.getNames(
            (0, 'successCompletesPackage'),
        ))

    PackFlags9 = Flags(0L,Flags.getNames(
            (0, 'repeatwhenComplete'),
            (1, 'unknown1'),
        ))

    PackFlags1 = Flags(0L,Flags.getNames(
            (0, 'offersServices'),
            (1, 'unknown2'),
            (2, 'mustcomplete'),
            (3, 'maintainSpeedatGoal'),
            (4, 'unknown5'),
            (5, 'unknown6'),
            (6, 'unlockdoorsatpackagestart'),
            (7, 'unlockdoorsatpackageend'),
            (8, 'unknown9'),
            (9, 'continueifPCNear'),
            (10, 'onceperday'),
            (11, 'unknown12'),
            (12, 'unknown13'),
            (13, 'preferredSpeed'),
            (14, 'unknown15'),
            (15, 'unknown16'),
            (16, 'unknown17'),
            (17, 'alwaysSneak'),
            (18, 'allowSwimming'),
            (19, 'unknown20'),
            (20, 'ignoreCombat'),
            (21, 'weaponsUnequipped'),
            (22, 'unknown23'),
            (23, 'weaponDrawn'),
            (24, 'unknown25'),
            (25, 'unknown26'),
            (26, 'unknown27'),
            (27, 'noCombatAlert'),
            (28, 'unknown29'),
            (29, 'wearSleepOutfitunused'),
            (30, 'unknown31'),
            (31, 'unknown32'),
        ))

    PackFlags2 = Flags(0L,Flags.getNames(
            (0, 'hellostoplayer'),
            (1, 'randomconversations'),
            (2, 'observecombatbehavior'),
            (3, 'greetcorpsebehavior'),
            (4, 'reactiontoplayeractions'),
            (5, 'friendlyfirecomments'),
            (6, 'aggroRadiusBehavior'),
            (7, 'allowIdleChatter'),
            (8, 'unknown9'),
            (9, 'worldInteractions'),
            (10, 'unknown11'),
            (11, 'unknown12'),
            (12, 'unknown13'),
            (13, 'unknown14'),
            (14, 'unknown15'),
            (15, 'unknown16'),
        ))

    # Data Inputs Flags
    PackFlags3 = Flags(0L,Flags.getNames(
            (0, 'public'),
        ))

    class MelPackLT(MelOptStruct):
        """For PLDT and PTDT. Second element of both may be either an FID or a long,
        depending on value of first element."""
        def loadData(self, record, ins, sub_type, size_, readId):
            if ((self.subType == 'PLDT' and size_ == 12) or
                (self.subType == 'PLD2' and size_ == 12) or
                (self.subType == 'PTDT' and size_ == 16) or
                (self.subType == 'PTD2' and size_ == 16)):
                MelOptStruct.loadData(self, record, ins, sub_type, size_, readId)
                return
            elif ((self.subType == 'PTDT' and size_ == 12) or
                  (self.subType == 'PTD2' and size_ == 12)):
                unpacked = ins.unpack('iIi', size_, readId)
            else:
                raise "Unexpected size encountered for PACK:%s subrecord: %s" % (self.subType, size_)
            unpacked += self.defaults[len(unpacked):]
            setter = record.__setattr__
            for attr,value,action in zip(self.attrs,unpacked,self.actions):
                if callable(action): value = action(value)
                setter(attr,value)
            if self._debug: print unpacked
        def hasFids(self,formElements):
            formElements.add(self)
        def dumpData(self,record,out):
            if ((self.subType == 'PLDT' and (record.locType or record.locId)) or
                (self.subType == 'PLD2' and (record.locType2 or record.locId2)) or
                (self.subType == 'PTDT' and (record.targetType or record.targetId)) or
                (self.subType == 'PTD2' and (record.targetType2 or record.targetId2))):
                MelStruct.dumpData(self,record,out)
        def mapFids(self,record,function,save=False):
            """Applies function to fids. If save is true, then fid is set
            to result of function."""
            if self.subType == 'PLDT' and record.locType != 5:
                result = function(record.locId)
                if save: record.locId = result
            elif self.subType == 'PLD2' and record.locType2 != 5:
                result = function(record.locId2)
                if save: record.locId2 = result
            elif self.subType == 'PTDT' and record.targetType != 2:
                result = function(record.targetId)
                if save: record.targetId = result
            elif self.subType == 'PTD2' and record.targetType2 != 2:
                result = function(record.targetId2)
                if save: record.targetId2 = result

    class MelPackDistributor(MelNull):
        """Handles embedded script records. Distributes load
        duties to other elements as needed."""
        def __init__(self):
            self._debug = False
        def getLoaders(self,loaders):
            """Self as loader for structure types."""
            for subType in ('POBA','POEA','POCA'):
                loaders[subType] = self
        def setMelSet(self,melSet):
            """Set parent melset. Need this so that can reassign loaders later."""
            self.melSet = melSet
            self.loaders = {}
            for element in melSet.elements:
                attr = element.__dict__.get('attr',None)
                if attr: self.loaders[attr] = element
        def loadData(self, record, ins, sub_type, size_, readId):
            if sub_type == 'POBA':
                element = self.loaders['onBegin']
            elif sub_type == 'POEA':
                element = self.loaders['onEnd']
            elif sub_type == 'POCA':
                element = self.loaders['onChange']
            # 'SCHR','SCDA','SCTX','SLSD','SCVR','SCRV','SCRO',
            # All older Script records chould be discarded if found
            for subtype in ('INAM','TNAM'):
                self.melSet.loaders[subtype] = element
            element.loadData(self, record, ins, sub_type, size_, readId)

    melSet = MelSet(
        MelString('EDID','eid'),
        MelVmad(),
        MelStruct('PKDT','I3BsH2s',(PackFlags1,'generalFlags',0L),'type','interruptOverride',
                  'preferredSpeed','unknown',(PackFlags2,'interruptFlags',0L),'unknown',),
        MelStruct('PSDT','2bB2b3si','month','dayofweek','date','hour','minute',
                  'unused','durationminutes',),
        MelConditions(),
        MelGroup('idleAnimations',
            MelUInt32('IDLF', 'type'),
            MelPartialCounter(MelStruct('IDLC', 'B3s', 'animation_count',
                                        'unknown'),
                              counter='animation_count', counts='animations'),
            MelFloat('IDLT', 'timerSetting',),
            MelFidList('IDLA', 'animations'),
            MelBase('IDLB','unknown'),
        ),
        MelFid('CNAM','combatStyle',),
        MelFid('QNAM','ownerQuest',),
        MelStruct('PKCU','3I','dataInputCount',(FID,'packageTemplate'),
                  'versionCount',),
        MelGroup('packageData',
            MelGroups('inputValues',
                MelString('ANAM','type'),
                # CNAM Needs Union Decider, No FormID
                MelBase('CNAM','unknown',),
                MelBase('BNAM','unknown',),
                # PDTO Needs Union Decider
                MelStructs('PDTO','2I','topicData','type',(FID,'data'),),
                # PLDT Needs Union Decider, No FormID
                MelStruct('PLDT','iIi','locationType','locationValue','radius',),
                # PTDA Needs Union Decider
                MelStruct('PTDA','iIi','targetDataType',(FID,'targetDataTarget'),
                          'targetDataCountDist',),
                MelBase('TPIC','unknown',),
            ),
            MelGroups('dataInputs',
                MelSInt8('UNAM', 'index'),
                MelString('BNAM','name',),
                MelUInt32('PNAM', (PackFlags1, 'flags', 0L)),
            ),
        ),
        MelBase('XNAM','marker',),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MrePerk(MelRecord):
    """Perk."""
    classType = 'PERK'

    _PerkScriptFlags = Flags(0L,Flags.getNames(
        (0, 'runImmediately'),
        (1, 'replaceDefault'),
    ))

    class MelPerkData(MelStruct):
        """Handle older truncated DATA for PERK subrecord."""
        def loadData(self, record, ins, sub_type, size_, readId):
            if size_ == 5:
                MelStruct.loadData(self, record, ins, sub_type, size_, readId)
                return
            elif size_ == 4:
                unpacked = ins.unpack('BBBB', size_, readId)
            else:
                raise "Unexpected size encountered for DATA subrecord: %s" % size_
            unpacked += self.defaults[len(unpacked):]
            setter = record.__setattr__
            for attr,value,action in zip(self.attrs,unpacked,self.actions):
                if callable(action): value = action(value)
                setter(attr,value)
            if self._debug: print unpacked, record.flagsA.getTrueAttrs()

    class MelPerkEffects(MelGroups):
        def __init__(self,attr,*elements):
            MelGroups.__init__(self,attr,*elements)
        def setMelSet(self,melSet):
            self.melSet = melSet
            self.attrLoaders = {}
            for element in melSet.elements:
                attr = element.__dict__.get('attr',None)
                if attr: self.attrLoaders[attr] = element
        def loadData(self, record, ins, sub_type, size_, readId):
            if sub_type == 'DATA' or sub_type == 'CTDA':
                effects = record.__getattribute__(self.attr)
                if not effects:
                    if sub_type == 'DATA':
                        element = self.attrLoaders['_data']
                    elif sub_type == 'CTDA':
                        element = self.attrLoaders['conditions']
                    element.loadData(record, ins, sub_type, size_, readId)
                    return
            MelGroups.loadData(self, record, ins, sub_type, size_, readId)

    melSet = MelSet(
        MelString('EDID','eid'),
        MelVmad(),
        MelLString('FULL','full'),
        MelLString('DESC','description'),
        MelString('ICON','iconPath'),
        MelString('MICO','smallIconPath'),
        MelConditions(),
        MelGroup('_data',
            MelPerkData('DATA', 'BBBBB', ('trait', 0), ('minLevel', 0),
                        ('ranks', 0), ('playable', 0), ('hidden', 0)),
        ),
        MelFid('NNAM', 'next_perk'),
        MelPerkEffects('effects',
            MelStruct('PRKE', 'BBB', 'type', 'rank', 'priority'),
            MelUnion({
                0: MelStruct('DATA', 'IB3s', (FID, 'quest'), 'quest_stage',
                             'unusedDATA'),
                1: MelFid('DATA', 'ability'),
                2: MelStruct('DATA', '3B', 'entry_point', 'function',
                             'perk_conditions_tab_count'),
            }, decider=AttrValDecider('type')),
            MelGroups('effectConditions',
                MelSInt8('PRKC', 'runOn'),
                MelConditions(),
            ),
            MelGroups('effectParams',
                MelUInt8('EPFT', 'function_parameter_type'),
                MelLString('EPF2','buttonLabel'),
                MelStruct('EPF3','2H',(_PerkScriptFlags, 'script_flags', 0L),
                          'fragment_index'),
                # EPFT has the following meanings:
                #  0: Unknown
                #  1: EPFD=float
                #  2: EPFD=float, float
                #  3: EPFD=fid (LVLI)
                #  4: EPFD=fid (SPEL), EPF2=string, EPF3=uint16 (flags)
                #  5: EPFD=fid (SPEL)
                #  6: EPFD=string
                #  7: EPFD=lstring
                # TODO(inf) there is a special case: If EPFT is 2 and
                #  DATA/function is one of 5, 12, 13 or 14, then:
                #  EPFD=uint32, float
                #  See commented out skeleton below - needs '../' syntax
                MelUnion({
                    0: MelBase('EPFD', 'param1'),
                    1: MelFloat('EPFD', 'param1'),
                    2: MelStruct('EPFD', 'If', 'param1', 'param2'),
#                    2: MelUnion({
#                        5:  MelStruct('EPFD', 'If', 'param1', 'param2'),
#                        12: MelStruct('EPFD', 'If', 'param1', 'param2'),
#                        13: MelStruct('EPFD', 'If', 'param1', 'param2'),
#                        14: MelStruct('EPFD', 'If', 'param1', 'param2'),
#                    }, decider=AttrValDecider('../function',
#                                                 assign_missing=-1),
#                        fallback=MelStruct('EPFD', '2f', 'param1', 'param2')),
                    3: MelFid('EPFD', 'param1'),
                    4: MelFid('EPFD', 'param1'),
                    5: MelFid('EPFD', 'param1'),
                    6: MelString('EPFD', 'param1'),
                    7: MelLString('EPFD', 'param1'),
                }, decider=AttrValDecider('function_parameter_type')),
            ),
            MelBase('PRKF','footer'),
        ),
    )
    melSet.elements[-1].setMelSet(melSet)
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreProj(MelRecord):
    """Projectile."""
    classType = 'PROJ'

    ProjTypeFlags = Flags(0L,Flags.getNames(
        (0, 'hitscan'),
        (1, 'explosive'),
        (2, 'altTriger'),
        (3, 'muzzleFlash'),
        (4, 'unknown4'),
        (5, 'canbeDisable'),
        (6, 'canbePickedUp'),
        (7, 'superSonic'),
        (8, 'pinsLimbs'),
        (9, 'passThroughSmallTransparent'),
        (10, 'disableCombatAimCorrection'),
        (11, 'rotation'),
    ))

    class MelProjData(MelStruct):
        """Handle older truncated DATA for PROJ subrecord."""
        def loadData(self, record, ins, sub_type, size_, readId):
            if size_ == 92:
                MelStruct.loadData(self, record, ins, sub_type, size_, readId)
                return
            elif size_ == 88:
                unpacked = ins.unpack('2H3f2I3f2I3f3I4fI', size_, readId)
            elif size_ == 84:
                unpacked = ins.unpack('2H3f2I3f2I3f3I4f', size_, readId)
            else:
                raise ModSizeError(record.inName, readId, 92, size_, True)
            unpacked += self.defaults[len(unpacked):]
            setter = record.__setattr__
            for attr,value,action in zip(self.attrs,unpacked,self.actions):
                if callable(action): value = action(value)
                setter(attr,value)
            if self._debug: print unpacked

    melSet = MelSet(
        MelString('EDID','eid'),
        MelBounds(),
        MelLString('FULL','full'),
        MelModel(),
        MelDestructible(),
        MelProjData('DATA','2H3f2I3f2I3f3I4f2I',(ProjTypeFlags,'flags',0L),'projectileTypes',
                  ('gravity',0.00000),('speed',10000.00000),('range',10000.00000),
                  (FID,'light',0),(FID,'muzzleFlash',0),('tracerChance',0.00000),
                  ('explosionAltTrigerProximity',0.00000),('explosionAltTrigerTimer',0.00000),
                  (FID,'explosion',0),(FID,'sound',0),('muzzleFlashDuration',0.00000),
                  ('fadeDuration',0.00000),('impactForce',0.00000),
                  (FID,'soundCountDown',0),(FID,'soundDisable',0),(FID,'defaultWeaponSource',0),
                  ('coneSpread',0.00000),('collisionRadius',0.00000),('lifetime',0.00000),
                  ('relaunchInterval',0.00000),(FID,'decalData',0),(FID,'collisionLayer',0),),
        MelGroup('models',
            MelString('NAM1','muzzleFlashPath'),
            # Ignore texture hashes - they're only an optimization, plenty of
            # records in Skyrim.esm are missing them
            MelNull('NAM2'),
        ),
        MelUInt32('VNAM', 'soundLevel',),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
# Needs testing should be mergable
class MreQust(MelRecord):
    """Quest."""
    classType = 'QUST'

    _questFlags = Flags(0,Flags.getNames(
        (0,'startGameEnabled'),
        (2,'wildernessEncounter'),
        (3,'allowRepeatedStages'),
        (8,'runOnce'),
        (9,'excludeFromDialogueExport'),
        (10,'warnOnAliasFillFailure'),
    ))
    _stageFlags = Flags(0,Flags.getNames(
        (0,'unknown0'),
        (1,'startUpStage'),
        (2,'startDownStage'),
        (3,'keepInstanceDataFromHereOn'),
    ))
    stageEntryFlags = Flags(0,Flags.getNames('complete','fail'))
    objectiveFlags = Flags(0,Flags.getNames('oredWithPrevious'))
    targetFlags = Flags(0,Flags.getNames('ignoresLocks'))
    aliasFlags = Flags(0,Flags.getNames(
        (0,'reservesLocationReference'),
        (1,'optional'),
        (2,'questObject'),
        (3,'allowReuseInQuest'),
        (4,'allowDead'),
        (5,'inLoadedArea'),
        (6,'essential'),
        (7,'allowDisabled'),
        (8,'storesText'),
        (9,'allowReserved'),
        (10,'protected'),
        (11,'noFillType'),
        (12,'allowDestroyed'),
        (13,'closest'),
        (14,'usesStoredText'),
        (15,'initiallyDisabled'),
        (16,'allowCleared'),
        (17,'clearsNameWhenRemoved'),
    ))

    class MelQuestLoaders(DataDict):
        """Since CTDA/CIS1/CIS2 and FNAM subrecords occur in two different places,
        we need to replace ordinary 'loaders' dictionary with a 'dictionary' that will
        return the correct element to handle the CTDA/CIS1/CIS2/FNAM subrecord. 'Correct'
        element is determined by which other subrecords have been encountered."""
        def __init__(self,loaders,
                     dialogueConditions,
                     eventConditions,
                     stages,
                     objectives,
                     aliases,
                     description,
                     targets
            ):
            self.data = loaders
            self.type_conditions = {
                'EDID':dialogueConditions,
                'NEXT':eventConditions,
                'INDX':stages,
                'QOBJ':objectives,
                'ALID':aliases,
                'ALED':targets,
            }
            self.conditions = dialogueConditions
            self.type_fnam = {
                'EDID':objectives,
                'ANAM':aliases,
            }
            self.fnam = objectives
            self.type_nnam = {
                'EDID':objectives,
                'ANAM':description,
            }
            self.nnam = objectives
            self.type_targets = {
                'EDID':objectives,
                'ANAM':targets,
            }
            self.targets = objectives
        def __getitem__(self,key):
            if key in ('CTDA','CIS1','CIS2'): return self.conditions
            if key == 'FNAM': return self.fnam
            if key == 'NNAM': return self.nnam
            if key == 'QSTA': return self.targets
            self.conditions = self.type_conditions.get(key, self.conditions)
            self.fnam = self.type_fnam.get(key, self.fnam)
            self.nnam = self.type_nnam.get(key, self.nnam)
            self.targets = self.type_targets.get(key, self.targets)
            return self.data[key]

    melSet = MelSet(
        MelString('EDID','eid'),
        MelVmad(),
        MelLString('FULL','full'),
        MelStruct('DNAM', '=H2B4sI', (_questFlags, 'questFlags', 0L),
                  'priority', 'formVersion', 'unknown', 'questType'),
        MelOptStruct('ENAM','4s',('event',None)),
        MelFids('QTGL','textDisplayGlobals'),
        MelString('FLTR','objectWindowFilter'),
        MelConditions('dialogueConditions'),
        MelBase('NEXT','marker'),
        MelConditions('eventConditions'),
        MelGroups('stages',
            MelStruct('INDX','H2B','index',(_stageFlags,'flags',0L),'unknown'),
            MelGroups('logEntries',
                MelUInt8('QSDT', (stageEntryFlags, 'stageFlags', 0L)),
                MelConditions(),
                MelLString('CNAM','log_text'),
                MelFid('NAM0', 'nextQuest'),
                MelGroup('unused',
                    MelBase('SCHR','schr_p'),
                    MelBase('SCTX','sctx_p'),
                    MelBase('QNAM','qnam_p'),
                ),
            ),
        ),
        MelGroups('objectives',
            MelUInt16('QOBJ', 'index'),
            MelUInt32('FNAM', (objectiveFlags, 'flags', 0L)),
            MelLString('NNAM','description'),
            MelGroups('targets',
                MelStruct('QSTA','iB3s','alias',(targetFlags,'flags'),('unused1',null3)),
                MelConditions(),
            ),
        ),
        MelBase('ANAM','aliasMarker'),
        MelGroups('aliases',
            MelUnion({
                'ALST': MelOptUInt32('ALST', ('aliasId', None)),
                'ALLS': MelOptUInt32('ALLS', ('aliasId', None)),
            }),
            MelString('ALID', 'aliasName'),
            MelUInt32('FNAM', (aliasFlags, 'flags', 0L)),
            MelOptSInt32('ALFI', ('forcedIntoAlias', None)),
            MelFid('ALFL','specificLocation'),
            MelFid('ALFR','forcedReference'),
            MelFid('ALUA','uniqueActor'),
            MelGroup('locationAliasReference',
                MelSInt32('ALFA', 'alias'),
                MelFid('KNAM','keyword'),
                MelFid('ALRT','referenceType'),
            ),
            MelGroup('externalAliasReference',
                MelFid('ALEQ','quest'),
                MelSInt32('ALEA', 'alias'),
            ),
            MelGroup('createReferenceToObject',
                MelFid('ALCO','object'),
                MelStruct('ALCA', 'hH', 'alias', 'create_target'),
                MelUInt32('ALCL', 'createLevel'),
            ),
            MelGroup('findMatchingReferenceNearAlias',
                MelSInt32('ALNA', 'alias'),
                MelUInt32('ALNT', 'type'),
            ),
            MelGroup('findMatchingReferenceFromEvent',
                MelStruct('ALFE','4s',('fromEvent',null4)),
                MelStruct('ALFD','4s',('eventData',null4)),
            ),
            MelConditions(),
            MelKeywords(),
            MelItemsCounter(),
            MelItems(),
            MelFid('SPOR','spectatorOverridePackageList'),
            MelFid('OCOR','observeDeadBodyOverridePackageList'),
            MelFid('GWOR','guardWarnOverridePackageList'),
            MelFid('ECOR','combatOverridePackageList'),
            MelFid('ALDN','displayName'),
            MelFids('ALSP','aliasSpells'),
            MelFids('ALFC','aliasFactions'),
            MelFids('ALPC','aliasPackageData'),
            MelFid('VTCK','voiceType'),
            MelBase('ALED','aliasEnd'),
        ),
        MelLString('NNAM','description'),
        MelGroups('targets',
            MelStruct('QSTA', 'IB3s', (FID, 'target'), (targetFlags, 'flags'),
                      ('unknown1', null3)),
            MelConditions(),
        ),
    )
    melSet.loaders = MelQuestLoaders(melSet.loaders,
                                     melSet.elements[7],  # dialogueConditions
                                     melSet.elements[9],  # eventConditions
                                     melSet.elements[10], # stages
                                     melSet.elements[11], # objectives
                                     melSet.elements[13], # aliases
                                     melSet.elements[14], # description
                                     melSet.elements[15], # targets
        )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
# Marker for organization please don't remove ---------------------------------
# RACE ------------------------------------------------------------------------
# Needs Updating
class MreRace(MelRecord):
    """Race."""
    classType = 'RACE'

    melSet = MelSet(
        MelString('EDID','eid'),
        MelLString('FULL','full'),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
# Needs Updating
class MreRefr(MelRecord):
    """Placed Object."""
    classType = 'REFR'
    _flags = Flags(0L,Flags.getNames('visible', 'canTravelTo','showAllHidden',))
    _parentFlags = Flags(0L,Flags.getNames('oppositeParent','popIn',))
    _actFlags = Flags(0L,Flags.getNames('useDefault', 'activate','open','openByDefault'))
    _lockFlags = Flags(0L,Flags.getNames(None, None, 'leveledLock'))
    _destinationFlags = Flags(0L,Flags.getNames('noAlarm'))
    _parentActivate = Flags(0L,Flags.getNames('parentActivateOnly'))
    reflectFlags = Flags(0L,Flags.getNames('reflection', 'refraction'))
    roomDataFlags = Flags(0L,Flags.getNames(
        (6,'hasImageSpace'),
        (7,'hasLightingTemplate'),
    ))

    class MelRefrXloc(MelOptStruct):
        """Handle older truncated XLOC for REFR subrecord."""
        def loadData(self, record, ins, sub_type, size_, readId):
            if size_ == 20:
                MelStruct.loadData(self, record, ins, sub_type, size_, readId)
                return
            elif size_ == 16:
                unpacked = ins.unpack('B3sIB3s4s', size_, readId)
            elif size_ == 12:
                unpacked = ins.unpack('B3sIB3s', size_, readId)
            else:
                raise ModSizeError(record.inName, readId, 20, size_, True)
            unpacked += self.defaults[len(unpacked):]
            setter = record.__setattr__
            for attr,value,action in zip(self.attrs,unpacked,self.actions):
                if callable(action): value = action(value)
                setter(attr,value)
            if self._debug: print unpacked

    class MelRefrXmrk(MelStruct):
        """Handler for xmrk record. Conditionally loads next items."""
        def loadData(self, record, ins, sub_type, size_, readId):
            """Reads data from ins into record attribute."""
            junk = ins.read(size_, readId)
            record.hasXmrk = True
            insTell = ins.tell
            insUnpack = ins.unpack
            pos = insTell()
            (sub_type_, size_) = insUnpack('4sH', 6, readId + '.FULL')
            while sub_type_ in ['FNAM', 'FULL', 'TNAM', ]:
                if sub_type_ == 'FNAM':
                    value = insUnpack('B', size_, readId)
                    record.flags = MreRefr._flags(*value)
                elif sub_type_ == 'FULL':
                    record.full = ins.readString(size_, readId)
                elif sub_type_ == 'TNAM':
                    record.markerType, record.unused5 = insUnpack('Bs', size_, readId)
                pos = insTell()
                (sub_type_, size_) = insUnpack('4sH', 6, readId + '.FULL')
            ins.seek(pos)
            if self._debug: print ' ',record.flags,record.full,record.markerType
        def dumpData(self,record,out):
            if (record.flags,record.full,record.markerType,record.unused5,record.reputation) != self.defaults[1:]:
                record.hasXmrk = True
            if record.hasXmrk:
                try:
                    out.write(struct_pack('=4sH','XMRK',0))
                    out.packSub('FNAM','B',record.flags.dump())
                    value = record.full
                    if value is not None:
                        out.packSub0('FULL',value)
                    out.packSub('TNAM','Bs',record.markerType, record.unused5)
                except struct.error:
                    print self.subType,self.format,record.flags,record.full,record.markerType
                    raise

    melSet = MelSet(
        MelString('EDID','eid'),
        MelVmad(),
        MelFid('NAME','base'),
        MelOptStruct('XMBO','3f','boundHalfExtentsX','boundHalfExtentsY','boundHalfExtentsZ'),
        MelOptStruct('XPRM','fffffffI','primitiveBoundX','primitiveBoundY','primitiveBoundZ',
                     'primitiveColorRed','primitiveColorGreen','primitiveColorBlue',
                     'primitiveUnknown','primitiveType'),
        MelBase('XORD','xord_p'),
        MelOptStruct('XOCP','9f','occlusionPlaneWidth','occlusionPlaneHeight',
                     'occlusionPlanePosX','occlusionPlanePosY','occlusionPlanePosZ',
                     'occlusionPlaneRot1','occlusionPlaneRot2','occlusionPlaneRot3',
                     'occlusionPlaneRot4'),
        MelStructA('XPOD','II','portalData',(FID,'portalOrigin'),(FID,'portalDestination')),
        MelOptStruct('XPTL','9f','portalWidth','portalHeight','portalPosX','portalPosY','portalPosZ',
                     'portalRot1','portalRot2','portalRot3','portalRot4'),
        MelGroup('roomData',
            MelStruct('XRMR','BB2s','linkedRoomsCount',(roomDataFlags,'roomFlags'),'unknown'),
            MelFid('LNAM', 'lightingTemplate'),
            MelFid('INAM', 'imageSpace'),
            MelFids('XLRM','linkedRoom'),
            ),
        MelBase('XMBP','multiboundPrimitiveMarker'),
        MelBase('XRGD','ragdollData'),
        MelBase('XRGB','ragdollBipedData'),
        MelOptFloat('XRDS', 'radius'),
        MelStructs('XPWR','II','reflectedByWaters',(FID,'reference'),(reflectFlags,'type',),),
        MelFids('XLTW','litWaters'),
        MelOptFid('XEMI', 'emittance'),
        MelOptStruct('XLIG', '4f4s', 'fov90Delta', 'fadeDelta',
                     'end_distance_cap', 'shadowDepthBias', 'unknown'),
        MelOptStruct('XALP','BB','cutoffAlpha','baseAlpha',),
        MelOptStruct('XTEL','I6fI',(FID,'destinationFid'),'destinationPosX',
                     'destinationPosY','destinationPosZ','destinationRotX',
                     'destinationRotY','destinationRotZ',
                     (_destinationFlags,'destinationFlags')),
        MelFids('XTNM','teleportMessageBox'),
        MelFid('XMBR','multiboundReference'),
        MelBase('XWCN', 'xwcn_p',),
        MelBase('XWCS', 'xwcs_p',),
        MelOptStruct('XWCU','3f4s3f4s','offsetX','offsetY','offsetZ','unknown',
                     'angleX','angleY','angleZ','unknown'),
        MelOptStruct('XCVL','4sf4s','unknown','angleX','unknown',),
        MelFid('XCZR','unknownRef'),
        MelBase('XCZA', 'xcza_p',),
        MelFid('XCZC','unknownRef2'),
        MelOptFloat('XSCL', ('scale',1.0)),
        MelFid('XSPC','spawnContainer'),
        MelGroup('activateParents',
            MelUInt8('XAPD', (_parentActivate, 'flags', None)),
            MelStructs('XAPR','If','activateParentRefs',(FID,'reference'),'delay')
        ),
        MelFid('XLIB','leveledItemBaseObject'),
        MelSInt32('XLCM', 'levelModifier'),
        MelFid('XLCN','persistentLocation',),
        MelOptUInt32('XTRI', 'collisionLayer'),
        # {>>Lock Tab for REFR when 'Locked' is Unchecked this record is not present <<<}
        MelRefrXloc('XLOC','B3sIB3s8s','lockLevel',('unused1',null3),
                    (FID,'lockKey'),(_lockFlags,'lockFlags'),('unused3',null3),
                    ('unused4',null4+null4)),
        MelFid('XEZN','encounterZone'),
        MelOptStruct('XNDP','IH2s',(FID,'navMesh'),'teleportMarkerTriangle','unknown'),
        MelFidList('XLRT','locationRefType',),
        MelNull('XIS2',),
        MelOwnership(),
        MelOptSInt32('XCNT', 'count'),
        MelOptFloat('XCHG', ('charge', None)),
        MelFid('XLRL','locationReference'),
        MelOptStruct('XESP','IB3s',(FID,'parent'),(_parentFlags,'parentFlags'),('unused6',null3)),
        MelStructs('XLKR','II','linkedReference',(FID,'keywordRef'),(FID,'linkedRef')),
        MelGroup('patrolData',
            MelFloat('XPRD', 'idleTime'),
            MelBase('XPPA','patrolScriptMarker'),
            MelFid('INAM', 'idle'),
            MelBase('SCHR','schr_p',),
            MelBase('SCTX','sctx_p',),
            MelStructs('PDTO','2I','topicData','type',(FID,'data'),),
        ),
        MelOptUInt32('XACT', (_actFlags, 'actFlags', 0L)),
        MelOptFloat('XHTW', 'headTrackingWeight'),
        MelOptFloat('XFVC', 'favorCost'),
        MelBase('ONAM','onam_p'),
        MelGroup('markerData',
            MelNull('XMRK',),
            MelOptUInt8('FNAM', 'mapFlags',),
            MelString('FULL','full'),
            MelOptStruct('TNAM','Bs','markerType','unknown',),
        ),
        MelFid('XATR', 'attachRef'),
        MelOptStruct('XLOD','3f',('lod1',None),('lod2',None),('lod3',None)),
        MelOptStruct('DATA','=6f',('posX',None),('posY',None),('posZ',None),
                     ('rotX',None),('rotY',None),('rotZ',None)),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreRegn(MelRecord):
    """Region."""
    classType = 'REGN'
    obflags = Flags(0L,Flags.getNames(
        ( 0,'conform'),
        ( 1,'paintVertices'),
        ( 2,'sizeVariance'),
        ( 3,'deltaX'),
        ( 4,'deltaY'),
        ( 5,'deltaZ'),
        ( 6,'Tree'),
        ( 7,'hugeRock'),))
    sdflags = Flags(0L,Flags.getNames(
        ( 0,'pleasant'),
        ( 1,'cloudy'),
        ( 2,'rainy'),
        ( 3,'snowy'),))
    rdatFlags = Flags(0L,Flags.getNames(
        ( 0,'Override'),))

    melSet = MelSet(
        MelString('EDID','eid'),
        MelStruct('RCLR','3Bs','mapRed','mapBlue','mapGreen',('unused1',null1)),
        MelFid('WNAM','worldspace'),
        MelGroups('areas',
            MelUInt32('RPLI', 'edgeFalloff'),
            MelStructA('RPLD','2f','points','posX','posY')
        ),
        MelGroups('entries',
            MelStruct('RDAT', 'I2B2s','entryType', (rdatFlags,'flags'), 'priority',
                     ('unused1',null2)),
            MelString('ICON','iconPath'),
            MelRegnEntrySubrecord(7, MelFid('RDMO', 'music')),
            MelRegnEntrySubrecord(7, MelStructA(
                'RDSA', '2If', 'sounds', (FID, 'sound'), (sdflags, 'flags'),
                'chance')),
            MelRegnEntrySubrecord(4, MelString('RDMP', 'mapName')),
            MelRegnEntrySubrecord(2, MelStructA(
                'RDOT', 'IH2sfBBBBH4sffffHHH2s4s', 'objects', (FID,'objectId'),
                'parentIndex', ('unused1', null2), 'density', 'clustering',
                'minSlope', 'maxSlope',(obflags, 'flags'), 'radiusWRTParent',
                'radius', ('unk1', null4), 'maxHeight', 'sink', 'sinkVar',
                'sizeVar', 'angleVarX','angleVarY',  'angleVarZ',
                ('unused2', null2), ('unk2', null4))),
            MelRegnEntrySubrecord(6, MelStructA(
                'RDGS', 'I4s', 'grass', ('unknown',null4))),
            MelRegnEntrySubrecord(3, MelStructA(
                'RDWT', '3I', 'weather', (FID, 'weather', None), 'chance',
                (FID, 'global', None))),
        ),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreRela(MelRecord):
    """Relationship."""
    classType = 'RELA'

    RelationshipFlags = Flags(0L,Flags.getNames(
        (0,'Unknown 1'),
        (1,'Unknown 2'),
        (2,'Unknown 3'),
        (3,'Unknown 4'),
        (4,'Unknown 5'),
        (5,'Unknown 6'),
        (6,'Unknown 7'),
        (7,'Secret'),
    ))

    melSet = MelSet(
        MelString('EDID','eid'),
        MelStruct('DATA','2IHsBI',(FID,'parent'),(FID,'child'),'rankType',
                  'unknown',(RelationshipFlags,'relaFlags',0L),(FID,'associationType'),),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreRevb(MelRecord):
    """Reverb Parameters"""
    classType = 'REVB'

    melSet = MelSet(
        MelString('EDID','eid'),
        MelStruct('DATA','2H4b6B','decayTimeMS','hfReferenceHZ','roomFilter',
                  'hfRoomFilter','reflections','reverbAmp','decayHFRatio',
                  'reflectDelayMS','reverbDelayMS','diffusion','density',
                  'unknown',),
        )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreRfct(MelRecord):
    """Visual Effect."""
    classType = 'RFCT'

    RfctTypeFlags = Flags(0L,Flags.getNames(
        (0, 'rotateToFaceTarget'),
        (1, 'attachToCamera'),
        (2, 'inheritRotation'),
    ))

    melSet = MelSet(
        MelString('EDID','eid'),
        MelStruct('DATA','3I',(FID,'impactSet'),(FID,'impactSet'),(RfctTypeFlags,'flags',0L),),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreScen(MelRecord):
    """Scene."""
    classType = 'SCEN'

    ScenFlags5 = Flags(0L,Flags.getNames(
            (0, 'unknown1'),
            (1, 'unknown2'),
            (2, 'unknown3'),
            (3, 'unknown4'),
            (4, 'unknown5'),
            (5, 'unknown6'),
            (6, 'unknown7'),
            (7, 'unknown8'),
            (8, 'unknown9'),
            (9, 'unknown10'),
            (10, 'unknown11'),
            (11, 'unknown12'),
            (12, 'unknown13'),
            (13, 'unknown14'),
            (14, 'unknown15'),
            (15, 'faceTarget'),
            (16, 'looping'),
            (17, 'headtrackPlayer'),
        ))

    ScenFlags3 = Flags(0L,Flags.getNames(
            (0, 'deathPauseunsused'),
            (1, 'deathEnd'),
            (2, 'combatPause'),
            (3, 'combatEnd'),
            (4, 'dialoguePause'),
            (5, 'dialogueEnd'),
            (6, 'oBS_COMPause'),
            (7, 'oBS_COMEnd'),
        ))

    ScenFlags2 = Flags(0L,Flags.getNames(
            (0, 'noPlayerActivation'),
            (1, 'optional'),
        ))

    ScenFlags1 = Flags(0L,Flags.getNames(
            (0, 'beginonQuestStart'),
            (1, 'stoponQuestEnd'),
            (2, 'unknown3'),
            (3, 'repeatConditionsWhileTrue'),
            (4, 'interruptible'),
        ))

    melSet = MelSet(
        MelString('EDID','eid'),
        MelVmad(),
        MelUInt32('FNAM', (ScenFlags1, 'flags', 0L)),
        MelGroups('phases',
            MelNull('HNAM'),
            MelString('NAM0','name',),
            MelGroup('startConditions',
                MelConditions(),
            ),
            MelNull('NEXT'),
            MelGroup('completionConditions',
                MelConditions(),
            ),
            # The next three are all leftovers
            MelGroup('unused',
                MelBase('SCHR','schr_p'),
                MelBase('SCDA','scda_p'),
                MelBase('SCTX','sctx_p'),
                MelBase('QNAM','qnam_p'),
                MelBase('SCRO','scro_p'),
            ),
            MelNull('NEXT'),
            MelGroup('unused',
                MelBase('SCHR','schr_p'),
                MelBase('SCDA','scda_p'),
                MelBase('SCTX','sctx_p'),
                MelBase('QNAM','qnam_p'),
                MelBase('SCRO','scro_p'),
            ),
            MelUInt32('WNAM', 'editorWidth'),
            MelNull('HNAM'),
        ),
        MelGroups('actors',
            MelUInt32('ALID', 'actorID'),
            MelUInt32('LNAM', (ScenFlags2, 'scenFlags2' ,0L)),
            MelUInt32('DNAM', (ScenFlags3, 'flags3' ,0L)),
        ),
        MelGroups('actions',
            MelUInt16('ANAM', 'actionType'),
            MelString('NAM0','name',),
            MelUInt32('ALID', 'actorID',),
            MelBase('LNAM','lnam_p',),
            MelUInt32('INAM', 'index'),
            MelUInt32('FNAM', (ScenFlags5,'flags',0L)),
            MelUInt32('SNAM', 'startPhase'),
            MelUInt32('ENAM', 'endPhase'),
            MelFloat('SNAM', 'timerSeconds'),
            MelFids('PNAM','packages'),
            MelFid('DATA','topic'),
            MelUInt32('HTID', 'headtrackActorID'),
            MelFloat('DMAX', 'loopingMax'),
            MelFloat('DMIN', 'loopingMin'),
            MelUInt32('DEMO', 'emotionType'),
            MelUInt32('DEVA', 'emotionValue'),
            MelGroup('unused', # leftover
                MelBase('SCHR','schr_p'),
                MelBase('SCDA','scda_p'),
                MelBase('SCTX','sctx_p'),
                MelBase('QNAM','qnam_p'),
                MelBase('SCRO','scro_p'),
            ),
            MelNull('ANAM'),
        ),
        # The next three are all leftovers
        MelGroup('unused',
            MelBase('SCHR','schr_p'),
            MelBase('SCDA','scda_p'),
            MelBase('SCTX','sctx_p'),
            MelBase('QNAM','qnam_p'),
            MelBase('SCRO','scro_p'),
        ),
        MelNull('NEXT'),
        MelGroup('unused',
            MelBase('SCHR','schr_p'),
            MelBase('SCDA','scda_p'),
            MelBase('SCTX','sctx_p'),
            MelBase('QNAM','qnam_p'),
            MelBase('SCRO','scro_p'),
        ),
        MelFid('PNAM','quest',),
        MelUInt32('INAM', 'lastActionIndex'),
        MelBase('VNAM','vnam_p'),
        MelConditions(),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreScrl(MelRecord,MreHasEffects):
    """Scroll."""
    classType = 'SCRL'

    ScrollDataFlags = Flags(0L,Flags.getNames(
        (0,'manualCostCalc'),
        (1,'unknown2'),
        (2,'unknown3'),
        (3,'unknown4'),
        (4,'unknown5'),
        (5,'unknown6'),
        (6,'unknown7'),
        (7,'unknown8'),
        (8,'unknown9'),
        (9,'unknown10'),
        (10,'unknown11'),
        (11,'unknown12'),
        (12,'unknown13'),
        (13,'unknown14'),
        (14,'unknown15'),
        (15,'unknown16'),
        (16,'unknown17'),
        (17,'pcStartSpell'),
        (18,'unknown19'),
        (19,'areaEffectIgnoresLOS'),
        (20,'ignoreResistance'),
        (21,'noAbsorbReflect'),
        (22,'unknown23'),
        (23,'noDualCastModification'),
        (24,'unknown25'),
        (25,'unknown26'),
        (26,'unknown27'),
        (27,'unknown28'),
        (28,'unknown29'),
        (29,'unknown30'),
        (30,'unknown31'),
        (31,'unknown32'),
    ))

    melSet = MelSet(
        MelString('EDID','eid'),
        MelBounds(),
        MelLString('FULL','full'),
        MelKeywords(),
        MelFids('MDOB','menuDisplayObject'),
        MelFid('ETYP','equipmentType',),
        MelLString('DESC','description'),
        MelModel(),
        MelDestructible(),
        MelFid('YNAM','pickupSound',),
        MelFid('ZNAM','dropSound',),
        MelStruct('DATA','If','itemValue','itemWeight',),
        MelStruct('SPIT','IIIfIIffI','baseCost',(ScrollDataFlags,'dataFlags',0L),
                  'scrollType','chargeTime','castType','targetType',
                  'castDuration','range',(FID,'halfCostPerk'),),
        MelEffects(),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreShou(MelRecord):
    """Shout Records"""
    classType = 'SHOU'
    melSet = MelSet(
        MelString('EDID','eid'),
        MelLString('FULL','full'),
        MelFid('MDOB','menuDisplayObject'),
        MelLString('DESC','description'),
        MelGroups('wordsOfPower',
            MelStruct('SNAM','2If',(FID,'word',None),(FID,'spell',None),'recoveryTime',),
        ),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreSlgm(MelRecord):
    """Soul Gem."""
    classType = 'SLGM'

    melSet = MelSet(
        MelString('EDID','eid'),
        MelBounds(),
        MelLString('FULL','full'),
        MelModel(),
        MelString('ICON','iconPath'),
        MelString('MICO','smallIconPath'),
        MelDestructible(),
        MelFid('YNAM','pickupSound'),
        MelFid('ZNAM','dropSound'),
        MelKeywords(),
        MelStruct('DATA','If','value','weight'),
        MelUInt8('SOUL', ('soul',0)),
        MelUInt8('SLCP', ('capacity',1)),
        MelFid('NAM0','linkedTo'),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreSmbn(MelRecord):
    """Story Manager Branch Node"""
    classType = 'SMBN'

    SmbnNodeFlags = Flags(0L,Flags.getNames(
        (0,'Random'),
        (1,'noChildWarn'),
    ))

    melSet = MelSet(
        MelString('EDID','eid'),
        MelFid('PNAM','parent',),
        MelFid('SNAM','child',),
        MelConditionCounter(),
        MelConditions(),
        MelUInt32('DNAM', (SmbnNodeFlags, 'nodeFlags', 0L)),
        MelBase('XNAM','xnam_p'),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreSmen(MelRecord):
    """Story Manager Event Node."""
    classType = 'SMEN'

    SmenNodeFlags = Flags(0L,Flags.getNames(
        (0,'Random'),
        (1,'noChildWarn'),
    ))

    melSet = MelSet(
        MelString('EDID','eid'),
        MelFid('PNAM','parent',),
        MelFid('SNAM','child',),
        MelConditionCounter(),
        MelConditions(),
        MelUInt32('DNAM', (SmenNodeFlags, 'nodeFlags', 0L)),
        MelBase('XNAM','xnam_p'),
        MelString('ENAM','type'),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreSmqn(MelRecord):
    """Story Manager Quest Node."""
    classType = 'SMQN'

    # "Do all" = "Do all before repeating"
    SmqnQuestFlags = Flags(0L,Flags.getNames(
        (0,'doAll'),
        (1,'sharesEvent'),
        (2,'numQuestsToRun'),
    ))

    SmqnNodeFlags = Flags(0L,Flags.getNames(
        (0,'Random'),
        (1,'noChildWarn'),
    ))

    melSet = MelSet(
        MelString('EDID','eid'),
        MelFid('PNAM','parent',),
        MelFid('SNAM','child',),
        MelConditionCounter(),
        MelConditions(),
        MelStruct('DNAM','2H',(SmqnNodeFlags,'nodeFlags',0L),(SmqnQuestFlags,'questFlags',0L),),
        MelUInt32('XNAM', 'maxConcurrentQuests'),
        MelOptUInt32('MNAM', ('numQuestsToRun', None)),
        MelCounter(MelUInt32('QNAM', 'quest_count'), counts='quests'),
        MelGroups('quests',
            MelFid('NNAM','quest',),
            MelBase('FNAM','fnam_p'),
            MelOptFloat('RNAM', ('hoursUntilReset', None)),
        )
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreSnct(MelRecord):
    """Sound Category."""
    classType = 'SNCT'

    SoundCategoryFlags = Flags(0L,Flags.getNames(
        (0,'muteWhenSubmerged'),
        (1,'shouldAppearOnMenu'),
    ))

    melSet = MelSet(
        MelString('EDID','eid'),
        MelLString('FULL','full'),
        MelUInt32('FNAM', (SoundCategoryFlags, 'flags', 0L)),
        MelFid('PNAM','parent',),
        MelUInt16('VNAM', 'staticVolumeMultiplier'),
        MelUInt16('UNAM', 'defaultMenuValue'),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreSndr(MelRecord):
    """Sound Descriptor."""
    classType = 'SNDR'

    melSet = MelSet(
        MelString('EDID','eid'),
        MelBase('CNAM','cnam_p'),
        MelFid('GNAM','category',),
        MelFid('SNAM','altSoundFor',),
        MelGroups('sounds',
            MelString('ANAM', 'sound_file_name',),
        ),
        MelFid('ONAM','outputModel',),
        MelLString('FNAM','string'),
        MelConditions(),
        MelStruct('LNAM','sBsB',('unkSndr1',null1),'looping',
                  ('unkSndr2',null1),'rumbleSendValue',),
        MelStruct('BNAM','2b2BH','pctFrequencyShift','pctFrequencyVariance','priority',
                  'dbVariance','staticAttenuation',),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreSopm(MelRecord):
    """Sound Output Model."""
    classType = 'SOPM'

    SopmFlags = Flags(0L,Flags.getNames(
            (0, 'attenuatesWithDistance'),
            (1, 'allowsRumble'),
        ))

    melSet = MelSet(
        MelString('EDID','eid'),
        MelStruct('NAM1','B2sB',(SopmFlags,'flags',0L),'unknown1','reverbSendpct',),
        MelBase('FNAM','fnam_p'),
        MelUInt32('MNAM', 'outputType'),
        MelBase('CNAM','cnam_p'),
        MelBase('SNAM','snam_p'),
        MelStruct('ONAM', '=24B', 'ch0_l', 'ch0_r', 'ch0_c', 'ch0_lFE',
                  'ch0_rL', 'ch0_rR', 'ch0_bL', 'ch0_bR', 'ch1_l', 'ch1_r',
                  'ch1_c', 'ch1_lFE', 'ch1_rL', 'ch1_rR', 'ch1_bL', 'ch1_bR',
                  'ch2_l', 'ch2_r', 'ch2_c', 'ch2_lFE', 'ch2_rL', 'ch2_rR',
                  'ch2_bL', 'ch2_bR'),
        MelStruct('ANAM','4s2f5B','unknown2','minDistance','maxDistance',
                  'curve1','curve2','curve3','curve4','curve5',
                   dumpExtra='extraData',),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreSoun(MelRecord):
    """Sound Marker."""
    classType = 'SOUN'

    melSet = MelSet(
        MelString('EDID','eid'),
        MelBounds(),
        MelString('FNAM','soundFileUnused'), # leftover
        MelBase('SNDD','soundDataUnused'), # leftover
        MelFid('SDSC','soundDescriptor'),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreSpel(MelRecord,MreHasEffects):
    """Spell."""
    classType = 'SPEL'

    # currently not used for Skyrim needs investigated to see if TES5Edit does this
    # class SpellFlags(Flags):
    #     """For SpellFlags, immuneSilence activates bits 1 AND 3."""
    #     def __setitem__(self,index,value):
    #         setter = Flags.__setitem__
    #         setter(self,index,value)
    #         if index == 1:
    #             setter(self,3,value)

    SpelTypeFlags = Flags(0L,Flags.getNames(
        ( 0,'manualCostCalc'),
        ( 1,'unknown2'),
        ( 2,'unknown3'),
        ( 3,'unknown4'),
        ( 4,'unknown5'),
        ( 5,'unknown6'),
        ( 6,'unknown7'),
        ( 7,'unknown8'),
        ( 8,'unknown9'),
        ( 9,'unknown10'),
        (10,'unknown11'),
        (11,'unknown12'),
        (12,'unknown13'),
        (13,'unknown14'),
        (14,'unknown15'),
        (15,'unknown16'),
        (16,'unknown17'),
        (17,'pcStartSpell'),
        (18,'unknown19'),
        (19,'areaEffectIgnoresLOS'),
        (20,'ignoreResistance'),
        (21,'noAbsorbReflect'),
        (22,'unknown23'),
        (23,'noDualCastModification'),
        (24,'unknown25'),
        (25,'unknown26'),
        (26,'unknown27'),
        (27,'unknown28'),
        (28,'unknown29'),
        (29,'unknown30'),
        (30,'unknown31'),
        (31,'unknown32'),
    ))

    melSet = MelSet(
        MelString('EDID','eid'),
        MelBounds(),
        MelLString('FULL','full'),
        MelKeywords(),
        MelFid('MDOB', 'menuDisplayObject'),
        MelFid('ETYP', 'equipmentType'),
        MelLString('DESC','description'),
        MelStruct('SPIT','IIIfIIffI','cost',(SpelTypeFlags,'dataFlags',0L),
                  'scrollType','chargeTime','castType','targetType',
                  'castDuration','range',(FID,'halfCostPerk'),),
        MelEffects(),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreSpgd(MelRecord):
    """Shader Particle Geometry."""
    classType = 'SPGD'

    class MelSpgdData(MelStruct):
        _SpgdDataFlags = Flags(0L, Flags.getNames(
            (0, 'rain'),
            (1, 'snow'),
        ))

        def __init__(self):
            MelStruct.__init__(
                self, 'DATA', '=7f4If', 'gravityVelocity',
                'rotationVelocity', 'particleSizeX', 'particleSizeY',
                'centerOffsetMin', 'centerOffsetMax', 'initialRotationRange',
                'numSubtexturesX', 'numSubtexturesY',
                (self._SpgdDataFlags, 'typeFlags', 0L), ('boxSize', 0),
                ('particleDensity', 0),
            )

        def loadData(self, record, ins, sub_type, size_, readId):
            """Reads data from ins into record attribute."""
            if size_ == 40:
                # 40 Bytes for legacy data post Skyrim 1.5 DATA is always 48:
                # fffffffIIIIf
                # Type is an Enum 0 = Rain; 1 = Snow
                unpacked = ins.unpack('=7f3I', size_, readId) + (0, 0,)
                setter = record.__setattr__
                for attr,value,action in zip(self.attrs,unpacked,self.actions):
                    if action: value = action(value)
                    setter(attr,value)
                if self._debug:
                    print u' ',zip(self.attrs,unpacked)
                    if len(unpacked) != len(self.attrs):
                        print u' ',unpacked
            elif size_ != 48:
                raise ModSizeError(record.inName, readId, 48, size_, True)
            else:
                MelStruct.loadData(self, record, ins, sub_type, size_, readId)

    melSet = MelSet(
        MelString('EDID','eid'),
        MelSpgdData(),
        MelString('ICON','icon'),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreStat(MelRecord):
    """Static."""
    classType = 'STAT'

    melSet = MelSet(
        MelString('EDID', 'eid'),
        MelBounds(),
        MelModel(),
        MelStruct('DNAM', 'fI', 'maxAngle30to120', (FID, 'material'),),
        # Contains null-terminated mesh filename followed by random data
        # up to 260 bytes and repeats 4 times
        MelBase('MNAM', 'distantLOD'),
        MelBase('ENAM', 'unknownENAM'),
    )
    __slots__ = melSet.getSlotsUsed()

# MNAM Should use a custom unpacker if needed for the patcher otherwise MelBase
#------------------------------------------------------------------------------
class MreTact(MelRecord):
    """Talking Activator."""
    classType = 'TACT'

    melSet = MelSet(
        MelString('EDID','eid'),
        MelVmad(),
        MelBounds(),
        MelLString('FULL','full'),
        MelModel(),
        MelDestructible(),
        MelKeywords(),
        MelBase('PNAM','pnam_p'),
        MelOptFid('SNAM', 'soundLoop'),
        MelBase('FNAM','fnam_p'),
        MelOptFid('VNAM', 'voiceType'),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreTree(MelRecord):
    """Tree."""
    classType = 'TREE'

    melSet = MelSet(
        MelString('EDID','eid'),
        MelVmad(),
        MelBounds(),
        MelModel(),
        MelFid('PFIG','harvestIngredient'),
        MelFid('SNAM','harvestSound'),
        MelStruct('PFPC','4B','spring','summer','fall','wsinter',),
        MelLString('FULL','full'),
        MelStruct('CNAM','ff32sff','trunkFlexibility','branchFlexibility',
                  'unknown','leafAmplitude','leafFrequency',),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreTxst(MelRecord):
    """Texture Set."""
    classType = 'TXST'

    TxstTypeFlags = Flags(0L,Flags.getNames(
        (0, 'noSpecularMap'),
        (1, 'facegenTextures'),
        (2, 'hasModelSpaceNormalMap'),
    ))

    melSet = MelSet(
        MelString('EDID','eid'),
        MelBounds(),
        MelGroups('destructionData',
            MelString('TX00','difuse'),
            MelString('TX01','normalGloss'),
            MelString('TX02','enviroMaskSubSurfaceTint'),
            MelString('TX03','glowDetailMap'),
            MelString('TX04','height'),
            MelString('TX05','environment'),
            MelString('TX06','multilayer'),
            MelString('TX07','backlightMaskSpecular'),
        ),
        MelDecalData(),
        MelUInt16('DNAM', (TxstTypeFlags, 'flags', 0L)),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreVtyp(MelRecord):
    """Voice Type."""
    classType = 'VTYP'

    VtypTypeFlags = Flags(0L,Flags.getNames(
            (0, 'allowDefaultDialog'),
            (1, 'female'),
        ))

    melSet = MelSet(
        MelString('EDID','eid'),
        MelUInt8('DNAM', (VtypTypeFlags, 'flags', 0L)),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreWatr(MelRecord):
    """Water."""
    classType = 'WATR'

    WatrTypeFlags = Flags(0L,Flags.getNames(
            (0, 'causesDamage'),
        ))

    melSet = MelSet(
        MelString('EDID','eid'),
        MelLString('FULL','full'),
        MelGroups('unused',
            MelString('NNAM','noiseMap',),
        ),
        MelUInt8('ANAM', 'opacity'),
        MelUInt8('FNAM', (WatrTypeFlags, 'flags', 0L)),
        MelBase('MNAM','unused1'),
        MelFid('TNAM','material',),
        MelFid('SNAM','openSound',),
        MelFid('XNAM','spell',),
        MelFid('INAM','imageSpace',),
        MelUInt16('DATA', 'damagePerSecond'),
        MelStruct('DNAM','7f4s2f3Bs3Bs3Bs4s43f','unknown1','unknown2','unknown3',
                  'unknown4','specularPropertiesSunSpecularPower',
                  'waterPropertiesReflectivityAmount',
                  'waterPropertiesFresnelAmount',('unknown5',null4),
                  'fogPropertiesAboveWaterFogDistanceNearPlane',
                  'fogPropertiesAboveWaterFogDistanceFarPlane',
                  # Shallow Color
                  'red_sc','green_sc','blue_sc','unknown_sc',
                  # Deep Color
                  'red_dc','green_dc','blue_dc','unknown_dc',
                  # Reflection Color
                  'red_rc','green_rc','blue_rc','unknown_rc',
                  ('unknown6',null4),'unknown7','unknown8','unknown9','unknown10',
                  'displacementSimulatorStartingSize',
                  'displacementSimulatorForce','displacementSimulatorVelocity',
                  'displacementSimulatorFalloff','displacementSimulatorDampner',
                  'unknown11','noisePropertiesNoiseFalloff',
                  'noisePropertiesLayerOneWindDirection',
                  'noisePropertiesLayerTwoWindDirection',
                  'noisePropertiesLayerThreeWindDirection',
                  'noisePropertiesLayerOneWindSpeed',
                  'noisePropertiesLayerTwoWindSpeed',
                  'noisePropertiesLayerThreeWindSpeed',
                  'unknown12','unknown13','fogPropertiesAboveWaterFogAmount',
                  'unknown14','fogPropertiesUnderWaterFogAmount',
                  'fogPropertiesUnderWaterFogDistanceNearPlane',
                  'fogPropertiesUnderWaterFogDistanceFarPlane',
                  'waterPropertiesRefractionMagnitude',
                  'specularPropertiesSpecularPower',
                  'unknown15','specularPropertiesSpecularRadius',
                  'specularPropertiesSpecularBrightness',
                  'noisePropertiesLayerOneUVScale',
                  'noisePropertiesLayerTwoUVScale',
                  'noisePropertiesLayerThreeUVScale',
                  'noisePropertiesLayerOneAmplitudeScale',
                  'noisePropertiesLayerTwoAmplitudeScale',
                  'noisePropertiesLayerThreeAmplitudeScale',
                  'waterPropertiesReflectionMagnitude',
                  'specularPropertiesSunSparkleMagnitude',
                  'specularPropertiesSunSpecularMagnitude',
                  'depthPropertiesReflections','depthPropertiesRefraction',
                  'depthPropertiesNormals','depthPropertiesSpecularLighting',
                  'specularPropertiesSunSparklePower',),
        MelBase('GNAM','unused2'),
        # Linear Velocity
        MelStruct('NAM0','3f','linv_x','linv_y','linv_z',),
        # Angular Velocity
        MelStruct('NAM1','3f','andv_x','andv_y','andv_z',),
        MelString('NAM2','noiseTexture'),
        MelString('NAM3','unused3'),
        MelString('NAM4','unused4'),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreWeap(MelRecord):
    """Weapon"""
    classType = 'WEAP'

    WeapFlags3 = Flags(0L,Flags.getNames(
        (0, 'onDeath'),
    ))

    WeapFlags2 = Flags(0L,Flags.getNames(
            (0, 'playerOnly'),
            (1, 'nPCsUseAmmo'),
            (2, 'noJamAfterReloadunused'),
            (3, 'unknown4'),
            (4, 'minorCrime'),
            (5, 'rangeFixed'),
            (6, 'notUsedinNormalCombat'),
            (7, 'unknown8'),
            (8, 'don'),
            (9, 'unknown10'),
            (10, 'rumbleAlternate'),
            (11, 'unknown12'),
            (12, 'nonhostile'),
            (13, 'boundWeapon'),
        ))

    WeapFlags1 = Flags(0L,Flags.getNames(
            (0, 'ignoresNormalWeaponResistance'),
            (1, 'automaticunused'),
            (2, 'hasScopeunused'),
            (3, 'can'),
            (4, 'hideBackpackunused'),
            (5, 'embeddedWeaponunused'),
            (6, 'don'),
            (7, 'nonplayable'),
        ))

    melSet = MelSet(
        MelString('EDID','eid'),
        MelVmad(),
        MelBounds(),
        MelLString('FULL','full'),
        MelModel('model1','MODL'),
        MelString('ICON','iconPath'),
        MelString('MICO','smallIconPath'),
        MelFid('EITM','enchantment',),
        MelOptUInt16('EAMT', 'enchantPoints'),
        MelDestructible(),
        MelFid('ETYP','equipmentType',),
        MelFid('BIDS','blockBashImpactDataSet',),
        MelFid('BAMT','alternateBlockMaterial',),
        MelFid('YNAM','pickupSound',),
        MelFid('ZNAM','dropSound',),
        MelKeywords(),
        MelLString('DESC','description'),
        MelModel('model2','MOD3'),
        MelBase('NNAM','unused1'),
        MelFid('INAM','impactDataSet',),
        MelFid('WNAM','firstPersonModelObject',),
        MelFid('SNAM','attackSound',),
        MelFid('XNAM','attackSound2D',),
        MelFid('NAM7','attackLoopSound',),
        MelFid('TNAM','attackFailSound',),
        MelFid('UNAM','idleSound',),
        MelFid('NAM9','equipSound',),
        MelFid('NAM8','unequipSound',),
        MelStruct('DATA','IfH','value','weight','damage',),
        MelStruct('DNAM','B3s2fH2sf4s4B2f2I5f12si8si4sf','animationType',
                  ('dnamUnk1',null3),'speed','reach',
                  (WeapFlags1,'dnamFlags1',None),('dnamUnk2',null2),'sightFOV',
                  ('dnamUnk3',null4),'baseVATSToHitChance','attackAnimation',
                  'numProjectiles','embeddedWeaponAVunused','minRange',
                  'maxRange','onHit',(WeapFlags2,'dnamFlags2',None),
                  'animationAttackMultiplier',('dnamUnk4',0.0),
                  'rumbleLeftMotorStrength','rumbleRightMotorStrength',
                  'rumbleDuration',('dnamUnk5',null4+null4+null4),'skill',
                  ('dnamUnk6',null4+null4),'resist',('dnamUnk7',null4),'stagger',),
        MelStruct('CRDT','H2sfB3sI','critDamage',('crdtUnk1',null2),'criticalMultiplier',
                  (WeapFlags3,'criticalFlags',0L),('crdtUnk2',null3),(FID,'criticalEffect',None),),
        MelUInt32('VNAM', 'detectionSoundLevel'),
        MelFid('CNAM','template',),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreWoop(MelRecord):
    """Word of Power."""
    classType = 'WOOP'

    melSet = MelSet(
        MelString('EDID','eid'),
        MelLString('FULL','full'),
        MelLString('TNAM','translation'),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
class MreWrld(MelRecord):
    """Worldspace."""
    classType = 'WRLD'

    WrldFlags2 = Flags(0L,Flags.getNames(
            (0, 'smallWorld'),
            (1, 'noFastTravel'),
            (2, 'unknown3'),
            (3, 'noLODWater'),
            (4, 'noLandscape'),
            (5, 'unknown6'),
            (6, 'fixedDimensions'),
            (7, 'noGrass'),
        ))

    WrldFlags1 = Flags(0L,Flags.getNames(
            (0, 'useLandData'),
            (1, 'useLODData'),
            (2, 'don'),
            (3, 'useWaterData'),
            (4, 'useClimateData'),
            (5, 'useImageSpaceDataunused'),
            (6, 'useSkyCell'),
        ))

    class MelWrldMnam(MelOptStruct):
        """Handle older truncated MNAM for WRLD subrecord."""
        def loadData(self, record, ins, sub_type, size_, readId):
            if size_ == 28:
                MelStruct.loadData(self, record, ins, sub_type, size_, readId)
                return
            elif size_ == 24:
                unpacked = ins.unpack('2i4h2f', size_, readId)
            elif size_ == 16:
                unpacked = ins.unpack('2i4h', size_, readId)
            else:
                raise ModSizeError(record.inName, readId, 28, size_, True)
            unpacked += self.defaults[len(unpacked):]
            setter = record.__setattr__
            for attr,value,action in zip(self.attrs,unpacked,self.actions):
                if callable(action): value = action(value)
                setter(attr,value)
            if self._debug: print unpacked, record.flags.getTrueAttrs()

    melSet = MelSet(
        MelString('EDID','eid'),
        MelGroups('unusedRNAM', # leftover
            MelBase('RNAM','unknown',),
        ),
        MelBase('MHDT','maxHeightData'),
        MelLString('FULL','full'),
        # Fixed Dimensions Center Cell
        MelOptStruct('WCTR','2h',('fixedX', 0),('fixedY', 0),),
        MelFid('LTMP','interiorLighting',),
        MelFid('XEZN','encounterZone',),
        MelFid('XLCN','location',),
        MelGroup('parent',
            MelFid('WNAM','worldspace',),
            MelStruct('PNAM','Bs',(WrldFlags1,'parentFlags',0L),'unknown',),
        ),
        MelFid('CNAM','climate',),
        MelFid('NAM2','water',),
        MelFid('NAM3','lODWaterType',),
        MelOptFloat('NAM4', ('lODWaterHeight', 0.0)),
        MelOptStruct('DNAM','2f',('defaultLandHeight', 0.0),
                     ('defaultWaterHeight', 0.0),),
        MelString('ICON','mapImage'),
        MelModel('cloudModel','MODL',),
        MelWrldMnam('MNAM','2i4h3f','usableDimensionsX','usableDimensionsY',
                  'cellCoordinatesX','cellCoordinatesY','seCellX','seCellY',
                  'cameraDataMinHeight','cameraDataMaxHeight',
                  'cameraDataInitialPitch',),
        MelStruct('ONAM','4f','worldMapScale','cellXOffset','cellYOffset',
                  'cellZOffset',),
        MelFloat('NAMA', 'distantLODMultiplier'),
        MelUInt8('DATA', (WrldFlags2, 'dataFlags', 0L)),
        # {>>> Object Bounds doesn't show up in CK <<<}
        MelStruct('NAM0','2f','minObjX','minObjY',),
        MelStruct('NAM9','2f','maxObjX','maxObjY',),
        MelFid('ZNAM','music',),
        MelString('NNAM','canopyShadowunused'),
        MelString('XNAM','waterNoiseTexture'),
        MelString('TNAM','hDLODDiffuseTexture'),
        MelString('UNAM','hDLODNormalTexture'),
        MelString('XWEM','waterEnvironmentMapunused'),
        MelBase('OFST','unknown'),
    )
    __slots__ = melSet.getSlotsUsed()

#------------------------------------------------------------------------------
# Many Things Marked MelBase that need updated
class MreWthr(MelRecord):
    """Weather"""
    classType = 'WTHR'

    WthrFlags2 = Flags(0L,Flags.getNames(
            (0, 'layer_0'),
            (1, 'layer_1'),
            (2, 'layer_2'),
            (3, 'layer_3'),
            (4, 'layer_4'),
            (5, 'layer_5'),
            (6, 'layer_6'),
            (7, 'layer_7'),
            (8, 'layer_8'),
            (9, 'layer_9'),
            (10, 'layer_10'),
            (11, 'layer_11'),
            (12, 'layer_12'),
            (13, 'layer_13'),
            (14, 'layer_14'),
            (15, 'layer_15'),
            (16, 'layer_16'),
            (17, 'layer_17'),
            (18, 'layer_18'),
            (19, 'layer_19'),
            (20, 'layer_20'),
            (21, 'layer_21'),
            (22, 'layer_22'),
            (23, 'layer_23'),
            (24, 'layer_24'),
            (25, 'layer_25'),
            (26, 'layer_26'),
            (27, 'layer_27'),
            (28, 'layer_28'),
            (29, 'layer_29'),
            (30, 'layer_30'),
            (31, 'layer_31'),
        ))

    WthrFlags1 = Flags(0L,Flags.getNames(
            (0, 'weatherPleasant'),
            (1, 'weatherCloudy'),
            (2, 'weatherRainy'),
            (3, 'weatherSnow'),
            (4, 'skyStaticsAlwaysVisible'),
            (5, 'skyStaticsFollowsSunPosition'),
        ))

    class MelWthrDalc(MelStructs):
        """Handle older truncated DALC for WTHR subrecord."""
        def loadData(self, record, ins, sub_type, size_, readId):
            if size_ == 32:
                MelStructs.loadData(self, record, ins, sub_type, size_, readId)
                return
            elif size_ == 24:
                unpacked = ins.unpack('=4B4B4B4B4B4B', size_, readId)
            else:
                raise ModSizeError(record.inName, readId, 32, size_, True)
            unpacked += self.defaults[len(unpacked):]
            target = MelObject()
            record.__getattribute__(self.attr).append(target)
            target.__slots__ = self.attrs
            setter = target.__setattr__
            for attr,value,action in zip(self.attrs,unpacked,self.actions):
                if callable(action): value = action(value)
                setter(attr,value)
            if self._debug: print unpacked

    melSet = MelSet(
        MelString('EDID','eid'),
        MelString('\x300TX','cloudTextureLayer_0'),
        MelString('\x310TX','cloudTextureLayer_1'),
        MelString('\x320TX','cloudTextureLayer_2'),
        MelString('\x330TX','cloudTextureLayer_3'),
        MelString('\x340TX','cloudTextureLayer_4'),
        MelString('\x350TX','cloudTextureLayer_5'),
        MelString('\x360TX','cloudTextureLayer_6'),
        MelString('\x370TX','cloudTextureLayer_7'),
        MelString('\x380TX','cloudTextureLayer_8'),
        MelString('\x390TX','cloudTextureLayer_9'),
        MelString('\x3A0TX','cloudTextureLayer_10'),
        MelString('\x3B0TX','cloudTextureLayer_11'),
        MelString('\x3C0TX','cloudTextureLayer_12'),
        MelString('\x3D0TX','cloudTextureLayer_13'),
        MelString('\x3E0TX','cloudTextureLayer_14'),
        MelString('\x3F0TX','cloudTextureLayer_15'),
        MelString('\x400TX','cloudTextureLayer_16'),
        MelString('A0TX','cloudTextureLayer_17'),
        MelString('B0TX','cloudTextureLayer_18'),
        MelString('C0TX','cloudTextureLayer_19'),
        MelString('D0TX','cloudTextureLayer_20'),
        MelString('E0TX','cloudTextureLayer_21'),
        MelString('F0TX','cloudTextureLayer_22'),
        MelString('G0TX','cloudTextureLayer_23'),
        MelString('H0TX','cloudTextureLayer_24'),
        MelString('I0TX','cloudTextureLayer_25'),
        MelString('J0TX','cloudTextureLayer_26'),
        MelString('K0TX','cloudTextureLayer_27'),
        MelString('L0TX','cloudTextureLayer_28'),
        MelBase('DNAM','dnam_p'),
        MelBase('CNAM','cnam_p'),
        MelBase('ANAM','anam_p'),
        MelBase('BNAM','bnam_p'),
        MelBase('LNAM','lnam_p'),
        MelFid('MNAM','precipitationType',),
        MelFid('NNAM','visualEffect',),
        MelBase('ONAM','onam_p'),
        MelBase('RNAM','cloudSpeedY'),
        MelBase('QNAM','cloudSpeedX'),
        MelStructA('PNAM','3Bs3Bs3Bs3Bs','cloudColors',
            'riseRedPnam','riseGreenPnam','riseBluePnam',('unused1',null1),
            'dayRedPnam','dayGreenPnam','dayBluePnam',('unused2',null1),
            'setRedPnam','setGreenPnam','setBluePnam',('unused3Pnam',null1),
            'nightRedPnam','nightGreenPnam','nightBluePnam',('unused4',null1),
            ),
        MelStructA('JNAM','4f','cloudAlphas','sunAlpha','dayAlpha','setAlpha','nightAlpha',),
        MelStructA('NAM0','3Bs3Bs3Bs3Bs','daytimeColors',
            'riseRed','riseGreen','riseBlue',('unused5',null1),
            'dayRed','dayGreen','dayBlue',('unused6',null1),
            'setRed','setGreen','setBlue',('unused7',null1),
            'nightRed','nightGreen','nightBlue',('unused8',null1),
            ),
        MelStruct('FNAM','8f','dayNear','dayFar','nightNear','nightFar',
                  'dayPower','nightPower','dayMax','nightMax',),
        MelStruct('DATA','B2s16B','windSpeed',('unknown',null2),'transDelta',
                  'sunGlare','sunDamage','precipitationBeginFadeIn',
                  'precipitationEndFadeOut','thunderLightningBeginFadeIn',
                  'thunderLightningEndFadeOut','thunderLightningFrequency',
                  (WthrFlags1,'wthrFlags1',0L),'red','green','blue',
                  'visualEffectBegin','visualEffectEnd',
                  'windDirection','windDirectionRange',),
        MelUInt32('NAM1', (WthrFlags2, 'wthrFlags2', 0L)),
        MelStructs('SNAM','2I','sounds',(FID,'sound'),'type'),
        MelFids('TNAM','skyStatics',),
        MelStruct('IMSP','4I',(FID,'imageSpacesSunrise'),(FID,'imageSpacesDay'),
                  (FID,'imageSpacesSunset'),(FID,'imageSpacesNight'),),
        MelWthrDalc('DALC','=4B4B4B4B4B4B4Bf','wthrAmbientColors',
            'redXplus','greenXplus','blueXplus','unknownXplus',
            'redXminus','greenXminus','blueXminus','unknownXminus',
            'redYplus','greenYplus','blueYplus','unknownYplus',
            'redYminus','greenYminus','blueYminus','unknownYminus',
            'redZplus','greenZplus','blueZplus','unknownZplus',
            'redZminus','greenZminus','blueZminus','unknownZminus',
            'redSpec','greenSpec','blueSpec','unknownSpec',
            'fresnelPower',
            ),
        MelBase('NAM2','nam2_p'),
        MelBase('NAM3','nam3_p'),
        MelModel('aurora','MODL'),
    )
    __slots__ = melSet.getSlotsUsed()

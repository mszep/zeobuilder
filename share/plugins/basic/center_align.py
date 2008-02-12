# Zeobuilder is an extensible GUI-toolkit for molecular model construction.
# Copyright (C) 2007 Toon Verstraelen <Toon.Verstraelen@UGent.be>
#
# This file is part of Zeobuilder.
#
# Zeobuilder is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# Zeobuilder is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>
#
# Contact information:
#
# Supervisors
#
# Prof. Dr. Michel Waroquier and Prof. Dr. Ir. Veronique Van Speybroeck
#
# Center for Molecular Modeling
# Ghent University
# Proeftuinstraat 86, B-9000 GENT - BELGIUM
# Tel: +32 9 264 65 59
# Fax: +32 9 264 65 60
# Email: Michel.Waroquier@UGent.be
# Email: Veronique.VanSpeybroeck@UGent.be
#
# Author
#
# Ir. Toon Verstraelen
# Center for Molecular Modeling
# Ghent University
# Proeftuinstraat 86, B-9000 GENT - BELGIUM
# Tel: +32 9 264 65 56
# Email: Toon.Verstraelen@UGent.be
#
# --


from zeobuilder import context
from zeobuilder.actions.composed import Immediate
from zeobuilder.actions.abstract import CenterAlignBase
from zeobuilder.actions.collections.menu import MenuInfo
from zeobuilder.nodes.parent_mixin import ContainerMixin
from zeobuilder.nodes.glmixin import GLTransformationMixin
from zeobuilder.nodes.analysis import calculate_center
import zeobuilder.actions.primitive as primitive
import zeobuilder.authors as authors

from molmod.transformations import Translation, Rotation, Complete

import numpy

import copy, math


class DefineOrigin(CenterAlignBase):
    description = "Define origin"
    menu_info = MenuInfo("default/_Object:tools/_Transform:center", "_Define origin", order=(0, 4, 1, 2, 2, 0))
    authors = [authors.toon_verstraelen]

    @staticmethod
    def analyze_selection():
        # A) calling ancestor
        if not CenterAlignBase.analyze_selection(): return False
        # B) validating
        cache = context.application.cache
        node = cache.node
        if not isinstance(node, GLTransformationMixin): return False
        if not isinstance(node.transformation, Translation): return False
        if cache.some_neighbours_fixed: return False
        # C) passed all tests:
        return True

    def do(self):
        cache = context.application.cache
        translation = Translation()
        translation.t = copy.deepcopy(cache.node.transformation.t)
        CenterAlignBase.do(self, cache.parent, cache.translated_neighbours, translation)


class Align(CenterAlignBase):
    description = "Align to parent"
    menu_info = MenuInfo("default/_Object:tools/_Transform:align", "_Align", order=(0, 4, 1, 2, 3, 0))
    authors = [authors.toon_verstraelen]

    @staticmethod
    def analyze_selection():
        # A) calling ancestor
        if not CenterAlignBase.analyze_selection(): return False
        # B) validating
        cache = context.application.cache
        node = cache.node
        if not isinstance(node, GLTransformationMixin): return False
        if not isinstance(node.transformation, Rotation): return False
        if cache.some_neighbours_fixed: return False
        # C) passed all tests:
        return True

    def do(self):
        cache = context.application.cache
        rotation = Rotation()
        rotation.r = copy.deepcopy(cache.node.transformation.r)
        CenterAlignBase.do(self, cache.parent, cache.transformed_neighbours, rotation)


class DefineOriginAndAlign(CenterAlignBase):
    description = "Define as origin and align to parent"
    menu_info = MenuInfo("default/_Object:tools/_Transform:centeralign", "De_fine origin and align", order=(0, 4, 1, 2, 4, 0))
    authors = [authors.toon_verstraelen]

    @staticmethod
    def analyze_selection():
        # A) calling ancestor
        if not CenterAlignBase.analyze_selection(): return False
        # B) validating
        cache = context.application.cache
        node = cache.node
        if not isinstance(node, GLTransformationMixin): return False
        if not isinstance(node.transformation, Complete): return False
        if cache.some_neighbours_fixed: return False
        # C) passed all tests:
        return True

    def do(self):
        cache = context.application.cache
        CenterAlignBase.do(self, cache.parent, cache.transformed_neighbours, copy.deepcopy(cache.node.transformation))


class CenterToChildren(CenterAlignBase):
    description = "Center to children"
    menu_info = MenuInfo("default/_Object:tools/_Transform:center", "Center to c_hildren", order=(0, 4, 1, 2, 2, 1))
    authors = [authors.toon_verstraelen]

    @staticmethod
    def analyze_selection():
        # A) calling ancestor
        if not CenterAlignBase.analyze_selection(): return False
        # B) validating
        cache = context.application.cache
        if not isinstance(cache.node, ContainerMixin): return False
        if len(cache.translated_children) == 0: return False
        if cache.some_children_fixed: return False
        # C) passed all tests:
        return True

    def do(self):
        cache = context.application.cache
        translation = Translation()
        translation.t = calculate_center(cache.child_translations)
        CenterAlignBase.do(self, cache.node, cache.translated_children, translation)


class AlignUnitCell(Immediate):
    description = "Align unit cell"
    menu_info = MenuInfo("default/_Object:tools/_Transform:align", "_Align unit cell", order=(0, 4, 1, 2, 3, 1))
    authors = [authors.toon_verstraelen]

    @staticmethod
    def analyze_selection():
        # A) calling ancestors
        if not Immediate.analyze_selection(): return False
        # B) validating
        node = context.application.cache.node
        Universe = context.application.plugins.get_node("Universe")
        if not isinstance(node, Universe): return False
        if node.cell_active.sum() == 0: return False
        # C) passed all tests:
        return True

    def do(self):
        universe = context.application.cache.node
        # first make sure the cell is right handed
        if numpy.linalg.det(universe.cell) < 0 and universe.cell_active.sum() == 3:
            new_cell = universe.cell.copy()
            temp = new_cell[:,0].copy()
            new_cell[:,0] = new_cell[:,1]
            new_cell[:,1] = temp
            primitive.SetProperty(universe, "cell", new_cell)

        # then rotate the unit cell box to the normalized frame:
        rotation = Rotation()
        rotation.r = numpy.array(universe.calc_align_rotation_matrix())
        new_cell = numpy.dot(rotation.r, universe.cell)
        old_cell_active = universe.cell_active.copy()
        universe.cell_active = numpy.array([False, False, False])
        primitive.SetProperty(universe, "cell", new_cell)
        for child in context.application.cache.transformed_children:
            primitive.Transform(child, rotation)
        universe.cell_active = old_cell_active
        primitive.SetProperty(universe, "cell", new_cell)


actions = {
    "DefineOrigin": DefineOrigin,
    "Align": Align,
    "DefineOriginAndAlign": DefineOriginAndAlign,
    "CenterToChildren": CenterToChildren,
    "AlignUnitCell": AlignUnitCell,
}




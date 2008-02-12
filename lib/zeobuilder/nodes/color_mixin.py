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
from zeobuilder.nodes.meta import NodeClass, Property
from zeobuilder.gui.fields_dialogs import DialogFieldInfo
from zeobuilder.undefined import Undefined
import zeobuilder.gui.fields as fields

import numpy, gobject


__all__ = ["ColorMixin", "UserColorMixin"]


class ColorMixin(gobject.GObject):

    __metaclass__ = NodeClass

    #
    # Properties
    #

    def set_color(self, color):
        self.color = color
        self.invalidate_draw_list()

    properties = [
        Property("color", numpy.array([0.7, 0.7, 0.7, 1.0]), lambda self: self.color, set_color)
    ]

    #
    # Dialog fields (see action EditProperties)
    #

    dialog_fields = set([
        DialogFieldInfo("Markup", (1, 0), fields.edit.Color(
            label_text="Color",
            attribute_name="color",
        ))
    ])

    #
    # Draw
    #

    def draw(self):
        context.application.vis_backend.set_color(*self.color)


class UserColorMixin(gobject.GObject):

    __metaclass__ = NodeClass

    #
    # Properties
    #

    def set_user_color(self, user_color):
        self.user_color = user_color
        self.invalidate_draw_list()

    properties = [
        Property("user_color", Undefined(numpy.array([0.7, 0.7, 0.7, 1.0])), lambda self: self.user_color, set_user_color, signal=True)
    ]

    #
    # Dialog fields (see action EditProperties)
    #

    dialog_fields = set([
        DialogFieldInfo("Markup", (1, 7), fields.optional.CheckOptional(
            fields.edit.Color(
                label_text="User defined color",
                attribute_name="user_color",
            )
        )),
    ])

    #
    # Draw
    #

    def get_color(self):
        if isinstance(self.user_color, Undefined):
            return self.default_color
        else:
            return self.user_color

    def draw(self):
        context.application.vis_backend.set_color(*self.get_color())



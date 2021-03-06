# -*- coding: utf-8 -*-
# Zeobuilder is an extensible GUI-toolkit for molecular model construction.
# Copyright (C) 2007 - 2012 Toon Verstraelen <Toon.Verstraelen@UGent.be>, Center
# for Molecular Modeling (CMM), Ghent University, Ghent, Belgium; all rights
# reserved unless otherwise stated.
#
# This file is part of Zeobuilder.
#
# Zeobuilder is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# In addition to the regulations of the GNU General Public License,
# publications and communications based in parts on this program or on
# parts of this program are required to cite the following article:
#
# "ZEOBUILDER: a GUI toolkit for the construction of complex molecules on the
# nanoscale with building blocks", Toon Verstraelen, Veronique Van Speybroeck
# and Michel Waroquier, Journal of Chemical Information and Modeling, Vol. 48
# (7), 1530-1541, 2008
# DOI:10.1021/ci8000748
#
# Zeobuilder is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>
#
#--


from zeobuilder import context
from zeobuilder.actions.composed import Immediate, UserError
from zeobuilder.actions.collections.menu import MenuInfo
from zeobuilder.nodes.parent_mixin import ContainerMixin
from zeobuilder.nodes.glcontainermixin import GLContainerMixin
import zeobuilder.authors as authors
import zeobuilder.actions.primitive as primitive

import gtk


class CoordinationDialog(object):
    def __init__(self, coordinated_tetra):
        total = sum([len(tetras) for tetras in coordinated_tetra])
        # create the dialog window
        self.dialog = gtk.Dialog("T-atom Coordination", None, gtk.DIALOG_MODAL, (gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE))
        #self.dialog.connect("response", self.on_dialog_response)
        self.dialog.set_resizable(False)
        # create the table
        table = gtk.Table(rows=7, columns=4)
        table.set_border_width(10)
        table.set_col_spacings(5)
        table.set_row_spacings(5)
        # add the table heading
        for index, label in enumerate(["Type", "Count", "%"]):
            label = gtk.Label("<b>%s</b>" % label)
            label.set_alignment(1, 0.5)
            label.set_use_markup(True)
            label.set_size_request(70, -1)
            table.attach(label, index, index+1, 0, 1, xoptions=gtk.FILL | gtk.EXPAND, yoptions=gtk.FILL)
        table.attach(gtk.HSeparator(), 0, 4, 1, 2, xoptions=gtk.FILL, yoptions=gtk.FILL)
        # add the rows
        for row, tetras in enumerate(coordinated_tetra):
            coordination = gtk.Label("Q%s" % row)
            coordination.set_alignment(1, 0.5)
            table.attach(coordination, 0, 1, row+2, row+3, xoptions=gtk.FILL, yoptions=gtk.FILL)
            count = gtk.Label("%s" % len(tetras))
            count.set_alignment(1, 0.5)
            table.attach(count, 1, 2, row+2, row+3, xoptions=gtk.FILL, yoptions=gtk.FILL)
            percentage = gtk.Label("%.2f" % (100*float(len(tetras)) / total))
            percentage.set_alignment(1, 0.5)
            table.attach(percentage, 2, 3, row+2, row+3, xoptions=gtk.FILL, yoptions=gtk.FILL)
            select = gtk.Button("Select")
            select.connect("clicked", self.on_select_clicked, row)
            select.set_sensitive(len(tetras) > 0)
            table.attach(select, 3, 4, row+2, row+3, xoptions=gtk.FILL, yoptions=gtk.FILL)
        # add the table to the dialog
        self.dialog.vbox.pack_start(table)

    def run(self):
        self.dialog.set_transient_for(context.parent_window)
        self.dialog.show_all()
        result = self.dialog.run()
        self.dialog.hide()
        return result

    def on_select_clicked(self, button, response_id):
        self.dialog.response(response_id)



class TetraCoordination(Immediate):
    description = "T-atom coordination"
    menu_info = MenuInfo("default/_Object:tools/_Molecular:info", "_T-atom coordination", order=(0, 4, 1, 5, 2, 1))
    authors = [authors.toon_verstraelen]

    @staticmethod
    def analyze_selection():
        # A) calling ancestor
        if not Immediate.analyze_selection(): return False
        # B) validating
        if len(context.application.cache.nodes) == 0: return False
        # C) passed all tests:
        return True

    def do(self):
        Atom = context.application.plugins.get_node("Atom")

        def iter_all_tetra(nodes):
            for node in nodes:
                if isinstance(node, Atom) and node.number > 12:
                    yield node
                elif isinstance(node, ContainerMixin):
                    for tetra in iter_all_tetra(node.children):
                        yield tetra

        coordinated_tetra = [[] for i in xrange(5)]
        for tetra in iter_all_tetra(context.application.cache.nodes_without_children):
            coordination = 0
            for bridging in tetra.iter_neighbors():
                if bridging.number > 6:
                    num_t = len([t for t in bridging.iter_neighbors() if t.number > 12])
                    if num_t > 2:
                        raise UserError("Invalid zeolite structure.")
                    if num_t == 2:
                        coordination += 1
            if coordination > 4:
                raise UserError("Invalid zeolite structure.")
            coordinated_tetra[coordination].append(tetra)

        result_dialog = CoordinationDialog(coordinated_tetra)
        response = result_dialog.run()

        if response != gtk.RESPONSE_CLOSE:
            main = context.application.main
            main.select_nodes(coordinated_tetra[response])


class AddZeoliteTetraeders(Immediate):
    description = "Add zeolite tetraeders"
    menu_info = MenuInfo("default/_Object:tools/_Molecular:add", "_Add zeolite tetraeders", image_name="plugins/basic/tetra.svg", order=(0, 4, 1, 5, 1, 4))
    authors = [authors.toon_verstraelen]

    @staticmethod
    def analyze_selection():
        # A) calling ancestor
        if not Immediate.analyze_selection(): return False
        # B) validating
        if len(context.application.cache.nodes) == 0: return False
        # C) passed all tests:
        return True

    def do(self):
        Atom = context.application.plugins.get_node("Atom")
        Tetraeder = context.application.plugins.get_node("Tetraeder")

        def iter_all_tetra(nodes):
            for node in nodes:
                if isinstance(node, Atom) and node.num_bonds() == 4:
                    yield node
                elif isinstance(node, ContainerMixin):
                    for tetra in iter_all_tetra(node.children):
                        yield tetra

        cache = context.application.cache
        if isinstance(cache.node, GLContainerMixin):
            parent = cache.node
        else:
            parent = cache.common_parent
            if parent is None:
                parent = context.application.model.universe
        for tetra in iter_all_tetra(cache.nodes_without_children):
            primitive.Add(
                Tetraeder(targets=list(tetra.iter_neighbors()), color=tetra.get_color()),
                parent,
            )


actions = {
    "TetraCoordination": TetraCoordination,
    "AddZeoliteTetraeders": AddZeoliteTetraeders,
}



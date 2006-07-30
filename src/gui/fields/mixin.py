# Zeobuilder is an extensible GUI-toolkit for molecular model construction.
# Copyright (C) 2005 Toon Verstraelen
#
# This file is part of Zeobuilder.
#
# Zeobuilder is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# --


from zeobuilder import context

import gtk


__all__ = [
    "ReadMixin", "EditMixin", "InvalidField", "FaultyMixin",
    "SpecialState", "ambiguous", "insensitive"
]


changed_indicator = "<span foreground=\"red\">*</span>"


class SpecialState(object):
    pass


class Ambiguous(SpecialState):
    def __str__(self):
        return ":::ambiguous:::"

ambiguous = Ambiguous()


class Insensitive(SpecialState):
    def __str__(self):
        return ":::insensitive:::"

insensitive = Insensitive()


class Attribute(object):
    def __get__(self, owner, ownertype):
        if owner.attribute_name is None:
            return owner.current_instance
        else:
            return owner.current_instance.__dict__[owner.attribute_name]

    def __set__(self, owner, value):
        if owner.attribute_name is None:
            raise AttributeError("Can not assign to an attribute when no attribute_name is given.")
        else:
            owner.current_instance.__dict__[owner.attribute_name] = value


class ReadMixin(object):
    attribute = Attribute()
    reset_representation = None

    def __init__(self, attribute_name=None):
        self.attribute_name = attribute_name

    def get_widgets_separate(self):
        assert self.data_widget is not None
        return self.label, self.data_widget, None

    def applicable(self, instance):
        if (self.attribute_name is not None) and (self.attribute_name not in instance.__dict__):
            #print "The attribute_name '%s' is not in the instance dictionary: %s." % (self.attribute_name, instance.__dict__)
            return False
        else:
            self.current_instance = instance
            if self.attribute is None:
                #print "The attribute corresponding to the attribute_name '%s' is None." % self.attribute_name
                result = True
            else:
                result = self.applicable_attribute()
                #print "The field-specific code for attribute_name '%s' said %s." % (self.attribute_name, result)
            del self.current_instance
            return result

    def applicable_attribute(self):
        return True

    def read(self):
        if self.get_active():
            self.write_to_widget(self.convert_to_representation_wrap(self.read_from_instance(self.instance)), True)

    def read_multiplex(self):
        if self.get_active():
            common = self.convert_to_representation_wrap(self.read_from_instance(self.instances[0]))
            for instance in self.instances[1:]:
                if common != self.convert_to_representation_wrap(self.read_from_instance(instance)):
                    self.set_ambiguous_capability(True)
                    self.write_to_widget(ambiguous, True)
                    return
            self.set_ambiguous_capability(False)
            self.write_to_widget(common, True)

    def write(self):
        pass

    def write_multiplex(self):
        pass

    def check(self):
        pass

    def set_ambiguous_capability(self, ambiguous):
        pass

    def changed_names(self):
        return []

    def read_from_instance(self, instance):
        self.current_instance = instance
        if self.attribute is None: return None
        result = self.read_from_attribute()
        del self.current_instance
        return result

    def read_from_attribute(self):
        return self.attribute

    def convert_to_representation_wrap(self, value):
        if value is None:
            return insensitive
        else:
            return self.convert_to_representation(value)

    def convert_to_representation(self, value):
        return value

    def write_to_widget(self, representation, original=False):
        raise NotImplementedError


class EditMixin(ReadMixin):
    Popup = None

    def __init__(self, attribute_name=None, show_popup=True, history_name=None):
        ReadMixin.__init__(self, attribute_name)
        self.show_popup = show_popup
        self.history_name = history_name

        self.original = None
        self.bu_popup = None
        self.popup = None

    def create_widgets(self):
        if (self.show_popup) and (self.Popup is not None):
            self.bu_popup = gtk.Button()
            self.bu_popup.set_property("can_focus", False)
            image = gtk.Image()
            image.set_from_stock(gtk.STOCK_INDEX, gtk.ICON_SIZE_MENU)
            self.bu_popup.add(image)
            self.bu_popup.connect("button_release_event", self.do_popup)
            self.popup = self.Popup(self)

    def destroy_widgets(self):
        if self.bu_popup is not None:
            self.bu_popup.destroy()
            self.bu_popup = None
            self.popup = None

    def get_widgets_separate(self):
        assert self.data_widget is not None
        return self.label, self.data_widget, self.bu_popup

    def do_popup(self, bu_popup, event):
        self.popup.do_popup(bu_popup, event.button, event.time)

    def write(self):
        if self.get_active() and self.changed():
            representation = self.read_from_widget()
            self.write_to_instance(self.convert_to_value_wrap(representation), self.instance)
            if self.history_name is not None:
                context.application.configuration.add_to_history(self.history_name, representation)

    def write_multiplex(self):
        if self.get_active() and self.changed():
            representation = self.read_from_widget()
            for instance in self.instances:
                self.write_to_instance(self.convert_to_value_wrap(representation), instance)

    def changed_names(self):
        if self.get_active() and self.changed():
            return [self.attribute_name]
        else:
            return []

    def write_to_widget(self, representation, original=False):
        if self.bu_popup is not None:
            self.bu_popup.set_sensitive(representation != insensitive)
        if original: self.original = representation
        self.update_label()

    def read_from_widget(self):
        # This shoud just return the values from the widgets without any
        # conversion.
        raise NotImplementedError

    def convert_to_value_wrap(self, representation):
        if representation is insensitive:
            return None
        else:
            return self.convert_to_value(representation)

    def convert_to_value(self, representation):
        # This should convert a representation in a value
        return representation

    def write_to_instance(self, value, instance):
        self.current_instance = instance
        if value is None: self.attribute = None
        self.write_to_attribute(value)
        del self.current_instance

    def write_to_attribute(self, value):
        self.attribute = value

    def changed(self):
        representation = self.read_from_widget()
        return representation != self.original and representation != ambiguous

    def on_widget_changed(self, widget):
        self.update_label()

    def update_label(self):
        if self.label is None:
            return
        if self.changed():
            #print "ON ", self.attribute_name, id(self), self.label_text
            if len(self.label.get_label()) == len(self.label_text):
                self.label.set_label(self.label_text + changed_indicator)
        else:
            #print "OFF", self.attribute_name, id(self), self.label_text
            if len(self.label.get_label()) > len(self.label_text):
                self.label.set_label(self.label_text)


class InvalidField(Exception):
    def __init__(self, field, message):
        Exception.__init__(self)
        self.field = field
        self.message = message


class FaultyMixin(EditMixin):
    def check(self):
        #print self.label_text, self.instances, self.instance, self.get_active()
        if self.get_active() and self.changed():
            try:
                self.convert_to_value_wrap(self.read_from_widget())
            except ValueError, e:
                invalid_field = InvalidField(self, str(e))
                raise invalid_field


NO_BUTTONS = 0
CHECK_BUTTONS = 1
RADIO_BUTTONS = 2

class TableMixin(object):
    def __init__(self, short=True, cols=1, buttons=NO_BUTTONS):
        self.short = short
        self.cols = cols
        self.buttons = buttons
        if not short and len(self.fields) == cols:
            self.high_widget = False
            for field in self.fields:
                if field.high_widget:
                    self.high_widget = True
                    break

    def create_widgets(self):
        fields_active = sum(field.get_active() for field in self.fields)
        rows = fields_active / self.cols + (fields_active % self.cols > 0)
        table = gtk.Table(rows, self.cols * 4)
        first_radio_button = None
        index = 0
        for field in self.fields:
            if not field.get_active():
                continue
            col = index % self.cols
            row = index / self.cols
            left = col * 4
            right = left + 4
            if self.buttons != NO_BUTTONS:
                if self.buttons == CHECK_BUTTONS:
                    toggle_button = gtk.CheckButton()
                elif self.buttons == RADIO_BUTTONS:
                    if first_radio_button is None:
                        toggle_button = gtk.RadioButton()
                        first_radio_button = toggle_button
                    else:
                        toggle_button = gtk.RadioButton(first_radio_button)
                table.attach(
                    toggle_button, left, left + 1, row, row+1,
                    xoptions=gtk.FILL, yoptions=gtk.FILL
                )
                left += 1
                field.old_representation = ambiguous
                field.sensitive_button = toggle_button
                toggle_button.connect("toggled", self.on_button_toggled, field)

            if field.high_widget:
                if self.short:
                    container = field.get_widgets_short_container()
                else:
                    container = field.get_widgets_flat_container()
                container.set_border_width(0)
                table.attach(
                    container, left, right, row, row + 1,
                    xoptions=gtk.EXPAND|gtk.FILL, yoptions=0,
                )
            else:
                label, data_widget, bu_popup = field.get_widgets_separate()
                if label is not None:
                    table.attach(
                        label, left, left + 1, row, row + 1,
                        xoptions=gtk.FILL, yoptions=0,
                    )
                    left += 1
                if bu_popup is not None:
                    table.attach(
                        bu_popup, right - 1, right, row, row + 1,
                        xoptions=0, yoptions=0,
                    )
                    right -= 1
                table.attach(
                    data_widget, left, right, row, row + 1,
                    xoptions=gtk.EXPAND|gtk.FILL, yoptions=0,
                )
            index += 1
        table.set_row_spacings(6)
        for col in xrange(self.cols * 4 - 1):
            if col % 4 == 3:
                table.set_col_spacing(col, 24)
            else:
                table.set_col_spacing(col, 6)
        self.data_widget = table

    def destroy_widgets(self):
        if self.buttons != NO_BUTTONS:
            for field in self.fields:
                if field.get_active():
                    field.sensitive_button.destroy()
                    field.sensitive_button = None

    def on_button_toggled(self, toggle_button, field):
        raise NotImplementedError

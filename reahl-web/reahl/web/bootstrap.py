# Copyright 2015 Reahl Software Services (Pty) Ltd. All rights reserved.
#-*- encoding: utf-8 -*-
#
#    This file is part of Reahl.
#
#    Reahl is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation; version 3 of the License.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Widgets and Layouts that provide an abstraction on top of Bootstrap (http://getbootstrap.com/)

.. versionadded:: 3.2

"""
from __future__ import print_function, unicode_literals, absolute_import, division

import six

from collections import OrderedDict
import copy

from reahl.web.fw import Layout, Widget
from reahl.web.ui import Form, Div, Header, Footer, Slot, HTML5Page, DerivedInputAttributes, InputStateAttributes, Span, Input, TextInput, Label, TextNode, ButtonInput, P

import reahl.web.layout
from reahl.component.exceptions import ProgrammerError, arg_checks, IsInstance



class Form(reahl.web.ui.Form):
    def get_js_options(self):
        return '''
        {
            errorElement: 'span',
            errorClass: 'help-block',
            highlight: function(element) {
                $(element).closest('.form-group').removeClass('has-success').addClass('has-error');
            },
            unhighlight: function(element) {
                $(element).closest('.form-group').removeClass('has-error').addClass('has-success');
            },
            errorPlacement: function (error, element) {
                if (element.parent('.input-group').length) {
                    error.insertAfter(element.parent());
                } else if (element.prop('type') === 'checkbox') {
                    error.insertAfter($(element).closest('.'+$(element).prop('type')));
                } else if (element.prop('type') === 'radio') {
                    error.insertAfter($(element).closest('.'+$(element).prop('type')).parent());
                } else {
                    error.insertAfter(element);
                }
            }
         }
    '''



class Container(Layout):
    def __init__(self, fluid=False):
        super(Container, self).__init__()
        self.fluid = fluid

    def customise_widget(self):
        container_class = 'container'
        if self.fluid:
            container_class = 'container-fluid'
        self.widget.append_class(container_class)



class ResponsiveSize(reahl.web.layout.ResponsiveSize):
    device_classes = ['xs', 'sm', 'md', 'lg']
    def __init__(self, xs=None, sm=None, md=None, lg=None):
        super(ResponsiveSize, self).__init__(xs=xs, sm=sm, md=md, lg=lg)
        self.offsets = {}

    def offset(self, xs=None, sm=None, md=None, lg=None):
        self.offsets = ResponsiveSize(xs=xs, sm=sm, md=md, lg=lg)
        return self

    def calculated_size_for(self, device_class):
        classes_that_impact = self.device_classes[:self.device_classes.index(device_class)+1]
        for possible_class in reversed(classes_that_impact):
            try:
                return self[possible_class]
            except KeyError:
                pass
        return 0
        
    def total_width_for(self, device_class):
        total = self.calculated_size_for(device_class)
        if self.offsets:
            total += self.offsets.calculated_size_for(device_class)
        return total
    
    @classmethod    
    def wraps_for_some_device_class(cls, sizes): 
        return any(cls.wraps_for(device_class, sizes)
                   for device_class in cls.device_classes)

    @classmethod    
    def wraps_for(cls, device_class, sizes):
        return (cls.sum_sizes_for(device_class, sizes)) > 12

    @classmethod    
    def sum_sizes_for(cls, device_class, sizes):
        total = 0
        for size in sizes:
            total += size.total_width_for(device_class)
        return total



class ColumnLayout(reahl.web.layout.ColumnLayout):
    def __init__(self, *column_definitions):
        if not all([isinstance(column_definition, tuple) for column_definition in column_definitions]):
            raise ProgrammerError('All column definitions are expected a tuple of the form (name, %s), got %s' %\
                                  (ResponsiveSize, column_definitions))
        self.added_sizes = []
        super(ColumnLayout, self).__init__(*column_definitions)

    def customise_widget(self):
        super(ColumnLayout, self).customise_widget()
        self.widget.append_class('row')
   
    def add_clearfix(self, column_size):
        clearfix = self.widget.add_child(Div(self.view))
        clearfix.append_class('clearfix')
        for device_class in column_size.device_classes:
            if ResponsiveSize.wraps_for(device_class, self.added_sizes+[column_size]):
                clearfix.append_class('visible-%s-block' % device_class)

    def add_column(self, column_size):
        if ResponsiveSize.wraps_for_some_device_class(self.added_sizes+[column_size]):
            self.add_clearfix(column_size)
            
        column = super(ColumnLayout, self).add_column(column_size)

        for device_class, value in column_size.items():
            column.append_class('col-%s-%s' % (device_class, value))
        for device_class, value in column_size.offsets.items():
            column.append_class('col-%s-offset-%s' % (device_class, value))

        self.added_sizes.append(column_size)
        return column



class DerivedTextInputAttributes(DerivedInputAttributes):

    def set_attributes(self, attributes):
        super(DerivedTextInputAttributes, self).set_attributes(attributes)
        attributes.add_to('class', ['form-control'])
        attributes.set_to('placeholder', self.input_widget.value)


class TextInput(reahl.web.ui.TextInput):
    append_error = False
    derived_input_attributes_class = DerivedTextInputAttributes


class CheckboxInput(reahl.web.ui.CheckboxInput):
    append_error = False
    type_class = 'checkbox'




from reahl.web.ui import HTMLElement, TextNode, Label, Span
class SingleRadioButton(Widget):
    def __init__(self, radio_input, form, value, label, checked=False, attribute_source=None, css_id=None):
        super(SingleRadioButton, self).__init__(form.view)

        button = self.add_child(HTMLElement(self.view, 'input', attribute_source=attribute_source))
        button.set_attribute('type', 'radio')
        button.set_attribute('value', value)
        button.set_attribute('form', form.css_id)
        if checked:
            button.set_attribute('checked', 'checked')

        self.type_class = 'radio'
        self.bound_field = radio_input.bound_field
        self.name = radio_input.name
        self.choice_value = label
    @property
    def label(self):
        return self.choice_value
    def get_input_status(self):
        return self.bound_field.input_status
    @property
    def validation_error(self):
        return self.bound_field.validation_error




class RadioButtonInput(reahl.web.ui.RadioButtonInput):
    append_error = False
    def __init__(self, form, bound_field, inline=False):
        self.inline = inline
        super(RadioButtonInput, self).__init__(form, bound_field)

    def create_main_element(self):
        return super(RadioButtonInput, self).create_main_element().use_layout(ChoicesLayout())

    def add_button_for_choice_to(self, widget, choice):
        button = SingleRadioButton(self, self.form, choice.as_input(), choice.label, checked=self.bound_field.is_selected(choice), attribute_source=self.html_input_attributes)
        widget.layout.add_choice(button)



class InputGroup(Div):
    @property
    def label(self):
        return self.bound_field.label

    @property
    def name(self):
        return self.input_widget.name

    @property
    def bound_field(self):
        return self.input_widget.bound_field

    def get_input_status(self):
        return self.bound_field.input_status

    @property
    def validation_error(self):
        return self.bound_field.validation_error

    def __init__(self, prepend, input_widget, append, css_id=None):
        super(InputGroup, self).__init__(input_widget.view, css_id=css_id)
        self.append_class('input-group')
        if prepend:
            self.add_as_addon(prepend)
        self.input_widget = self.add_child(input_widget)
        if append:
            self.add_as_addon(append)

    def add_as_addon(self, addon):
        if isinstance(addon, six.string_types):
            span = Span(self.view, text=addon)
        else:
            span = Span(self.view)
            span.add_child(addon)
        span.append_class('input-group-addon')
        return self.add_child(span)



            
            
class ChoicesLayout(Layout):
    def add_choice(self, html_input, help_text=None, inline=False):
        assert isinstance(html_input, (CheckboxInput, SingleRadioButton))
 
        label_widget = Label(self.view)
        input_type_class = html_input.type_class

        if inline:
            label_widget.append_class('%s-inline' % input_type_class)
            wrapper = label_widget
        else:
            outer_div = Div(self.view)
            outer_div.append_class(input_type_class)
            outer_div.add_child(label_widget)
            wrapper = outer_div

        label_widget.add_child(html_input)
        label_widget.add_child(TextNode(self.view, html_input.label))
 
        self.widget.add_child(wrapper)
            
        return wrapper


class FormLayout(Layout):
    def __init__(self, inline=False, horizontal=False):
        super(FormLayout, self).__init__()
        assert not (inline and horizontal), 'Cannot set both inline and horizontal'
        self.inline = inline
        self.horizontal = horizontal

    def customise_widget(self):
        if self.inline:
            self.widget.append_class('form-inline')
        elif self.horizontal:
            self.widget.append_class('form-horizontal')

    def add_input(self, html_input, render_label=None, help_text=None):
        render_label = render_label if render_label is not None else not isinstance(html_input, CheckboxInput)
        form_group = self.widget.add_child(Div(self.view))
        form_group.append_class('form-group')
        form_group.attribute_source = InputStateAttributes(html_input, 
                                                           error_class='has-error', success_class='has-success')
        if render_label:
            label = form_group.add_child(Label(self.view, text=html_input.label, for_input=html_input))
            label.append_class('control-label' if render_label else 'sr-only')

        if isinstance(html_input, CheckboxInput):
            form_group.use_layout(ChoicesLayout())
            form_group.layout.add_choice(html_input, inline=False)
        else:
            form_group.add_child(html_input)

        if html_input.get_input_status() == 'invalidly_entered':
            error_text = form_group.add_child(Span(self.view, text=html_input.validation_error.message))
            error_text.append_class('help-block')
            error_text.set_attribute('for', html_input.name)
            error_text.set_attribute('generated', 'true')

        if help_text:
            help_text = form_group.add_child(P(self.view, text=help_text))
            help_text.append_class('help-block')

        return form_group



class Button(ButtonInput):
    def __init__(self, form, event):
        super(Button, self).__init__(form, event)
        self.append_class('btn')

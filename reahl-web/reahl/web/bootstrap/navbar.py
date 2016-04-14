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

.. versionadded:: 3.2

"""
from __future__ import print_function, unicode_literals, absolute_import, division

import six

from reahl.web.fw import Layout, Widget
from reahl.web.ui import Url, HTMLElement, HTMLWidget
from reahl.web.bootstrap.ui import Div, Form, Nav, A, TextNode, ResponsiveSize
import reahl.web.bootstrap.navs
from reahl.web.bootstrap.grid import Container, DeviceClass, HTMLAttributeValueOption


class CollapseToggle(HTMLElement):
    def __init__(self, view, target_widget, text=None, hide_for_size=None):
        text = text or '☰'

        super(CollapseToggle, self).__init__(view, 'button', children_allowed=True)
        self.set_attribute('type', 'button')

        self.target_widget = target_widget
        self.append_class('navbar-toggler')
        self.set_attribute('data-toggle', 'collapse')
        self.set_attribute('data-target', '#%s' % target_widget.css_id)
        if hide_for_size:
            self.append_class('hidden-%s-up' % hide_for_size.class_label)

        self.add_child(TextNode(view, text))


class ResponsivePull(HTMLAttributeValueOption):
    def __init__(self, side, device_class):
        is_set = True if device_class else False
        self.device_class_label = device_class if (is_set and device_class is not True) else None
        super(ResponsivePull, self).__init__(side, is_set, prefix='pull')

    @property
    def side(self):
        return self.option_string

    def as_html_snippet(self):
        if self.device_class_label:
            return '-'.join([self.prefix, self.device_class_label, self.side])
        return super(ResponsivePull, self).as_html_snippet()


class ResponsiveFloat(Layout):
    def __init__(self, left=None, right=None):
        super(ResponsiveFloat, self).__init__()
        assert (left or right) and not (left and right), 'You should specify left or right, not both'
        self.left = ResponsivePull('left', left)
        self.right = ResponsivePull('right', right)

    def customise_widget(self):
        super(ResponsiveFloat, self).customise_widget()
        for responsive_pull in [self.left, self.right]:
            if responsive_pull.is_set:
                self.widget.append_class(responsive_pull.as_html_snippet())


class NavbarFixed(HTMLAttributeValueOption):
    def __init__(self, fixed_to):
        super(NavbarFixed, self).__init__(fixed_to, fixed_to is not None, 
                                          prefix='navbar-fixed', constrain_value_to=['top', 'bottom'])

class ColourTheme(HTMLAttributeValueOption):
    def __init__(self, name):
        super(ColourTheme, self).__init__(name, name is not None, 
                                          prefix='navbar', constrain_value_to=['light', 'dark'])

class BackgroundScheme(HTMLAttributeValueOption):
    def __init__(self, name):
        super(BackgroundScheme, self).__init__(name, name is not None, 
                                               prefix='bg', constrain_value_to=['primary', 'inverse', 'faded']) 

class NavbarLayout(Layout):
    def __init__(self, fixed_to=None, full=False, center_contents=False, colour_theme=None, bg_scheme=None):
        super(NavbarLayout, self).__init__()
        assert [fixed_to, full].count(True) <= 1, 'Only one should be set'
        self.fixed = NavbarFixed(fixed_to)
        self.full = HTMLAttributeValueOption('navbar-full', full)
        self.center_contents = center_contents
        self.colour_theme = ColourTheme(colour_theme)
        self.bg_scheme = BackgroundScheme(bg_scheme)
        self.brand = None

    def customise_widget(self):
        super(NavbarLayout, self).customise_widget()
        nav = self.widget.contents_container
        if self.center_contents:
            centering_div = nav.add_child(Div(self.view).use_layout(Container()))
            self.widget.set_contents_container(centering_div)

        for option in [self.fixed, self.full]:
            if option.is_set:
                self.widget.append_class(option.as_html_snippet())
            
        for option in [self.colour_theme, self.bg_scheme]:
            if option.is_set:
                nav.append_class(option.as_html_snippet())

    def set_brand_text(self, brand_text):
        brand_a = A(self.view, Url('#'), description=brand_text)
        self.set_brand(brand_a)

    def set_brand(self, brand_html_element):
        assert not self.brand and isinstance(brand_html_element, HTMLElement)
        self.widget.contents_container.insert_child(0, brand_html_element)
        brand_html_element.append_class('navbar-brand')
        self.brand = brand_html_element

    def add(self, widget, left=None, right=None):
        assert isinstance(widget, reahl.web.bootstrap.navs.Nav) or isinstance(widget, Form), 'You may only add Navs or Forms to a Navbar'
        if isinstance(widget, reahl.web.bootstrap.navs.Nav):
            widget.append_class('navbar-nav')
        if left or right:
            child = Div(self.view).use_layout(ResponsiveFloat(left=left, right=right))
            child.add_child(widget)
        else:
            child = widget
        self.widget.contents_container.add_child(child)
        return widget

    def add_toggle(self, target_html_element, text=None):
        assert target_html_element.css_id_is_set, 'To add a toggle to %s, you must set its css_id' % target_html_element
        target_html_element.append_class('collapse')
        toggle = CollapseToggle(self.view, target_html_element, text=text)
        self.widget.contents_container.add_child(toggle)
        return toggle


class ResponsiveLayout(NavbarLayout):
    def __init__(self, collapse_below_device_class, fixed_to=None, full=False, center_contents=False, colour_theme=None, bg_scheme=None, text=None):
        super(ResponsiveLayout, self).__init__(fixed_to=fixed_to, full=full, center_contents=center_contents, colour_theme=colour_theme, bg_scheme=bg_scheme)
        self.collapse_below_device_class = DeviceClass(collapse_below_device_class)
        assert self.collapse_below_device_class.one_smaller, 'It does not make sense to collapse only smaller than smallest devices'
        self.text = text

    def customise_widget(self):
        super(ResponsiveLayout, self).customise_widget()
        assert self.widget.css_id_is_set, 'To use a %s, you must set the css_id on %s' % (self.__class__, self.widget)

        collapsable = Div(self.view, css_id='%s_collapsable' % self.widget.css_id)
        collapsable.append_class('collapse')
        toggle_widget = CollapseToggle(self.view, collapsable, text=self.text, hide_for_size=self.collapse_below_device_class)
        toggle_size = self.collapse_below_device_class.one_smaller
        collapsable.append_class('navbar-toggleable-%s' % toggle_size.class_label)
        
        self.widget.contents_container.add_child(toggle_widget)
        self.widget.contents_container.add_child(collapsable)
        self.widget.set_contents_container(collapsable)




class Navbar(HTMLWidget):
    def __init__(self, view):
        super(Navbar, self).__init__(view)

        self.navbar = self.add_child(Nav(view))
        self.navbar.append_class('navbar')
        self.set_contents_container(self.navbar)
        self.set_html_representation(self.navbar)

    def set_contents_container(self, container):
        self.contents_container = container





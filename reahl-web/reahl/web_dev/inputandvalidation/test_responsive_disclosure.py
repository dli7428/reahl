# Copyright 2018 Reahl Software Services (Pty) Ltd. All rights reserved.
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


from __future__ import print_function, unicode_literals, absolute_import, division

from reahl.tofu import Fixture, expected, scenario, uses
from reahl.tofu.pytestsupport import with_fixtures
from reahl.stubble import CallMonitor

from reahl.web_dev.fixtures import WebFixture
from reahl.webdev.tools import XPath
from reahl.web.fw import Widget
from reahl.web.ui import Form, Div, SelectInput, Label, P, RadioButtonSelectInput, CheckboxSelectInput, \
                         CheckboxInput, ButtonInput, TextInput
from reahl.component.modelinterface import BooleanField, MultiChoiceField, ChoiceField, Choice, exposed, IntegerField, \
                                           EmailField, Event, Action, Field
from reahl.web_dev.inputandvalidation.test_widgetqueryargs import QueryStringFixture

@uses(web_fixture=WebFixture)
class ResponsiveDisclosureFixture(Fixture):

    def new_ModelObject(self):
        class ModelObject(object):
            @exposed
            def fields(self, fields):
                fields.choice = ChoiceField([Choice(1, IntegerField(label='One')), 
                                            Choice(2, IntegerField(label='Two')), 
                                            Choice(3, IntegerField(label='Three'))], 
                                            default=1,
                                            label='Choice')
        return ModelObject

    def new_MyChangingWidget(self):
        class MyChangingWidget(Div):
            def __init__(self, view, trigger_input, model_object):
                self.trigger_input = trigger_input
                self.model_object = model_object
                super(MyChangingWidget, self).__init__(view, css_id='dave')
                self.enable_refresh()
                trigger_input.enable_notify_change(self.query_fields.fancy_state)
                self.add_child(P(self.view, text='My state is now %s' % self.fancy_state))

            @property
            def fancy_state(self):
                return self.model_object.choice

            @exposed
            def query_fields(self, fields):
                fields.fancy_state = self.model_object.fields.choice

        return MyChangingWidget
    
    def new_MainWidget(self):
        fixture = self
        class MainWidget(Widget):
            def __init__(self, view):
                super(MainWidget, self).__init__(view)
                an_object = fixture.ModelObject()
                form = self.add_child(fixture.MyForm(view, an_object))
                self.add_child(fixture.MyChangingWidget(view, form.select_input, an_object))

        return MainWidget

    def new_MyForm(self):
        class MyForm(Form):
            def __init__(self, view, an_object):
                super(MyForm, self).__init__(view, 'myform')
                self.select_input = SelectInput(self, an_object.fields.choice)
                self.add_child(Label(view, for_input=self.select_input))
                self.add_child(self.select_input)
        return MyForm


class ResponsiveWidgetScenarios(ResponsiveDisclosureFixture):
    @scenario
    def select_input(self):
        fixture = self

        def change_value(browser):
              browser.select(XPath.select_labelled('Choice'), 'Three')
        self.change_value = change_value
        self.initial_state = 1
        self.changed_state = 3

    @scenario
    def radio_buttons(self):
        fixture = self

        class MyForm(Form):
            def __init__(self, view, an_object):
                super(MyForm, self).__init__(view, 'myform')
                self.select_input = RadioButtonSelectInput(self, an_object.fields.choice)
                self.select_input.set_id('marvin')
                self.add_child(Label(view, for_input=self.select_input))
                self.add_child(self.select_input)
        self.MyForm = MyForm

        def change_value(browser):
            browser.click(XPath.input_labelled('Three'))
        self.change_value = change_value
        self.initial_state = 1
        self.changed_state = 3

    @scenario
    def single_valued_checkbox(self):
        fixture = self

        class ModelObject(object):
            @exposed
            def fields(self, fields):
                fields.choice = BooleanField(default=False, label='Choice')
        self.ModelObject = ModelObject

        class MyForm(Form):
            def __init__(self, view, an_object):
                super(MyForm, self).__init__(view, 'myform')
                self.select_input = CheckboxInput(self, an_object.fields.choice)
                self.select_input.set_id('marvin')
                self.add_child(Label(view, for_input=self.select_input))
                self.add_child(self.select_input)
        self.MyForm = MyForm

        def change_value(browser):
            browser.click(XPath.input_labelled('Choice'))
        self.change_value = change_value
        self.initial_state = False
        self.changed_state = True

    @scenario
    def multi_valued_checkbox_select(self):
        fixture = self

        class ModelObject(object):
            @exposed
            def fields(self, fields):
                fields.choice = MultiChoiceField([Choice(1, IntegerField(label='One')), 
                                            Choice(2, IntegerField(label='Two')), 
                                            Choice(3, IntegerField(label='Three'))], 
                                            default=[1],
                                            label='Choice')
        self.ModelObject = ModelObject

        class MyForm(Form):
            def __init__(self, view, an_object):
                super(MyForm, self).__init__(view, 'myform')
                self.select_input = CheckboxSelectInput(self, an_object.fields.choice)
                self.select_input.set_id('marvin')
                self.add_child(Label(view, for_input=self.select_input))
                self.add_child(self.select_input)
        self.MyForm = MyForm

        def change_value(browser):
            browser.click(XPath.input_labelled('Three'))
        self.change_value = change_value
        self.initial_state = [1]
        self.changed_state = [1, 3]


@with_fixtures(WebFixture, QueryStringFixture, ResponsiveWidgetScenarios)
def test_input_values_can_be_widget_arguments(web_fixture, query_string_fixture, responsive_widget_scenarios):
    """Widget query arguments can be linked to the value of an input, which means the Widget will be re-rendered if the input value changes."""

    fixture = responsive_widget_scenarios

    wsgi_app = web_fixture.new_wsgi_app(enable_js=True, child_factory=fixture.MainWidget.factory())
    web_fixture.reahl_server.set_app(wsgi_app)
    browser = web_fixture.driver_browser
    browser.open('/')

    assert browser.wait_for(query_string_fixture.is_state_now, fixture.initial_state)
    fixture.change_value(browser)
    assert browser.wait_for(query_string_fixture.is_state_now, fixture.changed_state)


@with_fixtures(WebFixture, QueryStringFixture, ResponsiveDisclosureFixture)
def test_changing_values_do_not_disturb_other_hash_state(web_fixture, query_string_fixture, responsive_disclosure_fixture):
    """When an Input updates a linked Widget, other values in the hash are preserved."""

    fixture = responsive_disclosure_fixture

    wsgi_app = web_fixture.new_wsgi_app(enable_js=True, child_factory=fixture.MainWidget.factory())
    web_fixture.reahl_server.set_app(wsgi_app)
    browser = web_fixture.driver_browser
    browser.open('/')

    assert browser.wait_for(query_string_fixture.is_state_now, 1)
    browser.set_fragment('#choice=2&other_var=other_value')
    browser.select(XPath.select_labelled('Choice'), 'Three')
    assert browser.get_fragment() == '#choice=3&other_var=other_value'


def test_inputs_effect_other_parts_of_form(web_fixture):
    """Inputs can trigger refresh of Widgets that contain other inputs in the same form"""
    assert None, 'TODO: relax check_input_placement so that it only breaks if the form does NOT have a specific ID set (it should still break if the form ID is auto-generated' 
    # We need to think carefully about this one.
    # It makes sense to let an input be refreshed anywhere on the page, as long as its form's ID is always going to be unchanged.
    # Perhaps the test to change first is test_check_input_placement (inputandvalidation/test_eventhandling.py)
    # ...but I still think we need to have a test here? because this is a requirement relating to responsive disclosure?


@with_fixtures(WebFixture)
def test_validation(web_fixture):
    """If a Field is required, but its Input is not currently displayed as part of the form (because of the 
       state of another Input), the form should not expect input for it."""

    fixture = web_fixture

    class CheckModelValue(object):
        def submit_event(self, model_object):
            assert model_object.subscribe_to_newsletter == False
            assert not hasattr(model_object, 'email')
    check_model_value = CheckModelValue()

    class ModelObject(object):
        def handle_event(self):
            check_model_value.submit_event(self)

        @exposed
        def events(self, events):
            events.an_event = Event(label='click me', action=Action(self.handle_event))

        @exposed
        def fields(self, fields):
            fields.subscribe_to_newsletter = BooleanField(default=False, label='Subscribe to newsletter')
            fields.email = EmailField(required=True, label='Email')

    class MyForm(Form):
        def __init__(self, view):
            super(MyForm, self).__init__(view, 'myform')

            model_object = ModelObject()
            self.add_child(QuestionSection(self, model_object))
            self.define_event_handler(model_object.events.an_event)
            self.add_child(ButtonInput(self, model_object.events.an_event))

    class QuestionSection(Div):
        def __init__(self, form, model_object):
            self.model_object = model_object
            super(QuestionSection, self).__init__(form.view, css_id='questionid')

            checkbox_input = CheckboxInput(form, model_object.fields.subscribe_to_newsletter)
            self.add_child(Label(form.view, for_input=checkbox_input))
            checkbox_input.set_id('triggerid')
            self.add_child(checkbox_input)

            self.enable_refresh()
            checkbox_input.enable_notify_change(self.query_fields.subscribe_to_newsletter)

            if self.model_object.subscribe_to_newsletter:
                self.add_child(RequiredInfo(form, self.model_object))

        @exposed
        def query_fields(self, fields):
            fields.subscribe_to_newsletter = self.model_object.fields.subscribe_to_newsletter

    class RequiredInfo(Div):
        def __init__(self, form, model_object):
            super(RequiredInfo, self).__init__(form.view)
            text_input = TextInput(form, model_object.fields.email)
            self.add_child(Label(form.view, for_input=text_input))
            self.add_child(text_input)



    from reahl.web.bootstrap.forms import TextInput, FieldSet, FormLayout
    class IDDocument(object):

        @exposed
        def fields(self, fields):
            fields.subscribe_to_newsletter = BooleanField(default=False, label='Subscribe to newsletter')

            types = [Choice('passport', Field(label='Passport')),
                     Choice('rsa_id', Field(label='RSA ID'))]
            fields.document_type = ChoiceField(types, label='Type', default='rsa_id', required=False)
            fields.id_number     = Field(label='ID number', required=True)
            fields.passport_number = Field(label='Passport number', required=True)
            countries = [Choice('Ghana', Field(label='Ghana')),
                         Choice('South Africa', Field(label='South Africa')),
                         Choice('Nigeria', Field(label='Nigeria')),
                         Choice('Namibia', Field(label='Namibia')),
                         Choice('Zimbabwe', Field(label='Zimbabwe')),
                         Choice('Kenya', Field(label='Kenya'))
                         ]
            fields.country = ChoiceField(countries, label='Country', required=True)



    class IDForm(Form):
        def __init__(self, view):
            super(IDForm, self).__init__(view, 'myidform')

            new_document = IDDocument()
            grouped_inputs = self.add_child(FieldSet(view, legend_text='Identifying document'))
            grouped_inputs.use_layout(FormLayout())
            trigger = grouped_inputs.layout.add_input(SelectInput(self, new_document.fields.document_type))
            grouped_inputs.add_child(IDInputsSection(self, new_document, trigger))


    class IDInputsSection(Div):
        def __init__(self, form, document, trigger_input):
            self.document = document
            super(IDInputsSection, self).__init__(form.view, css_id='idinputs')
            self.enable_refresh()
            trigger_input.enable_notify_change(self.query_fields.document_type)

            if self.document.document_type == 'passport':
                self.add_child(PassportInputs(form, self.document))
            elif self.document.document_type     == 'rsa_id':
                self.add_child(IDInputs(form, self.document))

        @exposed
        def query_fields(self, fields):
            fields.document_type = self.document.fields.document_type

    class PassportInputs(Div):
        def __init__(self, form, document):
            super(PassportInputs, self).__init__(form.view)
            self.use_layout(FormLayout())
            self.layout.add_input(SelectInput(form, document.fields.country))
            self.layout.add_input(TextInput(form, document.fields.passport_number))

    class IDInputs(Div):
        def __init__(self, form, document):
            super(IDInputs, self).__init__(form.view)
            self.use_layout(FormLayout())
            self.layout.add_input(TextInput(form, document.fields.id_number))

    class BigWidget(Widget):
        def __init__(self, view):
            super(BigWidget, self).__init__(view)
            self.add_child(MyForm(view))
            self.add_child(IDForm(view))


    wsgi_app = web_fixture.new_wsgi_app(enable_js=True, child_factory=BigWidget.factory())
    web_fixture.reahl_server.set_app(wsgi_app)
    browser = web_fixture.driver_browser
    browser.open('/')

    web_fixture.pdb()

    assert browser.is_element_present(XPath.input_labelled('Email'))
    browser.click(XPath.input_labelled('Subscribe to newsletter'))
    assert not browser.is_element_present(XPath.input_labelled('Email'))

    with CallMonitor(check_model_value.submit_event) as monitor:
        assert monitor.times_called == 0
        browser.click(XPath.button_labelled('click me'))
        assert monitor.times_called == 1

    assert None, 'This might just already work, but I think we need a test'


def test_input_values_are_retained():
    """When input is intered into an input which is not always displayed, that previously entered input should be 
       saved when the input is not visible, and displayed once the input becomes visible again."""
    assert None, 'Not sure if we really want it to work this way...but this is a possible requirement'
    # If I understand the code correctly, this will already work if the underlying model object is persisted.
    # However, if you really want things to work this way, you should probably make it work regardless of
    # whether the underlying model object is persisted because one would expect such a feature to always just work.
    # I have not thought whether or not you really want this in a real world use case. Perhaps you DO want to 
    # start from scratch each time the user flips? Perhaps because we're unsure we should not spend time on this now?


# Naming of notifier.
# Clashing names of things on the hash (larger issue)

# TODO: break if a user sends a ChoiceField to a CheckboxSelectInput
# TODO: test that things like TextInput can give input to a MultiChoiceField by doing, eg input.split(',') in the naive case


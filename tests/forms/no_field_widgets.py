# -*- coding: utf-8 -*-
import unittest
from os import path
from html5lib import HTMLParser, treebuilders
from webob.multidict import MultiDict
from iktomi.utils.storage import VersionedStorage
from iktomi.templates import Template, BoundTemplate
from iktomi.templates import jinja2 as jnj
from iktomi.templates.jinja2 import TemplateEngine
import jinja2
import xpath

from iktomi.forms import fields, convs, widgets, media, perms, \
                         Form, Field, FieldList, FieldSet


class TestFormClass(unittest.TestCase):
    def setUp(self):
        pass
    
    @property
    def env(self):
        DIR = jnj.__file__
        DIR = path.dirname(path.abspath(DIR))
        TEMPLATES = [path.join(DIR, 'templates')]

        jinja_loader = TemplateEngine(TEMPLATES)
        template_loader = Template(engines={'html': jinja_loader},
                                            *TEMPLATES)
        env = VersionedStorage()
        env.template = BoundTemplate(env, template_loader)
        return env

    def parse(self, value):
        p = HTMLParser(tree=treebuilders.getTreeBuilder("dom"))
        return p.parseFragment(value)


class TestNoFieldWidget(TestFormClass):

    def test_init_form(self):
        class TestForm(Form):
            fields = [
                widgets.FieldBlock('', fields=[
                    widgets.NoFieldWidget(),
                    Field('f1'),
                    FieldSet('f2', fields=[]),
                    FieldList('f3', field=Field(''))
                ]),
                Field('f4'),
                FieldSet('f5', fields=[]),
                FieldList('f6', field=Field('')),
                widgets.NoFieldWidget(),
            ]

        form = TestForm()
        self.assertEqual([x.name for x in form.fields],
                         ['f1', 'f2', 'f3', 'f4', 'f5', 'f6'])
        self.assertEqual([type(x) for x in form.widgets],
                         [widgets.FieldBlock, Field.widget, FieldSet.widget, 
                          FieldList.widget, widgets.NoFieldWidget])

    def test_init_fieldset(self):
        class TestForm(Form):
            fields = [
                FieldSet('name', fields=[
                    widgets.FieldBlock('', fields=[
                        widgets.NoFieldWidget(),
                        Field('f1'),
                        FieldSet('f2', fields=[]),
                        FieldList('f3', field=Field(''))
                    ]),
                    Field('f4'),
                    FieldSet('f5', fields=[]),
                    FieldList('f6', field=Field('')),
                    widgets.NoFieldWidget(),
                ])
            ]

        form = TestForm()
        self.assertEqual([x.name for x in form.get_field('name').fields],
                         ['f1', 'f2', 'f3', 'f4', 'f5', 'f6'])
        self.assertEqual([type(x) for x in form.get_field('name').widgets],
                         [widgets.FieldBlock, Field.widget, FieldSet.widget, 
                          FieldList.widget, widgets.NoFieldWidget])

    def test_render_no_field(self):
        widget_text = jinja2.Markup('<div>widget</div>')
        class TestForm(Form):
            fields = [
                widgets.NoFieldWidget(render=lambda: widget_text)
            ]
        form = TestForm(self.env)
        render = form.render()
        html = self.parse(render)
        self.assert_(xpath.find('.//*:div[text()="widget"]', html))

    def test_render_field_block(self):
        widget_text = jinja2.Markup('<div>widget</div>')
        class TestForm(Form):
            fields = [
                widgets.FieldBlock('Title', fields=[
                    widgets.NoFieldWidget(render=lambda: widget_text),
                    Field('f1'),
                ],
                classname="block"),
            ]

        form = TestForm(self.env)
        render = form.render()
        html = self.parse(render)

        self.assertEqual(xpath.findvalue('.//*:div[@class="block"]/*:h2/text()', html), 'Title')
        self.assert_(xpath.find('.//*:div[@class="block"]//*:input[@name="f1"]', html))
        self.assert_(xpath.find('.//*:div[@class="block"]//*:div[text()="widget"]', html))



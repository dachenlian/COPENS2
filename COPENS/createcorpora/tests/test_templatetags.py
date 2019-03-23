from django.test import TestCase
from django.http import HttpRequest, QueryDict
from django.utils.html import escape
from ..templatetags import my_tags
from django.template import Template, Context


class TemplateTagTest(TestCase):

    TEMPLATE = Template("{% load my_tags %} {% param_replace page=1 test='true' %}")

    def test_param_replace_updates_query_string(self):
        context = Context({'request': HttpRequest()})
        rendered_template = self.TEMPLATE.render(context)
        self.assertIn(escape('page=1&test=true'), rendered_template)

    def test_param_replace_returns_correct_string(self):
        context = Context({'request': HttpRequest()})
        params = {'page': 1, 'test': 'true', 'empty': ''}
        encoded = my_tags.param_replace(context, **params)
        params.pop('empty')
        q = QueryDict(mutable=True)
        q.update(params)
        self.assertEquals(encoded, q.urlencode())

    def test_get_list_returns_list(self):
        lst = ['asbc', 'plurk', 'ntuspeak']
        context = QueryDict('&'.join(f'corpora={value}' for value in lst))
        lst = my_tags.get_list(context, 'corpora')
        self.assertSequenceEqual(['asbc', 'plurk', 'ntuspeak'], lst)



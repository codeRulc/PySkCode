"""
SkCode acronyms tag test code.
"""

import unittest

from skcode.etree import TreeNode
from skcode.tags import (AcronymTagOptions,
                         DEFAULT_RECOGNIZED_TAGS)


class AcronymsTagTestCase(unittest.TestCase):
    """ Tests suite for the acronyms tag module. """

    def test_tag_and_aliases_in_default_recognized_tags_dict(self):
        """ Test the presence of the tag and aliases in the dictionary of default recognized tags. """
        self.assertIn('abbr', DEFAULT_RECOGNIZED_TAGS)
        self.assertIsInstance(DEFAULT_RECOGNIZED_TAGS['abbr'], AcronymTagOptions)
        self.assertIn('acronym', DEFAULT_RECOGNIZED_TAGS)
        self.assertIsInstance(DEFAULT_RECOGNIZED_TAGS['acronym'], AcronymTagOptions)

    def test_tag_constant_values(self):
        """ Test tag constants. """
        opts = AcronymTagOptions()
        self.assertFalse(opts.newline_closes)
        self.assertFalse(opts.same_tag_closes)
        self.assertFalse(opts.standalone)
        self.assertTrue(opts.parse_embedded)
        self.assertFalse(opts.swallow_trailing_newline)
        self.assertTrue(opts.inline)
        self.assertFalse(opts.close_inlines)
        self.assertFalse(opts.make_paragraphs_here)
        self.assertEqual(opts.acronym_title_attr_name, 'title')

    def test_get_acronym_title_with_tagname_set(self):
        """ Test the ``get_acronym_title`` when the tag name attribute is set. """
        opts = AcronymTagOptions()
        tree_node = TreeNode(None, 'acronym', opts, attrs={'acronym': 'test'})
        title = opts.get_acronym_title(tree_node)
        self.assertEqual('test', title)

    def test_get_acronym_title_with_title_set(self):
        """ Test the ``get_acronym_title`` when the "title" attribute is set. """
        opts = AcronymTagOptions()
        tree_node = TreeNode(None, 'acronym', opts, attrs={'title': 'test'})
        title = opts.get_acronym_title(tree_node)
        self.assertEqual('test', title)

    def test_get_acronym_title_with_title_and_tagname_set(self):
        """ Test the ``get_acronym_title`` when the "title" and tag name attribute is set. """
        opts = AcronymTagOptions()
        tree_node = TreeNode(None, 'acronym', opts, attrs={'acronym': 'test', 'title': 'test2'})
        title = opts.get_acronym_title(tree_node)
        self.assertEqual('test', title)

    def test_get_acronym_title_without_title_set(self):
        """ Test the ``get_acronym_title`` when the title is not set at all. """
        opts = AcronymTagOptions()
        tree_node = TreeNode(None, 'acronym', opts, attrs={})
        title = opts.get_acronym_title(tree_node)
        self.assertEqual('', title)

    def test_get_acronym_title_with_html_entities(self):
        """ Test the ``get_acronym_title`` when the title contain HTML entities. """
        opts = AcronymTagOptions()
        tree_node = TreeNode(None, 'acronym', opts, attrs={'title': '&lt;test&gt;'})
        title = opts.get_acronym_title(tree_node)
        self.assertEqual('<test>', title)

    def test_html_rendering(self):
        """ Test HTML rendering. """
        opts = AcronymTagOptions()
        tree_node = TreeNode(None, 'acronym', opts, attrs={'title': 'As Soon As Possible'})
        rendered_output = opts.render_html(tree_node, 'ASAP')
        expected_output = '<abbr title="As Soon As Possible">ASAP</abbr>'
        self.assertEqual(expected_output, rendered_output)

    def test_html_rendering_without_title(self):
        """ Test HTML rendering without title. """
        opts = AcronymTagOptions()
        tree_node = TreeNode(None, 'acronym', opts, attrs={})
        rendered_output = opts.render_html(tree_node, 'ASAP')
        expected_output = 'ASAP'
        self.assertEqual(expected_output, rendered_output)

    def test_html_rendering_with_html_entities_in_title(self):
        """ Test HTML rendering with HTML entities in title. """
        opts = AcronymTagOptions()
        tree_node = TreeNode(None, 'acronym', opts, attrs={'title': '<As Soon As Possible>'})
        rendered_output = opts.render_html(tree_node, 'ASAP')
        expected_output = '<abbr title="&lt;As Soon As Possible&gt;">ASAP</abbr>'
        self.assertEqual(expected_output, rendered_output)

    def test_text_rendering(self):
        """ Test text rendering. """
        opts = AcronymTagOptions()
        tree_node = TreeNode(None, 'acronym', opts, attrs={'title': 'As Soon As Possible'})
        rendered_output = opts.render_text(tree_node, 'ASAP')
        expected_output = 'ASAP (As Soon As Possible)'
        self.assertEqual(expected_output, rendered_output)

    def test_text_rendering_without_title(self):
        """ Test text rendering without title. """
        opts = AcronymTagOptions()
        tree_node = TreeNode(None, 'acronym', opts, attrs={})
        rendered_output = opts.render_text(tree_node, 'ASAP')
        expected_output = 'ASAP'
        self.assertEqual(expected_output, rendered_output)

    def test_text_rendering_with_html_entities_in_title(self):
        """ Test text rendering with HTML entities in title. """
        opts = AcronymTagOptions()
        tree_node = TreeNode(None, 'acronym', opts, attrs={'title': '<As Soon As Possible>'})
        rendered_output = opts.render_text(tree_node, 'ASAP')
        expected_output = 'ASAP (<As Soon As Possible>)'
        self.assertEqual(expected_output, rendered_output)

    def test_skcode_rendering(self):
        """ Test SkCode rendering. """
        opts = AcronymTagOptions()
        tree_node = TreeNode(None, 'acronym', opts, attrs={'title': 'As Soon As Possible'})
        rendered_output = opts.render_skcode(tree_node, 'ASAP')
        expected_output = '[acronym title="As Soon As Possible"]ASAP[/acronym]'
        self.assertEqual(expected_output, rendered_output)

    def test_skcode_rendering_alias(self):
        """ Test SkCode rendering using alias. """
        opts = AcronymTagOptions()
        tree_node = TreeNode(None, 'abbr', opts, attrs={'title': 'As Soon As Possible'})
        rendered_output = opts.render_skcode(tree_node, 'ASAP')
        expected_output = '[abbr title="As Soon As Possible"]ASAP[/abbr]'
        self.assertEqual(expected_output, rendered_output)

    def test_skcode_rendering_without_title(self):
        """ Test SkCode rendering without title. """
        opts = AcronymTagOptions()
        tree_node = TreeNode(None, 'acronym', opts, attrs={})
        rendered_output = opts.render_skcode(tree_node, 'ASAP')
        expected_output = '[acronym title=""]ASAP[/acronym]'
        self.assertEqual(expected_output, rendered_output)

    def test_skcode_rendering_with_html_entities_in_title(self):
        """ Test SkCode rendering with HTML entities in title. """
        opts = AcronymTagOptions()
        tree_node = TreeNode(None, 'acronym', opts, attrs={'title': '<As Soon As Possible>'})
        rendered_output = opts.render_skcode(tree_node, 'ASAP')
        expected_output = '[acronym title="<As Soon As Possible>"]ASAP[/acronym]'
        self.assertEqual(expected_output, rendered_output)

from ..etree import TreeNode


class CollapseBaseTreeNode(TreeNode):
    """ Base class for all text alignment tag class. """

    # HTML template for rendering
    html_render_template = '<div class="{name}">{inner_html}</div>\n'

    def render_html(self, inner_html, **kwargs):
        """
        Callback function for rendering HTML.
        :param inner_html: The inner HTML of this tree node.
        :param kwargs: Extra keyword arguments for rendering.
        :return The rendered HTML of this node.
        """
        return self.html_render_template.format(name=self.canonical_tag_name, inner_html=inner_html)

    def render_text(self, inner_text, **kwargs):
        """
        Callback function for rendering text.
        :param inner_text: The inner text of this tree node.
        :param kwargs: Extra keyword arguments for rendering.
        :return The rendered text of this node.
        """
        return inner_text


class CollapseTreeNode(CollapseBaseTreeNode):
    """ Center align text tree node class. """

    canonical_tag_name = 'collapse'
    alias_tag_names = ()


class Collapse2TreeNode(CollapseBaseTreeNode):
    """ Left align text tree node class. """

    canonical_tag_name = 'collapse2'
    alias_tag_names = ()

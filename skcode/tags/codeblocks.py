"""
SkCode code block tag definitions code (require Pygments library).
"""

from gettext import gettext as _

from html import escape as escape_html
from html import unescape as unescape_html_entities

try:
    from pygments import highlight
    from pygments.formatters import HtmlFormatter
    from pygments.lexers import get_lexer_by_name
    from pygments.styles import get_style_by_name
    from pygments.util import ClassNotFound
except (ImportError, ModuleNotFoundError):
    pass

from ..etree import TreeNode
from ..tools import sanitize_url, slugify
from ..utility.relative_urls import get_relative_url_base


class CodeBlockTreeNode(TreeNode):
    """ Code block tree node class. """

    parse_embedded = False

    canonical_tag_name = 'code'
    alias_tag_names = ()

    # Tabulation size in spaces
    tab_size = 4

    # Pygments CSS style name
    pygments_css_style_name = 'default'

    # Display line numbers
    display_line_numbers = True

    # Default language name
    default_language_name = 'text'

    # Language attribute name
    language_attr_name = 'language'

    # Highlight lines attribute name
    hl_lines_attr_name = 'hl_lines'

    # Start line number attribute name
    line_start_num_attr_name = 'linenostart'

    # Filename attribute name
    filename_attr_name = 'filename'

    # Source link attribute name
    source_link_attr_name = 'src'

    # Figure ID attribute name
    figure_id_attr_name = 'id'

    # CSS class of the wrapping div
    wrapping_div_class_name = 'codetable'

    # HTML template of the wrapping div
    wrapping_div_html_template = """<div class="{class_name}">
    {source_code}
</div>"""

    # HTML template for the source caption text
    source_caption_html_template = 'Source : {}'

    # HTML template for the source link
    source_link_html_template = '<a href="{src_link}"{extra_args} target="_blank">{caption} ' \
                                '<i class="fa fa-link" aria-hidden="true"></i></a>'

    # HTML template for the source code (with caption)
    code_html_template = """<div class="panel panel-default" id="{figure_id}">
    <div class="panel-body">
        {source_code}
    </div>
    <div class="panel-footer">
        {caption}
    </div>
</div>"""

    # HTML template for the source code (without caption)
    code_only_html_template = '<a id="{figure_id}"></a>\n{source_code}'

    def get_language_name(self):
        """
        Return the language name of this code block for syntax highlighting.
        The language name can be set by setting the ``language_attr_name`` attribute of the tag or simply
        by setting the tag name attribute.
        The lookup order is: tag name (first), ``language_attr_name``.
        :return The language name of this code block, or the default one if not specified.
        """
        language_name = self.get_attribute_value('', self.language_attr_name, default=self.default_language_name)
        return unescape_html_entities(language_name)

    def get_highlight_lines(self):
        """
        Return the list of lines which has to be highlighted.
        :return A list of line numbers as int.
        """

        # Get the list as string
        highlight_lines = self.attrs.get(self.hl_lines_attr_name, '')

        # Shortcut if no line
        line_nums = []
        if not highlight_lines:
            return line_nums

        # Turn all line number into int
        for line_num in highlight_lines.split(','):
            line_num = line_num.strip()
            if not line_num:
                continue
            try:
                line_num = int(line_num)
                if line_num >= 0:
                    line_nums.append(line_num)
                else:
                    self.error_message = _('Line number must be positive')
            except ValueError:
                self.error_message = _('{} is not a number').format(line_num)

        # Return the list
        return line_nums

    def get_start_line_number(self):
        """
        Return the line number of the first line.
        :return: The line number to be used for the first line, or 1 if not specified.
        """

        # Get the line number as string
        first_line_number = self.attrs.get(self.line_start_num_attr_name, '')

        # Shortcut if no line number
        if not first_line_number:
            return 1

        # Return the line number as int
        try:
            line_num = int(first_line_number)
            if line_num >= 0:
                return line_num
            else:
                self.error_message = _('Line number must be positive')
                return 1
        except ValueError:
            self.error_message = _('{} is not a number').format(first_line_number)
            return 1

    def get_filename(self):
        """
        Return the filename of the current code block (optional).
        :return: The filename associated with the current code block, or an empty string.
        """
        filename = self.attrs.get(self.filename_attr_name, '')
        return unescape_html_entities(filename)

    def get_source_link_url(self):
        """
        Return the source link URL of the current code block (optional).
        :return: The source URL of the current code block, or an empty string.
        """
        src_link_url = self.attrs.get(self.source_link_attr_name, '')
        relative_url_base = get_relative_url_base(self.root_tree_node)
        return sanitize_url(src_link_url,
                            absolute_base_url=relative_url_base)

    def get_figure_id(self):
        """
        Return the figure ID for this code block.
        :return: The figure ID for this code block, or an empty string.
        """
        figure_id = self.attrs.get(self.figure_id_attr_name, '')
        return slugify(figure_id)

    def get_cleaned_content(self, splitlines=False):
        """
        Return the content of this node with all trailing blank lines removed.
        """
        lines = self.content.splitlines()
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()
        return lines if splitlines else '\n'.join(lines)

    def sanitize_node(self, breadcrumb):
        """
        Callback function for sanitizing and cleaning-up the given node.
        :param breadcrumb: The breadcrumb of node instances from the root node to the current node (excluded).
        """
        super(CodeBlockTreeNode, self).sanitize_node(breadcrumb)
        self.get_highlight_lines()
        self.get_start_line_number()
        try:
            language_name = self.get_language_name()
            if language_name:
                get_lexer_by_name(language_name)
        except ClassNotFound:
            self.error_message = _('Unknown language')

    def render_html(self, inner_html, force_rel_nofollow=True, **kwargs):
        """
        Callback function for rendering HTML.
        :param inner_html: The inner HTML of this tree node.
        :param force_rel_nofollow: If set to ``True``, all links in the rendered HTML will have the atribute
        "rel=nofollow" to avoid search engines to scrawl them (default ``True``).
        :param kwargs: Extra keyword arguments for rendering.
        :return The rendered HTML of this node.
        """

        # Get figure ID
        figure_id = self.get_figure_id()

        # Handle line anchors
        lineanchors = figure_id
        anchorlinenos = bool(figure_id)

        # Render the source code
        try:
            lexer = get_lexer_by_name(self.get_language_name(), tabsize=self.tab_size)
        except ClassNotFound:

            # Handle unknown language name
            lexer = get_lexer_by_name(self.default_language_name, tabsize=self.tab_size)

        style = get_style_by_name(self.pygments_css_style_name)
        formatter = HtmlFormatter(style=style,
                                  linenos='table' if self.display_line_numbers else False,
                                  hl_lines=self.get_highlight_lines(),
                                  linenostart=self.get_start_line_number(),
                                  noclasses=True,
                                  lineanchors=lineanchors,
                                  anchorlinenos=anchorlinenos)
        source_code = highlight(self.get_cleaned_content(), lexer, formatter)

        # Wrap table in div for horizontal scrolling
        source_code = self.wrapping_div_html_template.format(class_name=self.wrapping_div_class_name,
                                                             source_code=source_code)

        # Get extra filename and source link
        src_filename = self.get_filename()
        src_link_url = self.get_source_link_url()

        # Render the HTML block
        if src_filename or src_link_url:

            # Source code with caption
            caption = self.source_caption_html_template.format(escape_html(src_filename) if src_filename else src_link_url)

            # And source link
            if src_link_url:
                extra_args = ' rel="nofollow"' if force_rel_nofollow else ''
                caption = self.source_link_html_template.format(src_link=src_link_url,
                                                                extra_args=extra_args,
                                                                caption=caption)

            # Return the final HTML
            return self.code_html_template.format(figure_id=figure_id, source_code=source_code, caption=caption)

        elif figure_id:
            # Source code only with anchor
            return self.code_only_html_template.format(figure_id=figure_id, source_code=source_code)

        else:
            # Source code only
            return source_code

    def render_text(self, inner_text, **kwargs):
        """
        Callback function for rendering text.
        :param inner_text: The inner text of this tree node.
        :param kwargs: Extra keyword arguments for rendering.
        :return The rendered text of this node.
        """

        # Get all attributes
        figure_id = self.get_figure_id()
        src_filename = self.get_filename()
        src_link_url = self.get_source_link_url()
        get_start_line_number = self.get_start_line_number()
        hl_lines = self.get_highlight_lines()

        # Render the code block
        lines = []
        for num, line in enumerate(self.get_cleaned_content(splitlines=True), start=get_start_line_number):
            line = line.replace('\t', ' ' * self.tab_size)
            line_prefix = '{:d}>'.format(num) if num in hl_lines else '{:d}.'.format(num)
            lines.append('{prefix} {line}'.format(prefix=line_prefix.ljust(4), line=line))

        # Add the caption
        figure_extra = ' [#{id}]'.format(id=figure_id) if figure_id else ''
        if src_filename and src_link_url:
            caption = 'Source : {filename} ({link}){extra}'.format(filename=src_filename,
                                                                   link=src_link_url, extra=figure_extra)
            lines.append(caption)
        elif src_filename:
            caption = 'Source : {filename}{extra}'.format(filename=src_filename, extra=figure_extra)
            lines.append(caption)
        elif src_link_url:
            caption = 'Source : {link}{extra}'.format(link=src_link_url, extra=figure_extra)
            lines.append(caption)

        # Finish the job
        lines.append('')
        return '\n'.join(lines)


def generate_fixed_code_block_type_cls(language_name,
                                       canonical_tag_name=None,
                                       alias_tag_names=None):
    """
    Generate a fixed code block type class at runtime.
    :param language_name: The desired code block language to use.
    :param canonical_tag_name: The canonical name of the tag.
    :param alias_tag_names: The name alias of the tag
    :return: The generated class type.
    """
    assert language_name, "The language name is mandatory."
    _canonical_tag_name = canonical_tag_name or language_name
    _alias_tag_names = alias_tag_names or ()
    _language_name = language_name

    class FixedCodeBlockTreeNode(CodeBlockTreeNode):
        """ Fixed language code block tree node class. """

        canonical_tag_name = _canonical_tag_name
        alias_tag_names = _alias_tag_names
        language_name = _language_name

        def get_language_name(self):
            """
            Return the language name of this code block for syntax highlighting.
            :return The language name of this code block, as set in ``self.language_name``.
            """
            return self.language_name

    return FixedCodeBlockTreeNode

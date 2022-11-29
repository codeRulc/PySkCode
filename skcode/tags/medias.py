"""
SkCode medias tag definitions code.
"""

import posixpath
from gettext import gettext as _

from urllib.parse import (
    urlsplit,
    parse_qs,
    quote_plus
)

from html import escape as escape_html
from html import unescape as unescape_html_entities

from ..etree import TreeNode
from ..tools import sanitize_url
from ..utility.relative_urls import get_relative_url_base


class ImageTreeNode(TreeNode):
    """ Image tree node class. """

    canonical_tag_name = 'img'
    alias_tag_names = ()

    inline = True
    close_inlines = False

    # Alternate text attribute name
    alt_attr_name = 'alt'

    # Image width attribute name
    width_attr_name = 'width'

    # Image height attribute name
    height_attr_name = 'height'

    # Source link attribute name
    source_link_attr_name = 'src'

    # Allowed schemes for URL
    allowed_schemes = ('http', 'https')

    # HTML template for rendering
    html_render_template = '<img src="{src_link}"{extra_args} />'

    def get_image_src_link(self):
        """
        Get the image source link URL.
        """
        if src_link := self.attrs.get(self.source_link_attr_name):
            return src_link
        relative_url_base = get_relative_url_base(self.root_tree_node)
        src_link = self.get_raw_content().strip()
        return sanitize_url(src_link, allowed_schemes=self.allowed_schemes,
                            absolute_base_url=relative_url_base)

    def get_alt_text(self):
        """
        Get the image alt text.
        :return The image alternative text as string, or an empty string.
        """
        alt_text = self.attrs.get(self.alt_attr_name, '')
        return unescape_html_entities(alt_text)

    def get_img_width(self):
        """
        Get the image width, or zero.
        """
        width = self.attrs.get(self.width_attr_name, 0)
        if not width:
            return 0
        try:
            width = int(width)
            if width > 0:
                return width
            else:
                self.error_message = _('Width must be positive')
        except ValueError:
            self.error_message = _('{} is not a number').format(width)
            return 0
        return 0

    def get_img_height(self):
        """
        Get the image height, or zero.
        """
        height = self.attrs.get(self.height_attr_name, 0)
        if not height:
            return 0
        try:
            height = int(height)
            if height > 0:
                return height
            else:
                self.error_message = _('Height must be positive')
        except ValueError:
            self.error_message = _('{} is not a number').format(height)
            return 0
        return 0

    def sanitize_node(self, breadcrumb):
        """
        Callback function for sanitizing and cleaning-up the given node.
        :param breadcrumb: The breadcrumb of node instances from the root node to the current node (excluded).
        """
        super(ImageTreeNode, self).sanitize_node(breadcrumb)
        self.get_img_width()
        self.get_img_height()
        if not self.get_image_src_link():
            self.error_message = _('Missing or erroneous source URL')

    def render_html(self, inner_html, **kwargs):
        """
        Callback function for rendering HTML.
        :param inner_html: The inner HTML of this tree node.
        :param kwargs: Extra keyword arguments for rendering.
        :return The rendered HTML of this node.
        """

        # Get the image source link
        src_link = self.get_image_src_link()

        # Get the alternative text
        alt_text = self.get_alt_text()
        extra_attrs = ' alt="{}"'.format(escape_html(alt_text)) if alt_text else ''

        # Get the image width
        img_width = self.get_img_width()
        if img_width:
            extra_attrs += ' width="{}"'.format(img_width)

        # Get the image height
        img_height = self.get_img_height()
        if img_height:
            extra_attrs += ' height="{}"'.format(img_height)

        # Render the image
        return self.html_render_template.format(src_link=src_link,
                                                extra_args=extra_attrs)

    def render_text(self, inner_text, **kwargs):
        """
        Callback function for rendering text.
        :param inner_text: The inner text of this tree node.
        :param kwargs: Extra keyword arguments for rendering.
        :return The rendered text of this node.
        """

        # Get the image source link
        src_link = self.get_image_src_link()

        # Shortcut if no source link
        if not src_link:
            return inner_text

        # Get the alternative text
        alt_text = self.get_alt_text()
        return '{} ({})'.format(src_link, alt_text) if alt_text else src_link


class YoutubeTreeNode(TreeNode):
    """ Youtube video integration tree node class. """

    parse_embedded = False

    canonical_tag_name = 'youtube'
    alias_tag_names = ()

    # Default iframe width
    default_iframe_width = 560

    # Default iframe height
    default_iframe_height = 315

    # Allowed Youtube domains
    allowed_domains = (
        'www.youtube.com',
        'youtube.com',
        'youtu.be',
    )

    # Youtube video ID query arg name
    video_id_query_arg_name = 'v'

    # Special cases, when ID is in path
    video_id_in_path_domains = {
        'youtu.be',
    }

    # HTML template
    integration_html_template = """<div class="embed-container center-block">
        <div class="embed-video">
            <iframe width="{width}" height="{height}" src="https://www.youtube.com/embed/{video_id}" frameborder="0" allowfullscreen="true"></iframe>
        </div>
    </div>
    """

    # Text link
    text_link_format = 'https://youtu.be/{video_id}'

    def get_youtube_video_id(self):
        """
        Get the Youtube video ID, or an empty string.
        """

        # Get the URL
        url = self.get_raw_content().strip()

        # Shortcut if no url
        if not url:
            return ''

        # Split the URL
        try:
            scheme, netloc, path, query, fragment = urlsplit(url)
        except ValueError:

            # Handle malformed URL
            return ''

        # Check for bad netloc
        if netloc not in self.allowed_domains:
            return ''

        # Video ID in query
        if netloc not in self.video_id_in_path_domains:

            # Check for bad url query
            if not query:
                return ''

            # Get the video ID
            query_args = parse_qs(query)
            video_id = query_args.get(self.video_id_query_arg_name, None)

            # Query args return a list of values
            return video_id[0].strip() if video_id else ''

        # Video ID in path
        else:

            # Check for bad url path
            if not path or not path.startswith('/'):
                return ''

            # Get the video ID
            video_id = posixpath.basename(path.rstrip('/'))

            # Query args return a list of values
            return video_id.strip() if video_id else ''

    def sanitize_node(self, breadcrumb):
        """
        Callback function for sanitizing and cleaning-up the given node.
        :param breadcrumb: The breadcrumb of node instances from the root node to the current node (excluded).
        """
        super(YoutubeTreeNode, self).sanitize_node(breadcrumb)
        if not self.get_youtube_video_id():
            self.error_message = _('Missing or erroneous video URL')

    def render_html(self, inner_html, **kwargs):
        """
        Callback function for rendering HTML.
        :param inner_html: The inner HTML of this tree node.
        :param kwargs: Extra keyword arguments for rendering.
        :return The rendered HTML of this node.
        """

        # Get the video ID
        video_id = self.get_youtube_video_id()

        # Render the iframe
        return self.integration_html_template.format(
            width=self.default_iframe_width,
            height=self.default_iframe_height,
            video_id=quote_plus(video_id)) if video_id else inner_html

    def render_text(self, inner_text, **kwargs):
        """
        Callback function for rendering text.
        :param inner_text: The inner text of this tree node.
        :param kwargs: Extra keyword arguments for rendering.
        :return The rendered text of this node.
        """

        # Get the video ID
        video_id = self.get_youtube_video_id()
        return self.text_link_format.format(video_id=quote_plus(video_id)) if video_id else inner_text

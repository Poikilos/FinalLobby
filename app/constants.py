# -*- coding: utf-8 -*-
'''
Using older versions of the program, KivyMD (git December 2022) says:
ValueError: MDLabel.font_style is set to an invalid option 'Subhead'.
Must be one of: ['H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'Subtitle1',
'Subtitle2', 'Body1', 'Body2', 'Button', 'Caption', 'Overline', 'Icon']

For a visual showing how the styles appear, see:
<https://kivymd.readthedocs.io/en/latest/themes/font-definitions/index.html>
'''
FONT_STYLE_SUBHEADING = 'Subtitle1'
# ^ Subtitle1 is probably the same as the old 'Subhead' since they are
#   both apparently 16pt as shown (in non-compact mode) at
#   <https://github.com/kivymd/KivyMD/issues/88>

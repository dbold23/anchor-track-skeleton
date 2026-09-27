"""Anchor's visual system: theme tokens, signature marks and composed figures.

``anchor.viz.theme`` holds colours and rcParams, ``anchor.viz.marks`` the
building blocks (uncertainty lens, behaviour track, anchor pins, ethogram
ribbon), and ``anchor.viz.figures`` the composed figures the CLI, report and
gallery render. See ``docs/visual_style.md``.
"""
from anchor.viz import theme
from anchor.viz.theme import STATE_NAMES, state_color, state_colors, style, styled
__all__ = ['theme', 'STATE_NAMES', 'state_color', 'state_colors', 'style', 'styled']

import pygame
import logging

SRC_DICT = {
    ' ': (4, 54),
    'T': (29, 53),
    'R': (38, 7),
    'W': (24, 99),
    # Events
    'hammer_craft': (17, 4),
    'torch_craft': (10, 41),
    'pickaxe_craft': (35, 5),
    # Resources
    'wood': (14, 55),
    'stone': (17, 59),
    'hammer': (20, 4),
    'coal': (17, 24),
    'iron': (13, 30),
    # Players
    'Adam': (1, 0),
    'Buford': (22, 1),
    'Cindy': (38, 16),
    'Dax': (2, 109),
    'Eva': (7, 35),
    'Fate': (16, 37),
    'Gustav': (41, 40),
    'Hampton': (11, 114),
    'Ima': (1, 112),
    'Jack': (13, 111),
}


class Cell(pygame.Rect):
    def __init__(self, _id, x, y, width, height):
        super().__init__(x, y, width, height)
        self._id = _id
        try:
            src_x, src_y = SRC_DICT[self._id]
        except KeyError:
            # Handle the error, e.g., by setting a default position or logging a warning
            # logging.warning("ID '%s' not found in SRC_DICT. Using default position.", self._id)
            src_x, src_y = 0, 0  # Default position

        self.src_rect = pygame.Rect(
            src_x * width,
            src_y * height,
            width,
            height,
        )

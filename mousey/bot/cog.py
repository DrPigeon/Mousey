# -*- coding: utf-8 -*-
from .mousey import Mousey
from mousey import commands


class Cog(commands.Cog):
    def __init__(self, mousey: Mousey):
        super().__init__(mousey)

        self.mousey = mousey
        self.db = mousey.db
        self.redis = mousey.redis
        self.process = mousey.process
        self.session = mousey.session

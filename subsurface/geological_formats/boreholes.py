from subsurface.structs import LineSet


class BoreholeSet():
    def __init__(self, line_set: LineSet):
        self.geometry = line_set
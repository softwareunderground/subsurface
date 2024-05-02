from subsurface.structs import LineSet


__all__ = ['LineSet', ]


class BoreholeSet():
    def __init__(self, line_set: LineSet):
        self.geometry = line_set

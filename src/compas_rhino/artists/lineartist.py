from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.geometry import Line
from compas_rhino.artists import PrimitiveArtist, PointArtist

__all__ = ["LineArtist"]


class LineArtist(PrimitiveArtist):
    """A point artist defines functionality for visualising a COMPAS point in Rhino.
    """

    __module__ = "compas_rhino.artists"

    def __init__(self, line, layer=None, draw_points=False):

        if not isinstance(line, Line):
            raise ValueError("needs a compas.geometry.Line")

        super(LineArtist, self).__init__(line, layer=layer)

        self.GUID = PrimitiveArtist.draw_lines([self.line], self._layer, False, False)[
            0
        ]

        if draw_points:
            self.start = PointArtist(line.start)
            self.end = PointArtist(line.end)
            self.add(self.start)
            self.add(self.end)

    @property
    def line(self):
        """get the compas line geometry in local coordinate"""
        return self.geometry


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":

    from compas_rhino.utilities import unload_modules

    unload_modules("compas")
    unload_modules("compas_rhino")

    from compas.geometry import Translation, Rotation
    import math

    l = Line([0, 0, 0], [10, 0, 0])
    la = LineArtist(l, draw_points=True)

    R = Rotation.from_axis_and_angle([0, 0, 1], math.pi / 4)
    la.apply_transformation(R)
    la.draw()

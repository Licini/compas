from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.geometry import Line, Plane
from compas_rhino.artists import PrimitiveArtist, PointArtist, CircleArtist, LineArtist

__all__ = ["PlaneArtist"]


class PlaneArtist(PrimitiveArtist):
    """A point artist defines functionality for visualising a COMPAS point in Rhino.
    """

    __module__ = "compas_rhino.artists"

    def __init__(self, plane, layer=None, draw_points=False):

        if not isinstance(plane, Plane):
            raise ValueError("needs a compas.geometry.Line")

        super(PlaneArtist, self).__init__(None, layer=layer)

        self.axis_line = LineArtist(Line(plane.point, plane.normal))
        self.add(self.axis_line)

    # @property
    # def axis_line(self):
    #     """get the compas line geometry in local coordinate"""
    #     return self.axis_line.geometry


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":

    from compas_rhino.utilities import unload_modules

    unload_modules("compas")
    unload_modules("compas_rhino")

    plane = Plane([0, 0, 0], [0, 0, 1])
    pa = PlaneArtist(plane)
    pa.draw()

from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.geometry import Point
from compas_rhino.artists import PrimitiveArtist
from compas_rhino.geometry import RhinoPoint

__all__ = ["PointArtist"]


class PointArtist(PrimitiveArtist):
    """A point artist defines functionality for visualising a COMPAS point in Rhino.
    """

    __module__ = "compas_rhino.artists"

    def __init__(self, point=None, layer=None):

        if not isinstance(point, Point):
            raise ValueError("needs a compas.geometry.Point")

        super(PointArtist, self).__init__(point, layer=layer)

        self.GUID = PrimitiveArtist.draw_points(
            [self.point], self._layer, False, False
        )[0]

        self.rhino_point = RhinoPoint(self.GUID)

    @property
    def point(self):
        """get the compas point geometry in local coordinate"""
        return self.geometry



# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":

    from compas_rhino.utilities import unload_modules

    unload_modules("compas")
    unload_modules("compas_rhino")

    from compas.geometry import Rotation
    import math, time
    from threading import Thread

    pa = PointArtist(Point(10, 0, 0))
    pa2 = PointArtist(Point(-10, 0, 0))
    pa.add(pa2)

    R = Rotation.from_axis_and_angle([0, 0, 1], math.pi / 40)
    # pa.apply_transformation(R)
    # pa.draw()

    for i in range(0, 50):
        pa.apply_transformation(R)
        pa.draw()
        time.sleep(0.1)
        print(i)
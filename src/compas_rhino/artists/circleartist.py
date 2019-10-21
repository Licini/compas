from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.geometry import Circle
from compas_rhino.artists import PrimitiveArtist, PointArtist

__all__ = ["CircleArtist"]


class CircleArtist(PrimitiveArtist):
    """A point artist defines functionality for visualising a COMPAS point in Rhino.
    """

    __module__ = "compas_rhino.artists"

    def __init__(self, circle=None, layer=None, draw_center=False):

        if not isinstance(circle, Circle):
            raise ValueError("needs a compas.geometry.Circle")

        super(CircleArtist, self).__init__(circle, layer=layer)

        self.GUID = PrimitiveArtist.draw_circles(
            [self.circle], self._layer, False, False
        )[0]

        self.center = PointArtist(circle.center)
        self.add(self.center)

        if draw_center:
            self.center = PointArtist(circle.center)
            self.add(self.center)

    @property
    def circle(self):
        """get the compas circle geometry in local coordinate"""
        return self.geometry


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":

    from compas_rhino.utilities import unload_modules

    unload_modules("compas")
    unload_modules("compas_rhino")

    from compas.geometry import Plane
    from compas.geometry import Translation, Rotation
    import math

    plane = Plane([0, 0, 0], [0, 0, 1])
    circle = Circle(plane, 5)
    ca = CircleArtist(circle, draw_center=True)

    T = Translation([10, 0, 0])
    ca.apply_transformation(T)

    R = Rotation.from_axis_and_angle([1, 0, 0], math.pi/2)
    ca.apply_transformation(R)

    ca.draw()

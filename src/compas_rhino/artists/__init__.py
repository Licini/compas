"""
********************************************************************************
compas_rhino.artists
********************************************************************************

.. currentmodule:: compas_rhino.artists


Artists for visualising (painting) COMPAS data structures in Rhino.


.. autosummary::
    :toctree: generated/
    :nosignatures:

    PrimitiveArtist
    Artist
    MeshArtist
    NetworkArtist
    VolMeshArtist

"""
from __future__ import absolute_import

from .artist import *
from .primitiveartist import *

from .pointartist import *
from .circleartist import *
from .lineartist import *
from .planeartist import *


from .meshartist import *
from .networkartist import *
from .volmeshartist import *

__all__ = [name for name in dir() if not name.startswith('_')]

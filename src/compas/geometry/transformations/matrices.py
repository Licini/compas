from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import math

from copy import deepcopy

from compas.geometry.basic import scale_vector
from compas.geometry.basic import normalize_vector
from compas.geometry.basic import subtract_vectors
from compas.geometry.basic import cross_vectors
from compas.geometry.basic import dot_vectors
from compas.geometry.basic import multiply_matrix_vector
from compas.geometry.basic import length_vector
from compas.geometry.basic import allclose

from compas.geometry.transformations import _EPS
from compas.geometry.transformations import _SPEC2TUPLE
from compas.geometry.transformations import _NEXT_SPEC
from compas.geometry.transformations import identity_matrix

from compas.geometry.transformations.helpers import multiply_matrix_vector
from compas.geometry.transformations.helpers import identity_matrix


__author__    = ['Tom Van Mele', ]
__copyright__ = 'Copyright 2016 - Block Research Group, ETH Zurich'
__license__   = 'MIT License'
__email__     = 'vanmelet@ethz.ch'


__all__ = [
    'matrix_from_frame',
    'matrix_from_euler_angles',
    'matrix_from_axis_and_angle',
    'matrix_from_axis_angle_vector',
    'matrix_from_basis_vectors',
    'matrix_from_translation',
    'matrix_from_orthogonal_projection',
    'matrix_from_parallel_projection',
    'matrix_from_perspective_projection',
    'matrix_from_perspective_entries',
    'matrix_from_shear_entries',
    'matrix_from_shear',
    'matrix_from_scale_factors',

    'euler_angles_from_matrix',
    'axis_and_angle_from_matrix',
    'axis_angle_vector_from_matrix',
    'matrix_from_quaternion',
    'quaternion_from_matrix',
    'basis_vectors_from_matrix',
    'translation_from_matrix',
]


# ==============================================================================
# xforms
# ==============================================================================


def matrix_from_frame(frame):
    """Computes a change of basis transformation from world XY to the frame.

    Args:
        frame (:class:`compas.geometry.Frame`): a frame describing the targeted Cartesian
            coordinate system

    Example:
        >>> from compas.geometry import Frame
        >>> f = Frame([1, 1, 1], [0.68, 0.68, 0.27], [-0.67, 0.73, -0.15])
        >>> T = matrix_from_frame(f)
    """

    M = identity_matrix(4)
    M[0][0], M[1][0], M[2][0] = frame.xaxis
    M[0][1], M[1][1], M[2][1] = frame.yaxis
    M[0][2], M[1][2], M[2][2] = frame.zaxis
    M[0][3], M[1][3], M[2][3] = frame.point
    return M


def matrix_from_euler_angles(euler_angles, static=True, axes='xyz'):
    """Calculates a rotation matrix from Euler angles.

    In 3D space any orientation can be achieved by composing three elemental
    rotations, rotations about the axes (x,y,z) of a coordinate system. A
    triple of Euler angles can be interpreted in 24 ways, which depends on if
    the rotations are applied to a static (extrinsic) or rotating (intrinsic)
    frame and the order of axes.

    Args:
        euler_angles(:obj:`list` of :obj:`float`): Three numbers that represent
            the angles of rotations about the defined axes.
        static(:obj:`bool`, optional): If true the rotations are applied to a
            static frame. If not, to a rotational. Defaults to true.
        axes(:obj:`str`, optional): A 3 character string specifying order of
            the axes. Defaults to 'xyz'.

    Example:
        >>> ea1 = 1.4, 0.5, 2.3
        >>> args = True, 'xyz'
        >>> R = matrix_from_euler_angles(ea1, *args)
        >>> ea2 = euler_angles_from_matrix(R, *args)
        >>> allclose(ea1, ea2)
        True
    """

    global _SPEC2TUPLE
    global _NEXT_SPEC

    ai, aj, ak = euler_angles

    if static:
        firstaxis, parity, repetition, frame = _SPEC2TUPLE["s" + axes]
    else:
        firstaxis, parity, repetition, frame = _SPEC2TUPLE["r" + axes]

    i = firstaxis
    j = _NEXT_SPEC[i + parity]
    k = _NEXT_SPEC[i - parity + 1]

    if frame:
        ai, ak = ak, ai
    if parity:
        ai, aj, ak = -ai, -aj, -ak

    si, sj, sk = math.sin(ai), math.sin(aj), math.sin(ak)
    ci, cj, ck = math.cos(ai), math.cos(aj), math.cos(ak)
    cc, cs = ci * ck, ci * sk
    sc, ss = si * ck, si * sk

    M = [[1. if x == y else 0. for x in range(4)] for y in range(4)]
    if repetition:
        M[i][i] = cj
        M[i][j] = sj * si
        M[i][k] = sj * ci
        M[j][i] = sj * sk
        M[j][j] = -cj * ss + cc
        M[j][k] = -cj * cs - sc
        M[k][i] = -sj * ck
        M[k][j] = cj * sc + cs
        M[k][k] = cj * cc - ss
    else:
        M[i][i] = cj * ck
        M[i][j] = sj * sc - cs
        M[i][k] = sj * cc + ss
        M[j][i] = cj * sk
        M[j][j] = sj * ss + cc
        M[j][k] = sj * cs - sc
        M[k][i] = -sj
        M[k][j] = cj * si
        M[k][k] = cj * ci

    return M


def euler_angles_from_matrix(M, static=True, axes='xyz'):
    """Returns Euler angles from the rotation matrix M according to specified
        axis sequence and type of rotation.

    Args:
        M (:obj:`list` of :obj:`list` of :obj:`float`): The 3x3 or 4x4 matrix
            in row-major order.
        static(:obj:`bool`, optional): If true the rotations are applied to a
            static frame. If not, to a rotational. Defaults to True.
        axes(:obj:`str`, optional): A 3 character string specifying order of
            the axes. Defaults to 'xyz'.

    Returns:
        (:obj:`list` of :obj:`float`): The 3 Euler angles.

    Example:
        >>> ea1 = 1.4, 0.5, 2.3
        >>> args = True, 'xyz'
        >>> R = matrix_from_euler_angles(ea1, *args)
        >>> ea2 = euler_angles_from_matrix(R, *args)
        >>> allclose(ea1, ea2)
        True
    """

    global _SPEC2TUPLE
    global _NEXT_SPEC
    global _EPS

    if static:
        firstaxis, parity, repetition, frame = _SPEC2TUPLE["s" + axes]
    else:
        firstaxis, parity, repetition, frame = _SPEC2TUPLE["r" + axes]

    i = firstaxis
    j = _NEXT_SPEC[i + parity]
    k = _NEXT_SPEC[i - parity + 1]

    if repetition:
        sy = math.sqrt(M[i][j] * M[i][j] + M[i][k] * M[i][k])
        if sy > _EPS:
            ax = math.atan2(M[i][j], M[i][k])
            ay = math.atan2(sy, M[i][i])
            az = math.atan2(M[j][i], -M[k][i])
        else:
            ax = math.atan2(-M[j][k], M[j][j])
            ay = math.atan2(sy, M[i][i])
            az = 0.0
    else:
        cy = math.sqrt(M[i][i] * M[i][i] + M[j][i] * M[j][i])
        if cy > _EPS:
            ax = math.atan2(M[k][j], M[k][k])
            ay = math.atan2(-M[k][i], cy)
            az = math.atan2(M[j][i], M[i][i])
        else:
            ax = math.atan2(-M[j][k], M[j][j])
            ay = math.atan2(-M[k][i], cy)
            az = 0.0

    if parity:
        ax, ay, az = -ax, -ay, -az
    if frame:
        ax, az = az, ax

    return [ax, ay, az]


def matrix_from_axis_and_angle(axis, angle, point=None, rtype='list'):
    """Calculates a rotation matrix from an rotation axis, an angle and an
        optional point of rotation.

    Note:
        The rotation is based on the right hand rule, i.e. anti-clockwise
        if the axis of rotation points towards the observer.

    Args:
        axis (:obj:`list` of :obj:`float`): Three numbers that
            represent the axis of rotation
        angle (:obj:`float`): The rotation angle in radians.
        point (:obj:`list` of :obj:`float`, optional): A point to
            perform a rotation around an origin other than [0, 0, 0].

    Returns:
        (:obj:`list` of :obj:`list` of :obj:`float`): The matrix.

    Example:
        >>> axis1 = normalize_vector([-0.043, -0.254, 0.617])
        >>> angle1 = 0.1
        >>> R = matrix_from_axis_and_angle(axis1, angle1)
        >>> axis2, angle2 = axis_and_angle_from_matrix(R)
        >>> allclose(axis1, axis2)
        True
        >>> allclose([angle1], [angle2])
        True
    """
    if not point:
        point = [0.0, 0.0, 0.0]

    axis = list(axis)
    if length_vector(axis):
        axis = normalize_vector(axis)

    sina = math.sin(angle)
    cosa = math.cos(angle)

    R = [[cosa, 0.0, 0.0], [0.0, cosa, 0.0], [0.0, 0.0, cosa]]

    outer_product = [[axis[i] * axis[j] *
                      (1.0 - cosa) for i in range(3)] for j in range(3)]
    R = [[R[i][j] + outer_product[i][j]
          for i in range(3)] for j in range(3)]

    axis = scale_vector(axis, sina)
    m = [[0.0, -axis[2], axis[1]],
         [axis[2], 0.0, -axis[0]],
         [-axis[1], axis[0], 0.0]]

    M = [[1. if x == y else 0. for x in range(4)] for y in range(4)]
    for i in range(3):
        for j in range(3):
            R[i][j] += m[i][j]
            M[i][j] = R[i][j]

    # rotation about axis, angle AND point includes also translation
    t = subtract_vectors(point, multiply_matrix_vector(R, point))
    M[0][3] = t[0]
    M[1][3] = t[1]
    M[2][3] = t[2]

    if rtype == 'list':
        return M
    if rtype == 'array':
        from numpy import asarray
        return asarray(M)

    raise NotImplementedError


def matrix_from_axis_angle_vector(axis_angle_vector, point=[0, 0, 0]):
    """Calculates a rotation matrix from an axis-angle vector.

    Args:
        axis_angle_vector (:obj:`list` of :obj:`float`): Three numbers
            that represent the axis of rotation and angle of rotation
            through the vector's magnitude.
        point (:obj:`list` of :obj:`float`, optional): A point to
            perform a rotation around an origin other than [0, 0, 0].

    Example:
        >>> aav1 = [-0.043, -0.254, 0.617]
        >>> R = matrix_from_axis_angle_vector(aav1)
        >>> aav2 = axis_angle_vector_from_matrix(R)
        >>> allclose(aav1, aav2)
        True
    """
    axis = list(axis_angle_vector)
    angle = length_vector(axis_angle_vector)
    return matrix_from_axis_and_angle(axis, angle, point)


def axis_and_angle_from_matrix(M):
    """Returns the axis and the angle of the rotation matrix M.


    """
    epsilon = 0.01  # margin to allow for rounding errors
    epsilon2 = 0.1  # margin to distinguish between 0 and 180 degrees

    if ((math.fabs(M[0][1] - M[1][0]) < epsilon) and
        (math.fabs(M[0][2] - M[2][0]) < epsilon) and
            (math.fabs(M[1][2] - M[2][1]) < epsilon)):

        if ((math.fabs(M[0][1] + M[1][0]) < epsilon2) and
            (math.fabs(M[0][2] + M[2][0]) < epsilon2) and
            (math.fabs(M[1][2] + M[2][1]) < epsilon2) and
                (math.fabs(M[0][0] + M[1][1] + M[2][2] - 3) < epsilon2)):
            return [0, 0, 0], 0
        else:
            angle = math.pi
            xx = (M[0][0] + 1) / 2
            yy = (M[1][1] + 1) / 2
            zz = (M[2][2] + 1) / 2
            xy = (M[0][1] + M[1][0]) / 4
            xz = (M[0][2] + M[2][0]) / 4
            yz = (M[1][2] + M[2][1]) / 4
            root_half = math.sqrt(0.5)
            if ((xx > yy) and (xx > zz)):
                if (xx < epsilon):
                    axis = [0, root_half, root_half]
                else:
                    x = math.sqrt(xx)
                    axis = [x, xy / x, xz / x]
            elif (yy > zz):
                if (yy < epsilon):
                    axis = [root_half, 0, root_half]
                else:
                    y = math.sqrt(yy)
                    axis = [xy / y, y, yz / y]
            else:
                if (zz < epsilon):
                    axis = [root_half, root_half, 0]
                else:
                    z = math.sqrt(zz)
                    axis = [xz / z, yz / z, z]

            return axis, angle

    s = math.sqrt(
        (M[2][1] - M[1][2]) * (M[2][1] - M[1][2]) +
        (M[0][2] - M[2][0]) * (M[0][2] - M[2][0]) +
        (M[1][0] - M[0][1]) * (M[1][0] - M[0][1]))

    if (math.fabs(s) < 0.001):
        s = 1
    angle = math.acos((M[0][0] + M[1][1] + M[2][2] - 1) / 2)

    x = (M[2][1] - M[1][2]) / s
    y = (M[0][2] - M[2][0]) / s
    z = (M[1][0] - M[0][1]) / s

    return [x, y, z], angle


def axis_angle_vector_from_matrix(M):
    """Returns the axis-angle vector of the rotation matrix M.
    """
    axis, angle = axis_and_angle_from_matrix(M)
    return scale_vector(axis, angle)


def matrix_from_quaternion(quaternion):
    """Calculates a rotation matrix from quaternion coefficients.

    Args:
        quaternion (:obj:`list` of :obj:`float`): Four numbers that
            represents the four coefficient values of a quaternion.

    Raises:
        ValueError: If quaternion is invalid.

    Example:
        >>> q1 = [0.945, -0.021, -0.125, 0.303]
        >>> R = matrix_from_quaternion(q1)
        >>> q2 = quaternion_from_matrix(R)
        >>> allclose(q1, q2, tol=1e-03)
        True
    """
    q = quaternion
    n = q[0]**2 + q[1]**2 + q[2]**2 + q[3]**2  # dot product

    epsilon = 1.0e-15

    if n < epsilon:
        raise ValueError("Invalid quaternion, dot product must be != 0.")

    q = [v * math.sqrt(2.0 / n) for v in q]
    q = [[q[i] * q[j] for i in range(4)]
         for j in range(4)]  # outer_product

    rotation = [
        [1.0 - q[2][2] - q[3][3], q[1][2] - q[3][0], q[1][3] + q[2][0], 0.0],
        [q[1][2] + q[3][0], 1.0 - q[1][1] - q[3][3], q[2][3] - q[1][0], 0.0],
        [q[1][3] - q[2][0], q[2][3] + q[1][0], 1.0 - q[1][1] - q[2][2], 0.0],
        [0.0, 0.0, 0.0, 1.0]]
    return rotation


def quaternion_from_matrix(M):
    """Returns the 4 quaternion coefficients from a rotation matrix.

    Args:
        M (:obj:`list` of :obj:`list` of :obj:`float`): The rotation matrix.

    Returns:
        (:obj:`list` of :obj:`float`): The quaternion coefficients.

    Example:
        >>> q1 = [0.945, -0.021, -0.125, 0.303]
        >>> R = matrix_from_quaternion(q1)
        >>> q2 = quaternion_from_matrix(R)
        >>> allclose(q1, q2, tol=1e-03)
        True
    """

    qw, qx, qy, qz = 0, 0, 0, 0
    trace = M[0][0] + M[1][1] + M[2][2]

    if trace > 0.0:
        s = (0.5 / math.sqrt(trace + 1.0))
        qw = 0.25 / s
        qx = (M[2][1] - M[1][2]) * s
        qy = (M[0][2] - M[2][0]) * s
        qz = (M[1][0] - M[0][1]) * s

    elif ((M[0][0] > M[1][1]) and (M[0][0] > M[2][2])):
        s = 2.0 * math.sqrt(1.0 + M[0][0] - M[1][1] - M[2][2])
        qw = (M[2][1] - M[1][2]) / s
        qx = 0.25 * s
        qy = (M[0][1] + M[1][0]) / s
        qz = (M[0][2] + M[2][0]) / s

    elif (M[1][1] > M[2][2]):
        s = 2.0 * math.sqrt(1.0 + M[1][1] - M[0][0] - M[2][2])
        qw = (M[0][2] - M[2][0]) / s
        qx = (M[0][1] + M[1][0]) / s
        qy = 0.25 * s
        qz = (M[1][2] + M[2][1]) / s
    else:
        s = 2.0 * math.sqrt(1.0 + M[2][2] - M[0][0] - M[1][1])
        qw = (M[1][0] - M[0][1]) / s
        qx = (M[0][2] + M[2][0]) / s
        qy = (M[1][2] + M[2][1]) / s
        qz = 0.25 * s

    return [qw, qx, qy, qz]


def matrix_from_basis_vectors(xaxis, yaxis):
    """Creates a rotation matrix from basis vectors (= orthonormal vectors).

    Args:
        xaxis (:obj:`list` oof :obj:`float`): The x-axis of the frame.
        yaxis (:obj:`list` oof :obj:`float`): The y-axis of the frame.

    Example:
        >>> xaxis = [0.68, 0.68, 0.27]
        >>> yaxis = [-0.67, 0.73, -0.15]
        >>> R = matrix_from_basis_vectors(xaxis, yaxis)
    """
    xaxis = normalize_vector(list(xaxis))
    yaxis = normalize_vector(list(yaxis))
    zaxis = cross_vectors(xaxis, yaxis)
    yaxis = cross_vectors(zaxis, xaxis)  # correction

    R = identity_matrix(4)
    R[0][0], R[1][0], R[2][0] = xaxis
    R[0][1], R[1][1], R[2][1] = yaxis
    R[0][2], R[1][2], R[2][2] = zaxis
    return R


def basis_vectors_from_matrix(R):
    """Returns the basis vectors from the rotation matrix R.

    Raises:
        ValueError: If rotation matrix is invalid.

    Example:
        >>> from compas.geometry import Frame
        >>> f = Frame([0, 0, 0], [0.68, 0.68, 0.27], [-0.67, 0.73, -0.15])
        >>> R = matrix_from_frame(f)
        >>> xaxis, yaxis = basis_vectors_from_matrix(R)
    """
    xaxis = [R[0][0], R[1][0], R[2][0]]
    yaxis = [R[0][1], R[1][1], R[2][1]]
    zaxis = [R[0][2], R[1][2], R[2][2]]
    if not allclose(zaxis, cross_vectors(xaxis, yaxis)):
        raise ValueError("Matrix is invalid rotation matrix.")
    else:
        return [xaxis, yaxis]


def matrix_from_translation(translation, rtype='list'):
    """Returns a 4x4 translation matrix in row-major order.

    Args:
        translation (:obj:`list` of :obj:`float`): The x, y and z components
            of the translation.

    Example:
        >>> T = matrix_from_translation([1, 2, 3])
    """
    M = identity_matrix(4)
    M[0][3] = float(translation[0])
    M[1][3] = float(translation[1])
    M[2][3] = float(translation[2])

    if rtype == 'list':
        return M
    if rtype == 'array':
        from numpy import asarray
        return asarray(M)

    raise NotImplementedError


def translation_from_matrix(M):
    """Returns the 3 values of translation from the matrix M.
    """
    return [M[0][3], M[1][3], M[2][3]]


def matrix_from_orthogonal_projection(point, normal):
    """Returns an orthogonal projection matrix to project onto a plane \
        defined by point and normal.

    Args:
        point(:obj:`list` of :obj:`float`)
        normal(:obj:`list` of :obj:`float`)

    Example:
        >>> point = [0, 0, 0]
        >>> normal = [0, 0, 1]
        >>> P = matrix_from_orthogonal_projection(point, normal)
    """
    T = identity_matrix(4)
    normal = normalize_vector(normal)

    for j in range(3):
        for i in range(3):
            T[i][j] -= normal[i] * normal[j]  # outer_product

    T[0][3], T[1][3], T[2][3] = scale_vector(
        normal, dot_vectors(point, normal))
    return T


def matrix_from_parallel_projection(point, normal, direction):
    """Returns an parallel projection matrix to project onto a plane defined \
        by point, normal and direction.

    Args:
        point(:obj:`list` of :obj:`float`)
        normal(:obj:`list` of :obj:`float`)
        direction(:obj:`list` of :obj:`float`)

    Example:
        >>> point = [0, 0, 0]
        >>> normal = [0, 0, 1]
        >>> direction = [1, 1, 1]
        >>> P = matrix_from_parallel_projection(point, normal, direction)
    """
    T = identity_matrix(4)
    normal = normalize_vector(normal)

    scale = dot_vectors(direction, normal)
    for j in range(3):
        for i in range(3):
            T[i][j] -= direction[i] * normal[j] / scale

    T[0][3], T[1][3], T[2][3] = scale_vector(
        direction, dot_vectors(point, normal) / scale)
    return T


def matrix_from_perspective_projection(point, normal, perspective):
    """Returns an perspective projection matrix to project onto a plane \
        defined by point, normal and perspective.

    Args:
        point(:obj:`list` of :obj:`float`)
        normal(:obj:`list` of :obj:`float`)
        perspective(:obj:`list` of :obj:`float`)

    Example:
        >>> point = [0, 0, 0]
        >>> normal = [0, 0, 1]
        >>> perspective = [1, 1, 0]
        >>> P = matrix_from_perspective_projection(point, normal, perspective)
    """
    T = identity_matrix(4)
    normal = normalize_vector(normal)

    T[0][0] = T[1][1] = T[2][2] = dot_vectors(
        subtract_vectors(perspective, point), normal)

    for j in range(3):
        for i in range(3):
            T[i][j] -= perspective[i] * normal[j]

    T[0][3], T[1][3], T[2][3] = scale_vector(
        perspective, dot_vectors(point, normal))
    for i in range(3):
        T[3][i] -= normal[i]
    T[3][3] = dot_vectors(perspective, normal)
    return T


def matrix_from_perspective_entries(perspective):
    """Returns a matrix from perspective entries.

    Args:
        values(:obj:`list` of :obj:`float`): The 4 perspective entries of a
            matrix.
    """
    M = identity_matrix(4)
    M[3][0] = float(perspective[0])
    M[3][1] = float(perspective[1])
    M[3][2] = float(perspective[2])
    M[3][3] = float(perspective[3])
    return M


def matrix_from_shear_entries(shear_entries):
    """Returns a shear matrix from the 3 factors for x-y, x-z, and y-z axes.

    Args:
        shear_entries (:obj:`list` of :obj:`float`): The 3 shear factors for
            x-y, x-z, and y-z axes.

    Example:
        >>> Sh = matrix_from_shear_entries([1, 2, 3])
    """
    M = identity_matrix(4)
    M[0][1] = float(shear_entries[0])
    M[0][2] = float(shear_entries[1])
    M[1][2] = float(shear_entries[2])
    return M


def matrix_from_shear(angle, direction, point, normal):
    """Constructs a shear matrix by an angle along the direction vector on \
        the shear plane (defined by point and normal).

    A point P is transformed by the shear matrix into P" such that
    the vector P-P" is parallel to the direction vector and its extent is
    given by the angle of P-P'-P", where P' is the orthogonal projection
    of P onto the shear plane (defined by point and normal).

    Args:
        angle (:obj:`float`): The angle in radians.
        direction (:obj:`list` of :obj:`float`): The direction vector as
            list of 3 numbers. It must be orthogonal to the normal vector.
        point (:obj:`list` of :obj:`float`): The point of the shear plane
            as list of 3 numbers.
        normal (:obj:`list` of :obj:`float`): The normal of the shear plane
            as list of 3 numbers.

    Raises:
        ValueError: If direction and normal are not orthogonal.

    Example:
        >>> angle = 0.1
        >>> direction = [0.1, 0.2, 0.3]
        >>> point = [4, 3, 1]
        >>> normal = cross_vectors(direction, [1, 0.3, -0.1])
        >>> S = matrix_from_shear(angle, direction, point, normal)
    """

    normal = normalize_vector(normal)
    direction = normalize_vector(direction)

    if math.fabs(dot_vectors(normal, direction)) > _EPS:
        raise ValueError('Direction and normal vectors are not orthogonal')

    angle = math.tan(angle)
    M = [[1. if i == j else 0. for i in range(4)] for j in range(4)]

    for j in range(3):
        for i in range(3):
            M[i][j] += angle * direction[i] * normal[j]

    M[0][3], M[1][3], M[2][3] = scale_vector(
        direction, -angle * dot_vectors(point, normal))

    return M


def matrix_from_scale_factors(scale_factors, rtype='list'):
    """Returns a 4x4 scaling transformation.

    Args:
        scale_factors (:obj:`list` of :obj:`float`):  Three numbers defining
            the scaling factors in x, y, and z respectively.

    Example:
        >>> Sc = matrix_from_scale_factors([1, 2, 3])
    """
    M = identity_matrix(4)
    M[0][0] = float(scale_factors[0])
    M[1][1] = float(scale_factors[1])
    M[2][2] = float(scale_factors[2])

    if rtype == 'list':
        return M
    if rtype == 'array':
        from numpy import asarray
        return asarray(M)

    raise NotImplementedError


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":

    pass

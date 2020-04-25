import numpy


def magnitude(mag_vector):
    """Accepts a vector parameter and returns magnitude"""
    mag = 0
    for component in mag_vector:
        mag += component ** 2

    mag = numpy.sqrt(mag)

    return mag


def transform(rover_coordinates, destination_coordinates):
    """Accepts two points and returns a vector"""
    transformed_destination = []
    for index, element in enumerate(rover_coordinates):
        transformed_destination.append(destination_coordinates[index] - rover_coordinates[index])

    return transformed_destination


def cardinal_heading(vector):
    """
    Finds the cardinal heading, represented as an integer corresponding with the 8 cardinal directions:
    E: 0, NE: 1, N: 2, NW: 3, W: 4, SW: 5, S: 6, SE: 7
    :param vector: accepts a vector tuple
    :return: returns an integer cardinal direction
    """
    # Intermediate cardinal coordinate boundaries (constant)
    NNW = 1.96349540849362
    NWW = 2.74889357189107
    SWW = 3.53429173528852
    SSW = 4.31968989868597
    SSE = 5.10508806208342
    SEE = 5.89048622548087
    NEE = 0.392699081698724
    NNE = 1.17809724509617

    x = vector[0]
    y = vector[1]

    heading = None

    if x == 0 and y == 0:
        return heading
    elif x < 0 and y == 0:
        heading = (numpy.pi * 3 / 2)
    elif x > 0 and y == 0:
        heading = (numpy.pi / 2)
    elif x == 0 and y < 0:
        heading = numpy.pi
    elif x == 0 and y > 0:
        heading = 0
    elif x < 0 and y < 0:
        heading = (numpy.pi * 3 / 2) - numpy.arctan((x / y))
    elif x < 0:
        heading = (numpy.pi / 2) - numpy.arctan((x / y))
    elif y < 0:
        heading = (numpy.pi * 3 / 2) - numpy.arctan((x / y))
    else:
        heading = (numpy.pi / 2) - numpy.arctan((x / y))

    if NNE > heading > NEE:
        return 1    # NE
    if NNW > heading > NNE:
        return 2    # N
    if NWW > heading > NNW:
        return 3    # NW
    if SWW > heading > NWW:
        return 4    # W
    if SSW > heading > SWW:
        return 5    # SW
    if SSE > heading > SSW:
        return 6    # S
    if SEE > heading > SSE:
        return 7    # SE
    if NEE > heading or heading > SEE:
        return 0    # E




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


#### FIX DOCUMENTATION
def angle(angle_vector, theta_angle, cardinal):
    """Accepts a vector and returns an angle dictionary. Key will be the greek letter names.
    2D vectors use 'theta'
    3D vectors use cylindrical coordinate system; 'phi' and 'rho'"""

    # Cardinal coordinate boundaries
    NNW = 1.96349540849362
    NWW = 2.74889357189107
    SWW = 3.53429173528852
    SSW = 4.31968989868597
    SSE = 5.10508806208342
    SEE = 5.89048622548087
    NEE = 0.392699081698724
    NNE = 1.17809724509617

    angle_dict = {}

    if len(angle_vector) == 2 or theta_angle is True:
        x = angle_vector[0]
        y = angle_vector[1]

        if x < 0 and y == 0:
            angle_dict["theta"] = (numpy.pi * 3 / 2)
        elif x > 0 and y == 0:
            angle_dict["theta"] = (numpy.pi / 2)
        elif x == 0 and y < 0:
            angle_dict["theta"] = numpy.pi
        elif x == 0 and y > 0:
            angle_dict["theta"] = 0
        elif x < 0 and y < 0:
            angle_dict["theta"] = (numpy.pi * 3 / 2) - numpy.arctan((x / y))
        elif x < 0:
            angle_dict["theta"] = (numpy.pi / 2) - numpy.arctan((x / y))
        elif y < 0:
            angle_dict["theta"] = (numpy.pi * 3 / 2) - numpy.arctan((x / y))
        else:
            angle_dict["theta"] = (numpy.pi / 2) - numpy.arctan((x / y))

        if cardinal is True:
            theta = angle_dict["theta"]
            if NNE > theta > NEE:
                angle_dict["theta"] = "NE"
            if NNW > theta > NNE:
                angle_dict["theta"] = "N"
            if NWW > theta > NNW:
                angle_dict["theta"] = "NW"
            if SWW > theta > NWW:
                angle_dict["theta"] = "W"
            if SSW > theta > SWW:
                angle_dict["theta"] = "SW"
            if SSE > theta > SSW:
                angle_dict["theta"] = "S"
            if SEE > theta > SSE:
                angle_dict["theta"] = "SE"
            if NEE > theta or theta > SEE:
                angle_dict["theta"] = "E"

    elif len(angle_vector) == 3:
        x = angle_vector[0]
        y = angle_vector[1]
        z = angle_vector[2]

        angle_dict["phi"] = numpy.arctan(x / y)
        angle_dict["rho"] = numpy.arctan(x / z)
    else:
        print("not a 2d or 3d vector")

    return angle_dict


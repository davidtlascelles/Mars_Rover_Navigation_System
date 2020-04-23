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


def angle(angle_vector):
    """Accepts a vector and returns an angle dictionary. Key will be the greek letter names.
    2D vectors use 'theta'
    3D vectors use cylindrical coordinate system; 'phi' and 'rho'"""

    angle_dict = {}
    if len(angle_vector) == 3:
        x = angle_vector[0]
        y = angle_vector[1]
        z = angle_vector[2]

        angle_dict["phi"] = numpy.arctan(x/y)
        angle_dict["rho"] = numpy.arctan(x/z)

    elif len(angle_vector) == 2:
        x = angle_vector[0]
        y = angle_vector[1]

        angle_dict["theta"] = numpy.arctan((x/y))
    else:
        print("not a 2d or 3d vector")

    return angle_dict


test_a_2d = [34, 56]
test_b_2d = [21, 32]

test_a_3d = [34, 56, 10]
test_b_3d = [21, 32, 23]

test_2d_vector = transform(test_a_2d, test_b_2d)
print(f"Test 2D vector: \t{test_2d_vector}")
print(f"Test 2D magnitude: \t{magnitude(test_2d_vector):.2f}")
print(f"Test 2D angle: \t{angle(test_2d_vector)}")
print()

test_3d_vector = transform(test_a_3d, test_b_3d)
print(f"Test 3D vector: \t{test_3d_vector}")
print(f"Test 3D magnitude: \t{magnitude(test_3d_vector):.2f}")
print(f"Test 3D angle: \t{angle(test_3d_vector)}")

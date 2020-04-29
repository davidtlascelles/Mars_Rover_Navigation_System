import numpy


class Vector:

    def __init__(self, start=(0, 0), end=(0, 0), three_dimensional=True):
        self.__starting_coordinate = start
        self.__ending_coordinate = end

        self.vector = self.__make_vector(three_dimensions=False)
        self.radian_heading = self.__heading()
        self.cardinal_heading = self.__heading(False)
        self.magnitude = self.__magnitude()

    def __magnitude(self):
        """Accepts a vector parameter and returns magnitude"""
        mag = 0
        for component in self.vector:
            mag += numpy.power(component, 2)

        mag = numpy.sqrt(mag)

        return mag

    def __make_vector(self, three_dimensions):
        """Accepts two points and returns a vector"""
        transformed_destination = []
        if three_dimensions is False or len(self.__starting_coordinate) == 2:
            transformed_destination.append(self.__ending_coordinate[0] - self.__starting_coordinate[0])
            transformed_destination.append(self.__ending_coordinate[1] - self.__starting_coordinate[1])
        else:
            for index, element in enumerate(self.__starting_coordinate):
                transformed_destination.append(self.__ending_coordinate[index] - self.__starting_coordinate[index])

        return transformed_destination

    def __heading(self, radians=True):
        """
        Finds the cardinal heading, represented as an integer corresponding with the 8 cardinal directions:
        E: 0, NE: 1, N: 2, NW: 3, W: 4, SW: 5, S: 6, SE: 7
        :param radians: changes return type to heading in radians
        :return: returns an integer cardinal direction heading
        """
        x = self.vector[0]
        y = self.vector[1]

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

        if radians is True:
            return heading
        return self.__cardinal_heading()

    def __cardinal_heading(self):
        """
        Support method for heading(), looks up cardinal direction from radian value
        :return: cardinal direction heading integer
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

        if NNE > self.radian_heading > NEE:
            return 1  # NE
        if NNW > self.radian_heading > NNE:
            return 2  # N
        if NWW > self.radian_heading > NNW:
            return 3  # NW
        if SWW > self.radian_heading > NWW:
            return 4  # W
        if SSW > self.radian_heading > SWW:
            return 5  # SW
        if SSE > self.radian_heading > SSW:
            return 6  # S
        if SEE > self.radian_heading > SSE:
            return 7  # SE
        if NEE > self.radian_heading or self.radian_heading > SEE:
            return 0  # E

    def set_start(self, start):
        self.__starting_coordinate = start

    def set_end(self, end):
        self.__ending_coordinate = end

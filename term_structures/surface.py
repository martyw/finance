from scipy import interpolate


class Surface:
    def __init__(self, first_axis: list, second_axis: list, values: list):
        self.first_axis = first_axis
        self.second_axis = second_axis
        self.values = values
        self.interp = interpolate.interp2d(self.first_axis,
                                           self.second_axis,
                                           self.values)

    def __call__(self, x, y) -> float:
        return float(self.interp(x, y))

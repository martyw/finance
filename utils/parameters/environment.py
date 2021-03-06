import unittest
from datetime import date


class Environment:
    def __init__(self, vd=date(2008, 1, 1)):
        self._valuation_date = vd
        self.curves = {}
        self.surfaces = {}
        self.constants = {}

    @property
    def valuation_date(self):
        return self._valuation_date

    @valuation_date.setter
    def valuation_date(self, val_date):
        self._valuation_date = val_date

    def relative_date(self, rel_date):
        ret = (rel_date - self._valuation_date).days
        assert ret > 0, "date before pricing date"
        return ret

    def add_curve(self, key, curve):
        if key in self.curves:
            del self.curves[key]
        self.curves[key] = curve

    def add_surface(self, key, surface):
        if key in self.surfaces:
            del self.surfaces[key]
        self.surfaces[key] = surface

    def add_constant(self, key, constant):
        if key in self.constants:
            del self.constants[key]
        self.constants[key] = constant

    def get_curve(self, key):
        return self.curves[key]

    def get_surface(self, key):
        return self.surfaces[key]

    def get_constant(self, key):
        return self.constants[key]

import torch


__all__ = [
    'Constraint',
    'boolean',
    'dependent',
    'dependent_property',
    'greater_than',
    'integer_interval',
    'interval',
    'is_dependent',
    'lower_triangular',
    'nonnegative_integer',
    'positive',
    'real',
    'simplex',
    'unit_interval',
]


class Constraint(object):
    """
    Abstract base class for constraints.

    A constraint object represents a region over which a variable is valid,
    e.g. within which a variable can be optimized.
    """
    def check(self, value):
        """
        Returns a byte tensor of `sample_shape + batch_shape` indicating
        whether each event in value satisfies this constraint.
        """
        raise NotImplementedError


class _Dependent(Constraint):
    """
    Placeholder for variables whose support depends on other variables.
    These variables obey no simple coordinate-wise constraints.
    """
    def check(self, x):
        raise ValueError('Cannot determine validity of dependent constraint')


def is_dependent(constraint):
    return isinstance(constraint, _Dependent)


class _DependentProperty(property, _Dependent):
    """
    Decorator that extends @property to act like a `Dependent` constraint when
    called on a class and act like a property when called on an object.

    Example::

        class Uniform(Distribution):
            def __init__(self, low, high):
                self.low = low
                self.high = high
            @constraints.dependent_property
            def support(self):
                return constraints.interval(self.low, self.high)
    """
    pass


class _Boolean(Constraint):
    """
    Constrain to the two values `{0, 1}`.
    """
    def check(self, value):
        return (value == 0) | (value == 1)


class _NonnegativeInteger(Constraint):
    """
    Constrain to non-negative integers `{0, 1, 2, ...}`.
    """
    def check(self, value):
        return (value % 1 == 0) & (value >= 0)


class _IntegerInterval(Constraint):
    """
    Constrain to an integer interval `[lower_bound, upper_bound]`.
    """
    def __init__(self, lower_bound, upper_bound):
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

    def check(self, value):
        return (value % 1 == 0) & (self.lower_bound <= value) & (value <= self.upper_bound)


class _Real(Constraint):
    """
    Trivially constrain to the extended real line `[-inf, inf]`.
    """
    def check(self, value):
        return value == value  # False for NANs.


class _GreaterThan(Constraint):
    """
    Constrain to a real half line `[lower_bound, inf]`.
    """
    def __init__(self, lower_bound):
        self.lower_bound = lower_bound

    def check(self, value):
        return self.lower_bound <= value


class _Interval(Constraint):
    """
    Constrain to a real interval `[lower_bound, upper_bound]`.
    """
    def __init__(self, lower_bound, upper_bound):
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

    def check(self, value):
        return (self.lower_bound <= value) & (value <= self.upper_bound)


class _Simplex(Constraint):
    """
    Constrain to the unit simplex in the innermost (rightmost) dimension.
    Specifically: `x >= 0` and `x.sum(-1) == 1`.
    """
    def check(self, value):
        return (value >= 0) & ((value.sum(-1, True) - 1).abs() < 1e-6)


class _LowerTriangular(Constraint):
    """
    Constrain to lower-triangular square matrices.
    """
    def check(self, value):
        return (torch.tril(value) == value).min(-1).min(-1)


# Public interface.
dependent = _Dependent()
dependent_property = _DependentProperty
boolean = _Boolean()
nonnegative_integer = _NonnegativeInteger()
integer_interval = _IntegerInterval
real = _Real()
positive = _GreaterThan(0)
greater_than = _GreaterThan
unit_interval = _Interval(0, 1)
interval = _Interval
simplex = _Simplex()
lower_triangular = _LowerTriangular()

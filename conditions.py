from functions import *
from constants import *


# Represents an expression of type boolean
class Condition:
    def __init__(self):
        self.wrapParens = True

    def __str__(self):
        return "Condition"

    def wrap(self):
        if self.wrapParens:
            return "(" + str(self) + ")"
        else:
            return str(self)

    def convert(self, e):
        if isinstance(e, int):
            return Num(e)
        elif e == a:
            return A()
        elif e == b:
            return B()
        elif e == c:
            return C()
        elif e == x:
            return X()
        elif e == y:
            return Y()
        elif isinstance(e, str):
            return LogicVar(e)
        elif isinstance(e, Math) or isinstance(e, Condition):
            return e
        else:
            raise ValueError("expr" + str(e) +
                             "is not a number, variable, mathematical expression, or boolean condition")

    def simplify(self):
        return self

    def flatten(self):
        return [self]

    def eval(self):
        return False

    def bottom(self):
        return BOTTOM

    def top(self):
        return TOP


# Used to represent the set of all integers
class All(Condition):
    def __init__(self):
        super().__init__()
        self.wrapParens = False

    def __str__(self):
        return "True"

    def eval(self):
        return True


# Used to represent the empty set of integers
class Empty(Condition):
    def __init__(self):
        super().__init__()
        self.wrapParens = False

    def __str__(self):
        return "False"

    def eval(self):
        return False


# Logical variables (for now, just used for debugging)
class LogicVar(Condition):
    def __init__(self, name):
        super().__init__()
        self.wrapParens = False
        self.name = name

    def __str__(self):
        return self.name


# (Boolean, Boolean) -> Boolean
class And(Condition):
    def __init__(self, left, right):
        super().__init__()
        self.left = self.convert(left)
        self.right = self.convert(right)

    def __str__(self):
        return self.left.wrap() + " && " + self.right.wrap()

    def simplify(self):
        return And(self.left.simplify(), self.right.simplify())

    def flatten(self):
        l = self.left.flatten()
        r = self.right.flatten()
        result = []
        for first in l:
            for second in r:
                result.append(And(first, second))
        return result

    def eval(self):
        l = self.left.eval()
        if not l:
            return False
        return self.right.eval()


# (Boolean, Boolean) -> Boolean
class Or(Condition):
    def __init__(self, left, right):
        super().__init__()
        self.left = self.convert(left)
        self.right = self.convert(right)

    def __str__(self):
        return self.left.wrap() + " || " + self.right.wrap()

    def simplify(self):
        return Or(self.left.simplify(), self.right.simplify())

    def flatten(self):
        l = self.left.flatten()
        r = self.right.flatten()
        return l + r

    def eval(self):
        l = self.left.eval()
        if l:
            return True
        return self.right.eval()


# Binary conditions of the form (Int, Int) -> Boolean
class BinaryCondition(Condition):
    def __init__(self, left, right):
        super().__init__()
        self.left = self.convert(left)
        self.right = self.convert(right)

    def solve(self):
        return self, False


# (Int, Int) -> Boolean
class Equal(BinaryCondition):
    def __init__(self, left, right):
        super().__init__(left, right)

    def __str__(self):
        return str(self.left) + " == " + str(self.right)

    def simplify(self):
        l = self.left.simplify()
        r = self.right.simplify()
        lVal, lExists = l.eval()
        rVal, rExists = r.eval()

        # Transform c == e to e == c
        if lExists:
            temp = l
            l = r
            r = temp

        # Transform e + a == b to e == b - a
        if isinstance(l, Add):
            lrVal, lrExists = l.right.eval()
            if lrExists:
                r = Sub(r, l.right).simplify()
                l = l.left

        # Transform e - a == b to e == b + a
        if isinstance(l, Add):
            lrVal, lrExists = l.right.eval()
            if lrExists:
                r = Add(r, l.right).simplify()
                l = l.left

        # Transform a * e == b to e == b/a if b is divisible by a and a is nonzero
        rVal, rExists = r.eval()
        if rExists:
            if isinstance(l, Mult):
                llVal, llExists = l.left.eval()
                if llExists and llVal != 0 and rVal % llVal == 0:
                    l = l.right
                    r = Num(int(rVal / llVal))

        return Equal(l, r)

    def solve(self):
        if isinstance(self.left, A):
            return self, True
        elif isinstance(self.left, Add):
            l = self.left.left
            r = Sub(self.right, self.left.right).simplify()
            return Equal(l, r).simplify().solve()
        elif isinstance(self.left, Mult):
            if self.left.right.compare(self.right) == 0:
                l = self.left.left
                r = Num(1)
                return Equal(l, r).solve()
            else:
                rVal, rExists = self.right.eval()
                if rExists and rVal == 0:
                    l = self.left.left
                    r = self.right
                    return Equal(l, r).solve()
                else:
                    return self, False
        elif isinstance(self.left, Mod):
            if isinstance(self.left.left, A):
                return self, True
            else:
                return self, False
        else:
            return self, False

    def eval(self):
        return self.left.compare(self.right) == 0


# (Int, Int) -> Boolean
class Greater(BinaryCondition):
    def __init__(self, left, right):
        super().__init__(left, right)

    def __str__(self):
        return str(self.left) + " > " + str(self.right)

    def simplify(self):
        l = self.left.simplify()
        r = self.right.simplify()
        lVal, lExists = l.eval()
        rVal, rExists = r.eval()

        # Transform c > e to e < c
        swap = False
        if lExists:
            temp = l
            l = r
            r = temp
            swap = True

        # Transform e + a > b to e > b - a
        if isinstance(l, Add):
            lrVal, lrExists = l.right.eval()
            if lrExists:
                r = Sub(r, l.right).simplify()
                l = l.left

        # Transform e - a > b to e > b + a
        if isinstance(l, Add):
            lrVal, lrExists = l.right.eval()
            if lrExists:
                r = Add(r, l.right).simplify()
                l = l.left

        if swap:
            return Less(l, r)
        else:
            return Greater(l, r)

    def eval(self):
        lVal, lExists = self.left.eval()
        if not lExists:
            return False
        rVal, rExists = self.right.eval()
        return rExists and lVal > rVal


# (Int, Int) -> Boolean
class Geq(BinaryCondition):
    def __init__(self, left, right):
        super().__init__(left, right)

    def __str__(self):
        return str(self.left) + " >= " + str(self.right)

    def simplify(self):
        l = self.left.simplify()
        r = self.right.simplify()
        lVal, lExists = l.eval()
        rVal, rExists = r.eval()

        # Transform c >= e to e <= c
        swap = False
        if lExists:
            temp = l
            l = r
            r = temp
            swap = True

        # Transform e + a >= b to e >= b - a
        if isinstance(l, Add):
            lrVal, lrExists = l.right.eval()
            if lrExists:
                r = Sub(r, l.right).simplify()
                l = l.left

        # Transform e - a >= b to e >= b + a
        if isinstance(l, Add):
            lrVal, lrExists = l.right.eval()
            if lrExists:
                r = Add(r, l.right).simplify()
                l = l.left

        if swap:
            return Leq(l, r)
        else:
            return Geq(l, r)

    def eval(self):
        lVal, lExists = self.left.eval()
        if not lExists:
            return False
        rVal, rExists = self.right.eval()
        return rExists and lVal >= rVal


# (Int, Int) -> Boolean
class Less(BinaryCondition):
    def __init__(self, left, right):
        super().__init__(left, right)

    def __str__(self):
        return str(self.left) + " < " + str(self.right)

    def simplify(self):
        l = self.left.simplify()
        r = self.right.simplify()
        lVal, lExists = l.eval()
        rVal, rExists = r.eval()

        # Transform c < e to e > c
        swap = False
        if lExists:
            temp = l
            l = r
            r = temp
            swap = True

        # Transform e + a < b to e < b - a
        if isinstance(l, Add):
            lrVal, lrExists = l.right.eval()
            if lrExists:
                r = Sub(r, l.right).simplify()
                l = l.left

        # Transform e - a < b to e < b + a
        if isinstance(l, Add):
            lrVal, lrExists = l.right.eval()
            if lrExists:
                r = Add(r, l.right).simplify()
                l = l.left

        if swap:
            return Greater(l, r)
        else:
            return Less(l, r)

    def eval(self):
        lVal, lExists = self.left.eval()
        if not lExists:
            return False
        rVal, rExists = self.right.eval()
        return rExists and lVal < rVal


# (Int, Int) -> Boolean
class Leq(BinaryCondition):
    def __init__(self, left, right):
        super().__init__(left, right)

    def __str__(self):
        return str(self.left) + " <= " + str(self.right)

    def simplify(self):
        l = self.left.simplify()
        r = self.right.simplify()
        lVal, lExists = l.eval()
        rVal, rExists = r.eval()

        # Transform c <= e to e >= c
        swap = False
        if lExists:
            temp = l
            l = r
            r = temp
            swap = True

        # Transform e + a <= b to e <= b - a
        if isinstance(l, Add):
            lrVal, lrExists = l.right.eval()
            if lrExists:
                r = Sub(r, l.right).simplify()
                l = l.left

        # Transform e - a <= b to e <= b + a
        if isinstance(l, Add):
            lrVal, lrExists = l.right.eval()
            if lrExists:
                r = Add(r, l.right).simplify()
                l = l.left

        if swap:
            return Geq(l, r)
        else:
            return Leq(l, r)

    def eval(self):
        lVal, lExists = self.left.eval()
        if not lExists:
            return False
        rVal, rExists = self.right.eval()
        return rExists and lVal <= rVal

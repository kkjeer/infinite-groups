from enum import IntEnum
from functools import cmp_to_key

# Convenient shorthands that allow consumers to create integer functions
# using these variable names rather than calling N(), X(), or Y()
# E.g. consumers can call Add(x, y) rather than Add(X(), Y())
x = "should_create_x"
y = "should_create_y"
a = "should_create_a"
b = "should_create_b"
c = "should_create_c"

# Different kinds of integer expressions
MathKind = IntEnum(
    'MathKind', 'Mult Add Sub Div Mod Minus A B C X Y Num BinaryMath Math')


# Represents a mathematical function that returns an integer.
# Specific kinds of functions should inherit from Math.
class Math:
    def __init__(self):
        self.kind = MathKind.Math
        self.wrapParens = False

    def convert(self, expr):
        if isinstance(expr, int):
            return Num(expr)
        elif expr == a:
            return A()
        elif expr == b:
            return B()
        elif expr == c:
            return C()
        elif expr == x:
            return X()
        elif expr == y:
            return Y()
        elif isinstance(expr, Math):
            return expr
        else:
            raise ValueError("expr" + str(expr) +
                             "is not a number, variable, or mathematical expression")

    def __str__(self):
        return "Math"

    # Returns a string representation that wraps this expression in parentheses
    # if necessary. This allows string representations such as (x + y) * z.
    def wrap(self):
        if self.wrapParens:
            return "(" + str(self) + ")"
        else:
            return str(self)

    # Returns the integer value of this expression (if there is one).
    def eval(self):
        return 0, False

    # Returns a simplified expression by applying mathematical rules such as
    # 1 * e == e, e + 0 == e, e - e == 0, etc.
    def simplify(self):
        return self

    # Returns a list of expressions that coalesce the children of commutative
    # and associative operators.
    # For example, Add(Add(x, y), z) will be flattened to [x, y, z].
    def flatten(self, operator):
        return [self]

    # If this expression can be expressed as c * v, where c is a constant
    # and v is a variable, return (c, v, True).
    def getCoeff(self):
        if self.isVariable():
            return 1, self, True
        else:
            return 0, self, False

    # Returns true if this expression is a variable (A, B, C, X, or Y).
    def isVariable(self):
        return False

    # If this expression is a variable, return the name of the variable as
    # a string.
    def getVariableName(self):
        return ""

    # Returns an integer indicating the lexicographic comparison of this
    # expression with the given other expression.
    def compare(self, other):
        selfVal, selfExists = self.eval()
        otherVal, otherExists = other.eval()
        if selfExists:
            if otherExists:
                if selfVal < otherVal:
                    return -1
                elif selfVal > otherVal:
                    return 1
                else:
                    return 0
            else:
                return 1
        elif otherExists:
            return -1
        else:
            selfVar = self.getVariableName()
            otherVar = other.getVariableName()
            varCmp = 2
            if selfVar != "" and otherVar != "":
                if selfVar < otherVar:
                    varCmp = -1
                elif selfVar > otherVar:
                    varCmp = 1
            if varCmp != 2:
                return varCmp
            elif int(self.kind) < int(other.kind):
                return -1
            elif self.kind > other.kind:
                return 1
            else:
                return 0


# Binary integer functions of the form e1 op e2, where op is +, *, - or /.
class BinaryMath(Math):
    def __init__(self, left, right):
        super().__init__()
        self.kind = MathKind.BinaryMath
        self.wrapParens = True
        self.left = self.convert(left)
        self.right = self.convert(right)

    # Given integers x and y, return an integer that evaluates x and y.
    # This function should be overridden by subclasses to determine how
    # to use x and y to get the integer result.
    def func(self, x, y):
        return 0

    # Creates a new binary function. Subclasses should override this method.
    def make(self, left, right):
        return BinaryMath(left, right)

    # Evaluates this function to an integer if possible.
    def eval(self):
        leftVal, leftExists = self.left.eval()
        if leftExists:
            rightVal, rightExists = self.right.eval()
            return self.func(leftVal, rightVal), leftExists and rightExists
        else:
            return 0, False

    # Returns a simplified version of this function using mathematical rules.
    def simplify(self):
        val, valExists = self.eval()
        if valExists:
            return Num(val)
        l = self.left.simplify()
        r = self.right.simplify()
        res = self.make(l, r)
        return res

    # Returns an integer comparing this function to the given other function.
    def compare(self, other):
        cmp = super().compare(other)
        if cmp != 0:
            return cmp
        else:
            leftCmp = self.left.compare(other.left)
            if leftCmp != 0:
                return leftCmp
            else:
                return self.right.compare(other.right)


# (Int, Int) -> Int
class Add(BinaryMath):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.kind = MathKind.Add

    def __str__(self):
        return self.left.wrap() + " + " + self.right.wrap()

    # To evaluate an addition operator given two numbers x and y, add x and y.
    def func(self, x, y):
        return x + y

    # Creates a new addition operator.
    def make(self, left, right):
        f = Add(left, right).flatten("+")
        if len(f) == 1:
            result = f[0]
            if isinstance(result, Add):
                return result
            else:
                return result.simplify()
        val = 0
        idx = len(f) - 1
        eltVal, eltExists = f[idx].eval()
        while eltExists and idx >= 1:
            val += eltVal
            eltVal, eltExists = f[idx - 1].eval()
            idx = idx - 1

        def getFromIdx(idx):
            if idx == 0:
                return f[idx]
            else:
                return Add(getFromIdx(idx - 1), f[idx])

        rest = getFromIdx(idx)
        if val == 0:
            return rest
        else:
            return Add(rest, Num(val))

    # Recursively coalesces the children of + operators, since addition is
    # commutative and associative.
    def flatten(self, operator):
        if operator != "+":
            return [self]
        else:
            l = self.left.flatten(operator)
            r = self.right.flatten(operator)

            def mycompare(item1, item2):
                return item1.compare(item2)
            mylist = sorted(l + r, key=cmp_to_key(mycompare))
            result = []
            skipIndices = []
            idx = 0
            while idx < len(mylist):
                elt = mylist[idx]
                if idx in skipIndices:
                    idx += 1
                    continue

                term = elt
                coefficient = 1
                eltCoeff, eltVar, eltExists = elt.getCoeff()
                if eltExists:
                    term = eltVar
                    coefficient = eltCoeff
                search = idx + 1
                while search < len(mylist):
                    nextElt = mylist[search]
                    nextCoefficient = 1
                    nextCoeff, nextVar, nextExists = nextElt.getCoeff()
                    if nextExists:
                        nextCoefficient = nextCoeff
                        nextElt = nextVar
                    if term.compare(nextElt) == 0:
                        coefficient += nextCoefficient
                        skipIndices.append(search)
                    search += 1

                if coefficient == -1:
                    coeffElt = Minus(term)
                    result.append(coeffElt)
                elif coefficient != 1:
                    coeffElt = Mult(Num(coefficient), term)
                    result.append(coeffElt)
                else:
                    result.append(term)
                idx += 1
            result = sorted(result, key=cmp_to_key(mycompare))
            return result


# (Int, Int) -> Int
class Sub(BinaryMath):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.kind = MathKind.Sub

    def __str__(self):
        return self.left.wrap() + " - " + self.right.wrap()

    def func(self, x, y):
        return x - y

    def make(self, left, right):
        # Transform e1 - e2 to e1 + -e2
        minus = Minus(right)
        return Add(left, minus).simplify()


# (Int, Int) -> Int
class Mult(BinaryMath):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.kind = MathKind.Mult

    def __str__(self):
        l = self.left.wrap()
        r = self.right.wrap()
        lVar, lExists = self.left.eval()
        if lExists:
            return l + r
        elif self.left.isVariable() and self.right.isVariable():
            return l + r
        else:
            return l + " * " + r

    def wrap(self):
        lVar, lExists = self.left.eval()
        if lExists:
            return str(self)
        elif self.left.isVariable() and self.right.isVariable():
            return str(self)
        else:
            return "(" + str(self) + ")"

    def getCoeff(self):
        lVal, lExists = self.left.eval()
        if lExists:
            return lVal, self.right, True
        else:
            return 0, self, False

    def getVariableName(self):
        lVal, lExists = self.left.eval()
        if lExists:
            return self.right.getVariableName()
        else:
            return ""

    def func(self, x, y):
        return x * y

    def make(self, left, right):
        f = Mult(left, right).flatten("*")
        val = 1
        idx = len(f) - 1
        eltVal, eltExists = f[idx].eval()
        while eltExists and idx >= 1:
            val *= eltVal
            eltVal, eltExists = f[idx - 1].eval()
            idx = idx - 1

        def getFromIdx(idx):
            if idx == 0:
                return f[idx]
            else:
                return Mult(getFromIdx(idx - 1), f[idx])

        rest = getFromIdx(idx)

        if val == 1:
            if isinstance(rest, Mult):
                return self.simpHelper(rest.left, rest.right)
            else:
                return rest
        else:
            return self.simpHelper(rest, Num(val))

        l = rest
        r = Num(val)

    def simpHelper(self, l, r):
        # Transform (e * a) * b to e * c, where c is a * b
        if isinstance(l, Mult):
            rVal, rExists = r.eval()
            if rExists:
                lrVal, lrExists = l.right.eval()
                if (lrExists):
                    r = Num(lrVal * rVal)
                    l = l.left

        # Transform (a * e) * b to e * c, where c is a * b
        if isinstance(l, Mult):
            rVal, rExists = r.eval()
            if rExists:
                llVal, llExists = l.left.eval()
                if llExists:
                    r = Num(llVal * rVal)
                    l = l.right

        # Transform a * (b * e) to c * e, where c is a * b
        if isinstance(r, Mult):
            lVal, lExists = l.eval()
            if lExists:
                rlVal, rlExists = r.left.eval()
                if rlExists:
                    l = Num(lVal * lrVal)
                    r = r.right

        # Transform a * (e * b) to c * e, where c is a * b
        if isinstance(r, Mult):
            lVal, lExists = l.eval()
            if lExists:
                rrVal, rrExists = r.right.eval()
                if rrExists:
                    l = Num(lVal * rrVal)
                    r = r.left

        # Transform e * 0 and 0 * e to 0
        lVal, lExists = l.eval()
        rVal, rExists = r.eval()
        if (lExists and lVal) or (rExists and rVal == 0):
            return Num(0)

        # Transform e * 1 and 1 * e to e
        if rExists and rVal == 1:
            return l
        if lExists and lVal == 1:
            return r

        # Transform e * -1 and -1 * e to -e
        if rExists and rVal == -1:
            return Minus(l)
        if lExists and lVal == -1:
            return Minus(r)

        # Transform e * c to c * e
        if rExists and not lExists:
            temp = l
            l = r
            r = temp

        # Transform e1 * (e2 + e3) to (e1 * e2) + (e1 * e3)
        if isinstance(r, Add):
            if not isinstance(l, Add):
                temp = l
                l = Mult(l, r.left)
                r = Mult(temp, r.right)
                return Add(l, r).simplify()
            # Transform (e1 + e2) * (e3 + e4) to (e1 * e3 + e1 * e4) + (e2 * e3 + e2 * e4)
            else:
                e1 = l.left
                e2 = l.right
                e3 = r.left
                e4 = r.right
                l = Add(Mult(e1, e3), Mult(e1, e4))
                r = Add(Mult(e2, e3), Mult(e2, e4))
                return Add(l, r).simplify()

        # Transform (e1 + e2) * e3 to (e1 * e3) + (e2 * e3)
        if isinstance(l, Add):
            if not isinstance(r, Add):
                temp = l
                l = Mult(l.left, r)
                r = Mult(temp.right, r)
                return Add(l, r).simplify()

        return Mult(l, r)

    def flatten(self, operator):
        if (operator != "*"):
            return [self]
        else:
            l = self.left.flatten(operator)
            r = self.right.flatten(operator)

            def mycompare(item1, item2):
                return item1.compare(item2)
            mylist = sorted(l + r, key=cmp_to_key(mycompare))
            return mylist


# (Int, Int) -> Int
class Div(BinaryMath):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.kind = MathKind.Div

    def __str__(self):
        l = self.left.wrap()
        r = self.right.wrap()
        return l + " / " + r

    def getVariableName(self):
        rVal, rExists = self.right.eval()
        if rExists:
            return self.left.getVariableName()
        else:
            return ""

    def func(self, x, y):
        return x / y

    def make(self, left, right):
        l = left
        r = right
        return Div(l, r)


# (Int, Int) -> Int
class Mod(BinaryMath):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.kind = MathKind.Mod

    def __str__(self):
        l = self.left.wrap()
        r = self.right.wrap()
        return l + " % " + r

    def func(self, x, y):
        return x % y

    def make(self, left, right):
        return Mod(left, right)


# Int -> Int
class Minus(Math):
    def __init__(self, child):
        super().__init__()
        self.kind = MathKind.Minus
        self.child = self.convert(child)

    def __str__(self):
        return "-" + self.child.wrap()

    def func(self, x, y):
        return -x

    def eval(self):
        childVal, childExists = self.child.eval()
        if childExists:
            return -childVal, True
        else:
            return 0, False

    def getCoeff(self):
        childCoeff, childVar, childExists = self.child.getCoeff()
        if childExists:
            return -childCoeff, childVar, True
        else:
            return 0, self, False

    def getVariableName(self):
        return self.child.getVariableName()

    def make(self, left, right):
        return Minus(left)

    def simplify(self):
        c = self.child.simplify()
        cVal, cExists = c.eval()
        if cExists:
            return Num(-cVal)
        if isinstance(c, Minus):
            return c.child
        if isinstance(c, Add):
            l = Minus(c.left)
            r = Minus(c.right)
            return Add(l, r).simplify()
        return Minus(c)


# Int
class A(Math):
    def __init__(self):
        super().__init__()
        self.kind = MathKind.A

    def __str__(self):
        return "a"

    def getVariableName(self):
        return "a"

    def isVariable(self):
        return True


# Int
class B(Math):
    def __init__(self):
        super().__init__()
        self.kind = MathKind.B

    def __str__(self):
        return "b"

    def getVariableName(self):
        return "b"

    def isVariable(self):
        return True


# Int
class C(Math):
    def __init__(self):
        super().__init__()
        self.kind = MathKind.C

    def __str__(self):
        return "c"

    def getVariableName(self):
        return "c"

    def isVariable(self):
        return True


# Int
class X(Math):
    def __init__(self):
        super().__init__()
        self.kind = MathKind.X

    def __str__(self):
        return "x"

    def getVariableName(self):
        return "x"

    def isVariable(self):
        return True


# Int
class Y(Math):
    def __init__(self):
        super().__init__()
        self.kind = MathKind.Y

    def __str__(self):
        return "y"

    def getVariableName(self):
        return "y"

    def isVariable(self):
        return True


# Int
class Num(Math):
    def __init__(self, value):
        super().__init__()
        self.kind = MathKind.Num
        self.value = value

    def __str__(self):
        return str(self.value)

    def eval(self):
        return self.value, True

    def compare(self, other):
        kindCompare = super().compare(other)
        if kindCompare != 0:
            return kindCompare
        elif self.value < other.value:
            return -1
        elif self.value > other.value:
            return 1
        else:
            return 0

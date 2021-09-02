from conditions import *
from closure import *
from assoc import *
from identity import *
from inverse import *


# Representation of an algebraic group consisting of:
# 1. An Int -> Bool function that describes the members of the group, and:
# 2. An (Int, Int) -> Int function that describes the operation on group members.
class Group:
    def __init__(self, cond, func):
        self.cond = cond.simplify()
        self.func = func.simplify()
        self.identity = None
        self.inverse = None

    def __str__(self):
        return "c(x) = " + str(self.cond) + ", f(x, y) = " + str(self.func)

    def pretty(self):
        return "{\n  condition(x) = " + str(self.cond) + "\n  function(x, y) = " + str(self.func) + "\n  identity = " + str(self.identity) + "\n  inverse(x) = " + str(self.inverse) + "\n}"

    def isGroup(self):
        closed = checkClosure(self.cond, self.func)
        if not closed:
            print("not closed")
            return False
        assoc = checkAssoc(self.func)
        if not assoc:
            print("not associative")
            return False
        self.identity, identityExists = checkIdentity(self.cond, self.func)
        if not identityExists:
            print("no identity element")
            return False
        self.inverse, inverseExists = checkInverse(
            self.cond, self.func, self.identity)
        if not inverseExists:
            print("no inverse")
            return False
        return True


def testGroup(g):
    print("\n--- Testing whether", g, "is a group ---")
    if g.isGroup():
        print(g.pretty())
    else:
        print("not a group")


def main():
    print("\n\n\n------- MAIN ------")
    # Groups
    testGroup(Group(All(), Add(x, y)))
    testGroup(Group(Equal(Mod(x, 2), 0), Add(x, y)))
    # Not closed
    testGroup(Group(Greater(Mod(x, 4), 1), Add(x, y)))
    testGroup(Group(Geq(x, -3), Add(x, y)))
    testGroup(Group(Or(Less(x, -4), Greater(x, 4)), Add(x, y)))
    # Not associative
    testGroup(Group(All(), Sub(x, y)))
    testGroup(Group(All(), Add(Mult(2, x), y)))
    # No identity
    testGroup(Group(Geq(x, 5), Add(x, y)))
    testGroup(Group(Greater(x, 1), Mult(x, y)))
    # No inverse
    testGroup(Group(All(), Mult(x, y)))
    testGroup(Group(Geq(x, 0), Add(x, y)))


if __name__ == "__main__":
    main()

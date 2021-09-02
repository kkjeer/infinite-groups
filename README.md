# infinite-groups

Infinite groups uses ideas from abstract algebra to test whether a given
boolean function and a given integer function form an integer group or not.

An integer group consists of a set of integers and operation over integers.
This project represents the condition as a function of type Int -> Bool that
returns, for any integer x, True if x belongs to the set and False otherwise.
The operation is represented as a function of type (Int, Int) -> Int that
performs some operation on two given integers x and y in the set.

In order for a set `S` and operation `F` to form a group, they must fulfill
the following group axioms:

1. **Closure**. For each integer `x` and each integer `y` in `S`, `F(x, y)`
   must be in `S`.
2. **Associativity** For all integers `x`, `y`, and `z` in `S`, `F(F(x, y), z)`
   must be equal to `F(x, F(y, z))`.
3. **Identity**. There must be a unique integer `e` in `S` such that, for each
   integer `x` in `S`, `F(x, e) == F(e, x) == x`.
4. **Inverse**. For each integer `x` in `S`, there must be a unique integer
   `x`<sup>`-1`</sup> in `S` such that
   `F(x,` `x`<sup>`-1`</sup>`) == F(x`<sup>`-1`</sup>`, x) == e`, where `e`
   is the identity element in `S` as defined above.

## Examples

The set of all integers `s(x) = True` and the operation
`f(x, y) = x + y` is a group.

The set of all even integers `s(x) = x % 2 == 0` and the
operation `f(x, y) = x + y` is a group.

The set of all integers whose remainder when divided by four is greater than
one `s(x) = x % 4 > 1` and the operation `f(x, y) = x + y` is not a group.
These functions fail the closure axiom: `2` and `6` are both in the set `s`,
but `f(2, 6) == 8` is not.

The set of all integers `s(x) = True` and the operation `f(x, y) = x - y`
is not a group. These functions fail the associativity axiom:
`f(f(10, 6), 3) == (10 - 6) - 3 == 1`, while `f(10, f(6, 3)) == 10 - (6 - 3)`
` == 7`.

The set of all integers greater than or equal to five `s(x) = x > 5`
and the operation `f(x, y) = x + y` is not a group. These functions fail
the identity axiom: the solution for `e` to the equations `x + e == x` and
`e + x == x` is `0`, which is not in the set `s`.

The set of all integers `s(x) = True` and the operation `f(x, y) = x * y`
is not a group. These functions fail the inverse axiom: the solution for
`x`<sup>`-1`</sup> to the equations `x *` `x`<sup>`-1`</sup> ` == 1` and
`x`<sup>`-1`</sup> `* x == 1` is `1/x`, which is not in the set `s` since
`1/x` is not guaranteed to be an integer.

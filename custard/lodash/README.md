# Python Lodash

pylodash is collection utilities allow you working with `arrays`, `maths`, `number` and `string`

## Pylodash Methods

1. [Arrays](#arrays)
    - [chunk()](#chunk)
        - Creates an array of elements split into groups the length of size. If array can't be split evenly, the final
          chunk will be the remaining elements.

    - [compact()](#compact)
        - Creates an array with all falsey values removed. The values False, None, 0 and "" are falsey.

    - [difference()](#difference)
        - Creates an array of array values not included in the other given arrays using SameValueZero for equality
          comparisons. The order and references of result values are determined by the first array.

    - [drop()](#drop)
        - Creates a slice of array with n elements dropped from the beginning.

    - [drop_right()](#drop_right)
        - Creates a slice of array with n elements dropped from the end.

    - [fill()](#fill)
        - Fills elements of array with value from start up to, but not including, end.

    - [index_of()](#index_of)
        - Gets the index at which the first occurrence of value is found in array using SameValueZero for equality
          comparisons. If fromIndex is negative, it's used as the offset from the end of array.

    - [initial()](#initial)
        - Gets all but the last element of array.

    - [pull()](#pull)
        - Removes all given values from array using SameValueZero for equality comparisons.

2. [Maths](#maths)
    - [add()](#add)
        - Adds two numbers.

    - [ceil()](#ceil)
        - Computes *number* rounded up to *precision*.

    - [divide()](#divide)
        - Divide two numbers.

    - [floor()](#floor)
        - Computes *number* rounded down to *precision*.

    - [max()](#max)
        - Computes the maximum value of *array*. If array is empty or falsey, [] is returned.

    - [mean()](#mean)
        - Computes the mean of the values in *array*.

    - [min()](#min)
        - Computes the minimum value of *array*. If *array* is empty or falsey, [] is returned.

    - [multiply()](#multiply)
        - Multiply two numbers.

    - [substract()](#substract)
        - Subtract two numbers.

    - [sum()](#sum)
        - Computes the sum of the values in array.


3. [Number](#number)
    - [clamp()](#clamp)
        - Clamps number within the inclusive lower and upper bounds.

    - [in_range()](#in_range)
        - Checks if *n* is between *start* and up to, but not including, *end*. If *end* is not specified, it's set to *
          start* with *start* then set to *0*. If *start* is greater than *end* the params are swapped to support
          negative ranges.

    - [random()](#random)
        - Produces a random number between the inclusive lower and upper bounds. If only one argument is provided a
          number between 0 and the given number is returned. If floating is true, or either lower or upper are floats, a
          floating-point number is returned instead of an integer.

4. [String](#string)
    - [camel_case()](#camelcase)
        - Converts string to camel case.

    - [capitalize()](#capitalize)
        - Converts the first character of string to upper case and the remaining to lower case.

    - [ends_with()](#ends_with)
        - Checks if string ends with the given target string.

    - [escape()](#escape)
        - Converts the characters "&", "<", ">", '"', and "'" in string to their corresponding HTML entities.

    - [lower_case()](#lower_case)
        - Converts string, as space separated words, to lower case.

    - [lower_first()](#lower_first)
        - Converts the first character of string to lower case.

    - [pad()](#pad)
        - Pads string on the left and right sides if it's shorter than length. Padding characters are truncated if they
          can't be evenly divided by length.

    - [pad_end()](#pad_end)
        - Pads string on the right side if it's shorter than length. Padding characters are truncated if they exceed
          length.

    - [pad_start()](#pad_start)
        - Pads string on the left side if it's shorter than length. Padding characters are truncated if they exceed
          length.

    - [repeat()](#repeat)
        - Repeats the given string n times.

    - [replace()](#replace)
        - Replaces matches for pattern in string with replacement.

    - [starts_with()](#starts_with)
        - Checks if string starts with the given target string.

## List methods in packages

### <a name="arrays">"Arrays" Methods</a>

<a name="chunk"></a>

```
_.chunk(array, [size=1])
```

**Example**

```
_.chunk(['a', 'b', 'c', 'd'], 2)
// => [['a', 'b'], ['c', 'd']]
 
_.chunk(['a', 'b', 'c', 'd'], 3)
// => [['a', 'b', 'c'], ['d']]
```

---

<a name="compact"></a>

```
_.compact(array)
```

**Example**

```
_.compact([0, 1, False, 2, '', 3])
// => [1, 2, 3]
```

---
<a name="difference"></a>

```
_.difference(array, [values])
```

**Example**

```
_.difference([2, 1], [2, 3])
// => [1]
```

---
<a name="drop"></a>

```
_.drop(array, [n=1])
```

**Example**

```
_.drop([1, 2, 3])
// => [2, 3]
 
_.drop([1, 2, 3], 2)
// => [3]
 
_.drop([1, 2, 3], 5)
// => []
 
_.drop([1, 2, 3], 0)
// => [1, 2, 3]
```

---
<a name="drop_right"></a>

```
_.drop_right(array, [n=1])
```

**Example**

```
_.drop_right([1, 2, 3])
// => [1, 2]
 
_.drop_right([1, 2, 3], 2)
// => [1]
 
_.drop_right([1, 2, 3], 5)
// => []
 
_.drop_right([1, 2, 3], 0)
// => [1, 2, 3]
```

---
<a name="fill"></a>

```
_.fill(array, value, [start=0])
```

**Example**

```
array = [1, 2, 3]
 
_.fill(array, 'a')
// => ['a', 'a', 'a']
 
_.fill(Array(3), 2)
// => [2, 2, 2]
 
_.fill([3, 6, 8, 10], '*', 1, 3)
// => [3, '*', '*', 10]
```

---
<a name="index_of"></a>

```
_.index_of(array, value, [fromIndex=0])
```

**Example**

```
_.index_of([1, 2, 1, 2], 2)
// => 1
 
// Search from the `fromIndex`.
_.index_of([1, 2, 1, 2], 2, 2)
// => 3
```

---
<a name="initial"></a>

```
_.initial(array)
```

**Example**

```
_.initial([1, 2, 3])
// => [1, 2]
```

---
<a name="pull"></a>

```
_.pull(array, [values])
```

**Example**

```
array = ['a', 'b', 'c', 'a', 'b', 'c']
 
_.pull(array, 'a', 'c')
// => ['b', 'b']
```

---

### <a name="maths">"Maths" Methods</a>

<a name="add"></a>

```
_.add(augend, addend)
```

**Example**

```
_.add(6, 4)
// => 10
```

---
<a name="ceil"></a>

```
_.ceil(number, [precision=0])
```

**Example**

```
_.ceil(4.006)
// => 5
 
_.ceil(6.004, 2)
// => 6.01
 
_.ceil(6040, -2)
// => 6100
```

---
<a name="divide"></a>

```
_.divide(dividend, divisor)
```

**Example**

```
_.divide(6, 4)
// => 1.5
```

---
<a name="floor"></a>

```
_.floor(number, [precision=0])
```

**Example**

```
_.floor(4.006)
// => 4
 
_.floor(0.046, 2)
// => 0.04
 
_.floor(4060, -2)
// => 4000
```

---
<a name="max"></a>

```
_.max(array)
```

**Example**

```
_.max([3, 2, 8, 6])
// => 8
 
_.max([]);
// => undefined
```

---
<a name="mean"></a>

```
_.mean(array)
```

**Example**

```
_.mean([3, 2, 8, 6]);
// => 5
```

---
<a name="min"></a>

```
_.min(array)
```

**Example**

```
_.min([3, 2, 8, 6]);
// => 2
 
_.min([]);
// => undefined
```

---
<a name="multiply"></a>

```
_.multiply(multiplier, multiplicand)
```

**Example**

```
_.multiply(6, 4)
// => 24
```

---
<a name="round"></a>

```
_.round(number, [precision=0])
```

**Example**

```
_.round(4.006)
// => 4
 
_.round(4.006, 2)
// => 4.01
 
_.round(4060, -2)
// => 4100
```

---
<a name="subtract"></a>

```
_.subtract(minuend, subtrahend)
```

**Example**

```
_.subtract(6, 4)
// => 2
```

---
<a name="sum"></a>

```
_.sum(array)
```

**Example**

```
_.sum([3, 2, 8, 6])
// => 20
```

---

### <a name="number">"Number" Methods</a>

<a name="clamp"></a>

```
_.clamp(number, [lower], upper)
```

**Example**

```
_.clamp(-10, -5, 5)
// => -5
 
_.clamp(10, -5, 5)
// => 5
```

---
<a name="in_range"></a>

```
_.in_range(number, [start=0], end)
```

**Example**

```
_.in_range(3, 2, 4)
// => True
 
_.in_range(3, 8)
// => True
 
_.in_range(3, 2)
// => False
 
_.in_range(2, 2)
// => False
 
_.in_range(1.2, 2)
// => True
 
_.in_range(5.2, 4)
// => False
 
_.in_range(-3, -2, -6)
// => True
```

---
<a name="random"></a>

```
_.random([lower=0], [upper=1], [floating])
```

**Example**

```
_.random(0, 5);
// => an integer between 0 and 5
 
_.random(5);
// => also an integer between 0 and 5
 
_.random(5, true);
// => a floating-point number between 0 and 5
 
_.random(1.2, 5.2);
// => a floating-point number between 1.2 and 5.2
```

---

### <a name="string">"String" Methods</a>

<a name="camelcase"></a>

```
_.camel_case([string=''])
```

**Example**

```
_.camel_case('Foo Bar')
// => 'fooBar'
 
_.camel_case('--foo-bar--')
// => 'fooBar'
 
_.camel_case('__FOO_BAR__')
// => 'fooBar'
```

---
<a name="capitalize"></a>

```
_.capitalize([string=''])
```

**Example**

```
_.capitalize('FRED')
// => 'Fred'
```

---
<a name="ends_with"></a>

```
_.ends_with([string=''], [target], [position=string.length])
```

**Example**

```
_.ends_with('abc', 'c')
// => True
 
_.ends_with('abc', 'b')
// => False
 
_.ends_with('abc', 'b', 2)
// => True
```

---
<a name="escape"></a>

```
_.escape([string=''])
```

**Example**

```
_.escape('fred, barney, & pebbles')
// => 'fred, barney, &amp; pebbles'
```

---
<a name="lower_case"></a>

```
_.lower_case([string=''])
```

**Example**

```
_.lower_case('--Foo-Bar--')
// => 'foo bar'
 
_.lower_case('fooBar')
// => 'foo bar'
 
_.lower_case('__FOO_BAR__')
// => 'foo bar'
```

---
<a name="lower_first"></a>

```
_.lower_first([string=''])
```

**Example**

```
_.lower_first('Fred')
// => 'fred'
 
_.lower_first('FRED')
// => 'fRED'
```

---
<a name="pad"></a>

```
_.pad([string=''], [length=0], [chars=' '])
```

**Example**

```
_.pad('abc', 8)
// => '  abc   '
 
_.pad('abc', 8, '_-')
// => '_-abc_-_'
 
_.pad('abc', 3)
// => 'abc'
```

---
<a name="pad_end"></a>

```
_.pad_end([string=''], [length=0], [chars=' '])
```

**Example**

```
_.pad_end('abc', 6)
// => 'abc   '
 
_.pad_end('abc', 6, '_-')
// => 'abc_-_'
 
_.pad_end('abc', 3)
// => 'abc'
```

---
<a name="pad_start"></a>

```
_.pad_start([string=''], [length=0], [chars=' '])
```

**Example**

```
_.pad_start('abc', 6)
// => '   abc'
 
_.pad_start('abc', 6, '_-')
// => '_-_abc'
 
_.pad_start('abc', 3)
// => 'abc'
```

---
<a name="repeat"></a>

```
_.repeat([string=''], [n=1])
```

**Example**

```
_.repeat('*', 3)
// => '***'
 
_.repeat('abc', 2)
// => 'abcabc'
 
_.repeat('abc', 0)
// => ''
```

---
<a name="replace"></a>

```
_.replace([string=''], pattern, replacement)
```

**Example**

```
_.replace('Hi Fred', 'Fred', 'Barney')
// => 'Hi Barney'
```

---
<a name="starts_with"></a>

```
_.starts_with([string=''], [target], [position=0])
```

**Example**

```
_.starts_with('abc', 'a')
// => True
 
_.starts_with('abc', 'b')
// => False
 
_.starts_with('abc', 'b', 1)
// => True
```

## Development Mode

### Building Your Package

In development mode, pylodash need install packages below to build package:

```
- setuptools >= 38.6.0
- wheel >= 0.31.0
- twine >= 1.11.0
```

Run command to build package:

```
$ python3 setup.py sdist bdist_wheel
```

### Testing Your Package

To check that your package description will render properly on PyPI, you can run twine check on the files created in
dist:

```
$ twine check dist/*
```

### Uploading Your Packages

To install package to develop environment, we can use command:

```
$ python3 setup.py develop
```

To upload package to testing environment before upload to PyPI, follow step (make sure you have an account registered):

```
$ twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```

To publish your own package to PyPI, this final step is short:

```
$ twine upload dist/*
```

### *pip* install Your Package

With your package uploaded to PyPI, you can install it with pip as well:

```
$ pip install pylodash
```

To run all test cases in package, you can run command below in folder package:

```
$ python setup.py test
```

## License

Copyright © 2019 All rights reserved.
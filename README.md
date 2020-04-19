# waveConstructor

Construct waveJSON based on text description.

# Format

## Blanks

Blank lines are ignored.

## Comments

Lines that begin with `#` are ignored.

Mid-line comments are not allowed.

## Declarations

### Waves

Declare waves to ensure they appear in the desired order.

Wave names are quoted in declarations, but not quoted in assignment.

```
wave "name"
```

Blank waves are spacers.

```
wave ""
```


Optionally you may supply a "short name" at the end using the format:

```
wave "A Long Name" as short_name
```

The long name will appear in the text output, allowing you to give more descriptive names with otherwise-unusable characters in the name.

Refer to the wave using the short name.

## Clocks

Advance the clock by 1 frame using a `.` on a line.

You may enter more than 1 `.` per line to advance the clock multiple frames on a single line.

## Assignment

Assign a value to a wave for a given frame using the syntax:

```
name = value
```

To mark a node for use as an edge later, prefix the node letter with the letter `n`:

```
name = nLetter
```

Example:

```
myWave = na
```

Will mark the current frame as node `a` for use in edges.

## Edges

Edges can be automatically assigned edge nodes, or edge letters can be used.

Mixing of types is not allowed.

Optionally, assign a label by putting `:` and the label after the edge declaration.

Example:

```
a ~> b : Label text
```

### Automatic

Supply two wave names separated by a valid edge arrow to create an edge with automatic node marker assignment.

Example:

```
wave1 ~> wave2
```

Or, with label:


```
wave1 ~> wave2 : Label text
```

### Manual

Supply two assigned node markers separated by a valid edge arrow to create an edge with the given node marker assignment.

Example:

```
a ~> b
```

Or, with label:


```
a ~> b : Label text
```


## Modifiers

Supply modifiers like `phase` or `period` to a wave with the following syntax:

```
name : modifier value
```

Example:

```
wave1 : phase 0.5
```

# TODO List

* Header/footer
* Formatting
* Groups


# gTimeCalc

gTimeCalc is an interactive calculator for time in `hh:mm:ss.ms` format.


## Usage


### Pasting time

You can copy a time string from an any source and paste it to both of time
entries. The units of time can be separated by a colon,
a Unicode "RATIO" (U+2236), a comma or any number of spaces and tabs.
The last component (seconds) is treated as a real number, others — as integers,
which means that fractional part (if any) will be truncated.

Time units in a string are parsed from right to left, so some of them, as well
as separators between, can be omitted. In this case, they will be treated
as zero. For example: `12:` and `00:12:00` is 12 minutes, `:` is just zero.

The minus (simple ASCII hyphen (U+002D) or Unicode "MINUS SIGN" (U+2212))
allowed as well. For example, `1:−60` will be pasted as 0. But keep in mind
that the resulting time is always positive, so `1:−70` will be pasted as
10 seconds.

Here are some examples:

String       | Will be pasted as
-------------|-----------------------------------------------------------
`12:15:35.5` | 12 hours, 15 minutes, 35 seconds, 500 milliseconds
`12:15:`     | 12 hours, 15 minutes
`12:15`      | 12 minutes, 15 seconds
`12`         | 12 seconds
`−12`        | 12 seconds (the final time is always positive)
`.010`       | 10 milliseconds
`1:−60`      | 0 (1 minute minus 60 seconds)
`1:−70`      | 10 seconds (positive result of 1 minute minus 70 seconds)
`130:`       | 2 hours, 10 minutes
`3723`       | 1 hour, 2 minutes, 3 seconds


### The list

gTimeCalc has an equation list in which you can add a state of the calculator.
To load an equation back, click twice on it. You can use the list simply as a
notebook: its state is automatically saved on exit (as well as the state
of the calculator itself).

But the most useful feature of the list is ability to export equations
to a text file in a user-defined format. For example, you can parse an
exported file using a scripting language and launch a program
(like FFmpeg or Mencoder) with appropriate arguments for batch processing.
Or you can export a [CSV][] to open in a spreadsheet.


#### Formatting

The formatting works by replacing special specifiers in a format string with
a related information, which can be a component from an equation or special
characters like a tabulation or a line break. Any other text remains as is.

For practical reasons and simplicity, a text that replaces specifiers uses
ASCII symbols instead of the "real" Unicode ones. This means that time units
will be separated by a colon (U+003A) instead of "RATIO" (U+2236), and a minus
will be pasted as a hyphen (U+002D) instead of "MINUS SIGN" (U+2212).

Here are all of the format specifiers (but you don't need to remember all of
them — the "Format" entry has pop-up tooltip):

Spec | Meaning
-----|------------
`%1` | Time 1
`%2` | Time 2
`%o` | Operation
`%r` | Result
`%n` | Newline
`%t` | Tabulation

For example, the format string to print a whole equation will be
`%1 %o %2 = %r`.


[CSV]: https://en.wikipedia.org/wiki/Comma-separated_values

[gTimeCalc website]: https://danpla.github.io/gtimecalc/

# About

gTimeCalc is an interactive calculator for time in `hh:mm:ss.ms`
format. It's a cross-platform, free, and open source software.

![gTimeCalc screenshot](img/screenshot.png)


# Installation

The [gTimeCalc website] provides several download options, including
an installer for Windows and a DEB package for Debian, Ubuntu, and
derivatives. Downloads for other systems may be added later.

If you don't find a suitable choice for your system, it's possible to
use gTimeCalc without installation. You will need the following
dependencies:

 * Python 3
 * PyGObject
 * gir1.2-gtk-3.0

On Debian, Ubuntu, and derivatives you can install the dependencies
with:

    sudo apt-get install make python3 python3-gi gir1.2-gtk-3.0 gir1.2-appindicator3-0.1

After you have installed the dependencies, download the source code
tarball, unpack it anywhere, and execute `bin/gtimecalc`. If you have
any troubles with the last step, please read
[Python Setup and Usage][].

[Python Setup and Usage]: https://docs.python.org/3/using/index.html


# Usage


## Pasting time

You can copy a time string from any text and paste it into both time
entries. The time units can be separated by a colon, a Unicode
"RATIO" (U+2236), a comma, or any number of spaces and tabs. Seconds
can have a decimal separator followed by a fractional part denoting
milliseconds. The decimal separator is always a period, regardless of
your locale.

Time units in a string are parsed from right to left, so some of
them, as well as separators between, can be omitted. In this case,
they will be treated as zero. For example: `12:` and `00:12:00` is 12
minutes, `:` is just zero. It's also possible to omit the integer
part of seconds if you only need to express milliseconds, like `.010`.

The minus (ASCII hyphen (U+002D) or Unicode "MINUS SIGN" (U+2212)) is
allowed as well. For example, `1:−60` is 0. The resulting time is
always positive, so `1:−70` is 10 seconds.

Here are some examples:

String       | Pasted as
-------------|----------------------------------------------------------
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


## Equation list

![gTimeCalc with equation list enabled](img/equation_list.png)

gTimeCalc has a list (select "View → Equations" to show it) in which
you can add equations from the calculator. To load the equation back,
click twice on it.

The "Save equation as…" button shows the dialog that allows you to
save the equation list as a plain text file in a custom format, e.g.
[CSV][] to open in a spreadsheet. The formatting is described in the
next section.

![Equation list export dialog](img/export_dialog.png)


### Formatting

The formatting works by replacing format specifiers in the format
string (the "Format" entry) with related information, such as a
component from the equation. Any text which is not a specifier remains
as is.

Here are all the format specifiers (you can also see them in the
pop-up tooltip of the Format entry):

Spec | Meaning
-----|-----------
`%1` | Time 1
`%2` | Time 2
`%o` | Operation
`%r` | Result
`%n` | Newline
`%t` | Tabulation
`%%` | %

For example, the format string to print a whole equation will be
`%1 %o %2 = %r`. To create a [CSV][] file, use `%1,%o,%2,%r` and
choose Windows (CRLF) line endings.

Several notes:

 *  For practical reasons, the text that replaces specifiers uses
    ASCII symbols instead of the Unicode ones. This means that time
    units will be separated by a colon (U+003A) instead of "RATIO"
    (U+2236), and the minus will be pasted as a hyphen (U+002D)
    instead of "MINUS SIGN" (U+2212).

 *  Each equation will be on a separate line. You don't have to add
    `%n` at the end of the format string for this.

 *  Using `%%` to insert the percent sign is only necessary when the
    sign and the following character create another specifier.

[CSV]: https://en.wikipedia.org/wiki/Comma-separated_values


SECOND_MS = 1000
MINUTE_MS = 60 * SECOND_MS
HOUR_MS = 60 * MINUTE_MS


def _ndivmod(x, y):
    '''Custom divmod to work with negative numbers.'''
    q = abs(x) // y
    if x < 0:
        q = -q
    r = x - y * q
    return q, r


def join_units(hours, minutes, seconds, milliseconds):
    '''Join time units to milliseconds.'''
    return (
        int(hours) * HOUR_MS +
        int(minutes) * MINUTE_MS +
        int(seconds) * SECOND_MS +
        int(milliseconds))


def split_units(ms):
    '''Split milliseconds by time units.'''
    hours, ms = _ndivmod(ms, HOUR_MS)
    minutes, ms = _ndivmod(ms, MINUTE_MS)
    seconds, ms = _ndivmod(ms, SECOND_MS)
    return hours, minutes, seconds, ms


def ms_to_str(ms, unicode_symbols=False):
    '''Convert milliseconds to a string in hh:mm:ss.ms format.

    If unicode_symbols is True, MUNUS SING will be used instead of a hyphen and
    RATIO instead of a colon.
    '''
    sign = ('-', '\N{MINUS SIGN}')[unicode_symbols] if ms < 0 else ''
    ratio = (':', '\N{RATIO}')[unicode_symbols]

    hours, ms = _ndivmod(ms, HOUR_MS)
    minutes, ms = _ndivmod(ms, MINUTE_MS)
    seconds = ms / SECOND_MS
    seconds_pad = 6 if seconds < 10 else 0  # Pad only the integer part

    return '{}{:02}{ratio}{:02}{ratio}{:0{}.3f}'.format(
        sign, abs(hours), abs(minutes), abs(seconds), seconds_pad, ratio=ratio)


_TIME_STR_TRANS = str.maketrans('\N{MINUS SIGN}\N{RATIO},', '-::')


def str_to_ms(time_str):
    '''Convert a string in hh:mm:ss.ms format to milliseconds.

    Time components in the string can be separated by a colon,
    Unicode "RATIO", a comma, or whitespace. Negative values
    (with - or Unicode "MINUS SIGN") are also allowed.

    Raises ValueError if the string cannot be converted.
    '''

    time_str = time_str.translate(_TIME_STR_TRANS)

    parts = []
    for s in time_str.split(':'):
        parts.extend(s.split() or ('',))

    result = 0
    for val, ms, val_t in zip(
            reversed(parts),
            (SECOND_MS, MINUTE_MS, HOUR_MS),
            (float, int, int)):
        if val:
            result += round(val_t(val) * ms)
    return result

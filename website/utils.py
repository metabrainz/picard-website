from flask.ext.babel import format_datetime, format_date


def reformat_date(value, format=None):
    """Converts date into string formatted for current locale."""
    return format_date(value, format)


def reformat_datetime(value, format=None):
    """Converts datetime into string formatted for current locale."""
    return format_datetime(value.replace(tzinfo=None), format)

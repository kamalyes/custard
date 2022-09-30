def is_number(s):
    """Check input is number or not

    Arguments:
        s {*} -- The input to check

    Returns:
        (boolean)] -- Returns True if input a number else False
    """
    try:
        int(s)
        return True
    except ValueError:
        return False

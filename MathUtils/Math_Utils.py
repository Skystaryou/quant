def double_compare(x, y):
    max_error=1e-11
    if (abs(x-y)<max_error):
        return 0
    else:
        if (x>y):
            return 1
        else:
            return -1
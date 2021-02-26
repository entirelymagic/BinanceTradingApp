def investment_return(amt, int_rate, period):
    return amt * ((1 + (0.01 * int_rate)) ** period)

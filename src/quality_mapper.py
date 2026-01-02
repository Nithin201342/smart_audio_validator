def map_quality(mos):
    if mos < 2.5:
        return "Poor", round((2.5 - mos) / 2.5 * 100, 1)
    elif mos < 3.5:
        return "Average", round((mos - 2.5) * 100, 1)
    else:
        return "Good", round((mos - 3.5) / 1.5 * 100, 1)

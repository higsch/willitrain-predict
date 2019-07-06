def identifyRainMasses(arr):
    arr = (arr != 0) & (arr != 255)
    rainMasses = measure.label(arr, background=0, neighbors=8,)
    rainMasses[rainMasses == 0] = 255
    return(rainMasses)

#절대습도 산출
#온도,상대습도

def calcSaturatedVaporPressure(AirTemperature): #온도로 포화수증기압 산출 (mb)

    es = 6.11*pow(10,(7.5*AirTemperature)/(237.3+AirTemperature))
    return es


def calcAbsHumidity(RHumidity,AirTemperature): #mmhg g/m3(질량기준)

    d = (RHumidity/100)*(804/(1+0.00366*AirTemperature))*(calcSaturatedVaporPressure(AirTemperature)/1013.250)

    return d

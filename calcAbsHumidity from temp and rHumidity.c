double calcSaturatedVaporPressure() //온도로 포화수증기압 산출 (mb) hPa
{
    double es = 6.11*pow(10,(7.5*comp_data.temperature)/(237.3+comp_data.temperature))
    return es;

}

double calcAbsHumidity()//mb g/m3(건공기 질량기준)
{
    d = (comp_data.humidity/100)*(804/(1+0.00366*comp_data.temperature))*(calcSaturatedVaporPressure()/1013.250)

    return d;
}

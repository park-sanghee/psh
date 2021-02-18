#include "SC16IS750.h"
#include <ti/drivers/I2C.h>
#include "ti_drivers_config.h"


I2C_Handle i2cHandle;
I2C_Params i2cParams;


void sc16is750_setup(int baudrate)
{
    sc16is750_ResetDevice();
    sc16is750_FIFOReset(0);
    sc16is750_FIFOEnable(1);

    sc16is750_SetBaudrate(baudrate);
    sc16is750_SetLine(8,0,1);

    while(sc16is750_ping() != 1){
      printf("sc16is750 ping error - device not found \n");
      usleep(1000);
    }


}


uint8_t sc16is750_ReadRegister(uint8_t reg_addr)
{
    uint8_t result;


    uint8_t rbuf[1]={0};
    uint8_t wbuf[1];
    bool status = 1;
    wbuf[0] = reg_addr<<3;

    I2C_Transaction i2cTransactionR;
    i2cTransactionR.slaveAddress = 0x4d;
    i2cTransactionR.writeBuf =wbuf;
    i2cTransactionR.writeCount =1;
    i2cTransactionR.readBuf = rbuf;
    i2cTransactionR.readCount = 1;

    status = I2C_transfer(i2cHandle, &i2cTransactionR);

    result=rbuf[0];

    return result;

}

void sc16is750_WriteRegister(uint8_t reg_addr, uint8_t val)
{

    bool status = 1;
    uint8_t buf[2]={0};

    buf[0] = reg_addr<<3;
    buf[1] = val;

    I2C_Transaction i2cTransactionW;
    i2cTransactionW.slaveAddress = 0x4d;//id.dev_addr;
    i2cTransactionW.writeBuf =buf;
    i2cTransactionW.writeCount =2;
    i2cTransactionW.readBuf = NULL;
    i2cTransactionW.readCount = NULL;
    //usleep(1000);
    status = I2C_transfer(i2cHandle, &i2cTransactionW);



    return ;
}
void sc16is750_WriteRegisterMultiple(uint8_t reg_addr, uint8_t *data ,int len)
{
    int i;
    bool status = 1;
    uint8_t buf[20]={0,};

    buf[0] = reg_addr<<3;

    for (i = 0; i < len; i++)
        buf[i + 1] = data[i];

    I2C_Transaction i2cTransactionW;
    i2cTransactionW.slaveAddress = 0x4d;//id.dev_addr;
    i2cTransactionW.writeBuf =buf;
    i2cTransactionW.writeCount =len+1;
    i2cTransactionW.readBuf = NULL;
    i2cTransactionW.readCount = NULL;
    usleep(1000);
    status = I2C_transfer(i2cHandle, &i2cTransactionW);

    return ;
}

void sc16is750_ReadRegisterMultiple(uint8_t reg_addr, int *data ,int len)
{
    int i;
    bool status = 1;
    uint8_t rbuf[30]={0,};
    uint8_t wbuf[1]={0};

    wbuf[0] = reg_addr<<3;

    I2C_Transaction i2cTransactionW;
    i2cTransactionW.slaveAddress = 0x4d;//id.dev_addr;
    i2cTransactionW.writeBuf =wbuf;
    i2cTransactionW.writeCount =1;
    i2cTransactionW.readBuf = rbuf;
    i2cTransactionW.readCount = len;
    usleep(1000);
    status = I2C_transfer(i2cHandle, &i2cTransactionW);

    for(i=0;i<len;i++){
        *data=rbuf[i];
        data++;
       }

    return ;
}

int16_t sc16is750_SetBaudrate(uint32_t baudrate) //return error of baudrate parts per thousand
{
    uint16_t divisor;
    uint8_t prescaler;
    uint32_t actual_baudrate;
    int16_t error;
    uint8_t temp_lcr;
    if ( (sc16is750_ReadRegister(SC16IS750_REG_MCR)&0x80) == 0) { //if prescaler==1
        prescaler = 1;
    } else {
        prescaler = 4;
    }

    divisor = (SC16IS750_CRYSTCAL_FREQ/prescaler)/(baudrate*16);

    temp_lcr = sc16is750_ReadRegister(SC16IS750_REG_LCR);
    temp_lcr |= 0x80;
    sc16is750_WriteRegister(SC16IS750_REG_LCR,temp_lcr);
    //write to DLL
    sc16is750_WriteRegister(SC16IS750_REG_DLL,(uint8_t)divisor);
    //write to DLH
    sc16is750_WriteRegister(SC16IS750_REG_DLH,(uint8_t)(divisor>>8));
    temp_lcr &= 0x7F;
    sc16is750_WriteRegister(SC16IS750_REG_LCR,temp_lcr);


    actual_baudrate = (SC16IS750_CRYSTCAL_FREQ/prescaler)/(16*divisor);
    error = ((float)actual_baudrate-baudrate)*1000/baudrate; //must be 0 if no error
#ifdef  SC16IS750_DEBUG_PRINT
    Serial.print("Desired baudrate: ");
    Serial.println(baudrate,DEC);
    Serial.print("Calculated divisor: ");
    Serial.println(divisor,DEC);
    Serial.print("Actual baudrate: ");
    Serial.println(actual_baudrate,DEC);
    Serial.print("Baudrate error: ");
    Serial.println(error,DEC);
#endif

    return error;

}

void sc16is750_SetLine(uint8_t data_length, uint8_t parity_select, uint8_t stop_length )
{
    uint8_t temp_lcr;
    temp_lcr = sc16is750_ReadRegister(SC16IS750_REG_LCR);
    temp_lcr &= 0xC0; //Clear the lower six bit of LCR (LCR[0] to LCR[5]
#ifdef  SC16IS750_DEBUG_PRINT
    Serial.print("LCR Register:0x");
    Serial.println(temp_lcr,DEC);
#endif
    switch (data_length) {            //data length settings
        case 5:
            break;
        case 6:
            temp_lcr |= 0x01;
            break;
        case 7:
            temp_lcr |= 0x02;
            break;
        case 8:
            temp_lcr |= 0x03;
            break;
        default:
            temp_lcr |= 0x03;
            break;
    }

    if ( stop_length == 2 ) {
        temp_lcr |= 0x04;
    }

    switch (parity_select) {            //parity selection length settings
        case 0:                         //no parity
             break;
        case 1:                         //odd parity
            temp_lcr |= 0x08;
            break;
        case 2:                         //even parity
            temp_lcr |= 0x18;
            break;
        case 3:                         //force '1' parity
            temp_lcr |= 0x03;
            break;
        case 4:                         //force '0' parity
            break;
        default:
            break;
    }

    sc16is750_WriteRegister(SC16IS750_REG_LCR,temp_lcr);
}

void sc16is750_ResetDevice(void)
{
    uint8_t reg;

    reg = sc16is750_ReadRegister(SC16IS750_REG_IOCONTROL);
    reg |= 0x08;
    sc16is750_WriteRegister(SC16IS750_REG_IOCONTROL, reg);

    return;
}

void sc16is750_FIFOEnable(uint8_t fifo_enable)
{
    uint8_t temp_fcr;

    temp_fcr = sc16is750_ReadRegister(SC16IS750_REG_FCR);

    if (fifo_enable == 0){
        temp_fcr &= 0xFE;
    } else {
        temp_fcr |= 0x01;
    }
    sc16is750_WriteRegister(SC16IS750_REG_FCR,temp_fcr);

    return;
}

void sc16is750_FIFOReset(uint8_t rx_fifo)
{
     uint8_t temp_fcr;

    temp_fcr = sc16is750_ReadRegister(SC16IS750_REG_FCR);

    if (rx_fifo == 0){
        temp_fcr |= 0x04;
    } else {
        temp_fcr |= 0x02;
    }
    sc16is750_WriteRegister(SC16IS750_REG_FCR,temp_fcr);

    return;

}


uint8_t sc16is750_FIFOAvailableData(void)
{
#ifdef  SC16IS750_DEBUG_PRINT
    Serial.print("=====Available data:");
    Serial.println(ReadRegister(SC16IS750_REG_RXLVL), DEC);
#endif
   return sc16is750_ReadRegister(SC16IS750_REG_RXLVL);
//    return ReadRegister(SC16IS750_REG_LSR) & 0x01;
}

uint8_t sc16is750_FIFOAvailableSpace(void)
{
   return sc16is750_ReadRegister(SC16IS750_REG_TXLVL);

}



void sc16is750_WriteByte(uint8_t val)
{
    uint8_t tmp_lsr;
 /*   while ( FIFOAvailableSpace() == 0 ){
#ifdef  SC16IS750_DEBUG_PRINT
        Serial.println("No available space");
#endif
    };
#ifdef  SC16IS750_DEBUG_PRINT
    Serial.println("++++++++++++Data sent");
#endif
    WriteRegister(SC16IS750_REG_THR,val);
*/
    do {
        tmp_lsr = sc16is750_ReadRegister(SC16IS750_REG_LSR);
    } while ((tmp_lsr&0x20) ==0);

    sc16is750_WriteRegister(SC16IS750_REG_THR,val);

}

int sc16is750_ReadByte(void)
{
    volatile uint8_t val;
    if (sc16is750_FIFOAvailableData() == 0) {
#ifdef  SC16IS750_DEBUG_PRINT
    Serial.println("No data available");
#endif
        return -1;

    } else {

#ifdef  SC16IS750_DEBUG_PRINT
    Serial.println("***********Data available***********");
#endif
      val = sc16is750_ReadRegister(SC16IS750_REG_RHR);
      return val;
    }


}

uint8_t sc16is750_ping()
{
    sc16is750_WriteRegister(SC16IS750_REG_SPR,0x55);
    if (sc16is750_ReadRegister(SC16IS750_REG_SPR) !=0x55) {
        return 0;
    }

    sc16is750_WriteRegister(SC16IS750_REG_SPR,0xAA);
    if (sc16is750_ReadRegister(SC16IS750_REG_SPR) !=0xAA) {
        return 0;
    }

    return 1;

}

uint8_t sc16is750_read_windData(unsigned int *dir,unsigned int *speed )
{
    uint8_t windData[9]={0,};
    int rwindData[9]={0,};
    int i=0;
    unsigned int current_wind_DIR = 0;
    unsigned int current_wind_SPD = 0;
    windData[0]=0x01;
    windData[1]=0x03;
    windData[2]=0x00;
    windData[3]=0x00;
    windData[4]=0x00;
    windData[5]=0x02;
    windData[6]=0xC4;
    windData[7]=0x0B;

    sc16is750_WriteRegisterMultiple(SC16IS750_REG_THR, windData,8);
    sleep(1);
    if (sc16is750_FIFOAvailableData() != 0) {
        sc16is750_ReadRegisterMultiple(SC16IS750_REG_RHR, rwindData,8);
    }else{
        printf("sc16is750_FIFOAvailableData - error \n");
    }

    sc16is750_FIFOReset(0);

    current_wind_DIR = rwindData[5] << 8 | rwindData[6];
    current_wind_SPD = rwindData[3] << 8 | rwindData[4];
    *dir = current_wind_DIR;
    *speed = current_wind_SPD;
    return 1;

}

uint8_t sc16is750_read_windData2(unsigned int *dir,unsigned int *speed )
{
    uint8_t windData[9]={0,};
    int rwindData[18]={0,};
    int i=0;
    unsigned int current_wind_DIR = 0;
    unsigned int current_wind_SPD = 0;

    windData[0]=0x01;
    windData[1]=0x03;
    windData[2]=0x01;
    windData[3]=0xF4;
    windData[4]=0x00;
    windData[5]=0x06;
    windData[6]=0x85;
    windData[7]=0xC6;

    sc16is750_WriteRegisterMultiple(SC16IS750_REG_THR, windData,8);
    for (i=0;i<1200;i++)
        usleep(1000);
    if (sc16is750_FIFOAvailableData() != 0) {
        sc16is750_ReadRegisterMultiple(SC16IS750_REG_RHR, rwindData,17);
        // Addr Func VALID  SPD  PWR  DG  DIRD HUM   TEMP   CRCL CRCH
        // 0    1    2      3 4  5 6  7 8 9 10 11 12 13 14
    }else{
        printf("sc16is750_FIFOAvailableData - error \n");
    }

    sc16is750_FIFOReset(0);

    printf("SPD1 : %d  ", rwindData[3]<<8  | rwindData[4]);
    printf("DIR2 : %d  ", rwindData[9]<<8  | rwindData[10]);
    printf("HUM  : %d  ", rwindData[11]<<8 | rwindData[12]);
    printf("TEMP : %d  ", rwindData[13]<<8 | rwindData[14]);

    current_wind_DIR = rwindData[9] << 8 | rwindData[10];
    current_wind_SPD = rwindData[3] << 8 | rwindData[4];
    *dir = current_wind_DIR;
    *speed = current_wind_SPD;
    return 1;
}

from machine import Pin, UART, I2C
import utime
from ssd1306 import SSD1306_I2C
from micropyGPS import MicropyGPS
from ulora import LoRa, ModemConfig,SPIConfig

#LoRa parameters
RFM95_RST = 28 # pino reset lora
RFM95_SPIBUS = SPIConfig.rp2_0 # pinagem LoRa RM95 e Pico
RFM95_CS = 17 # Chip select
RFM95_INT = 20 # DIO0
RF95_FREQ = 868.0 # Frequencia de transmissao
RF95_POW = 10 # Potencia de transmissao
CLIENT_ADDRESS = 1 # endereço cliente
SERVER_ADDRESS =2 # endereço server

# initialize radio LoRa
lora = LoRa(RFM95_SPIBUS,RFM95_INT,CLIENT_ADDRESS,RFM95_CS,reset_pin = RFM95_RST,freq =RF95_FREQ, tx_power =RF95_POW,acks = True)

#Inicializa I2C e display oled
i2c = I2C(1,sda =Pin(14),scl=Pin(15),freq=400000)
oled = SSD1306_I2C(128,64,i2c)

# Inicializa GPS
gps_module = UART(0,baudrate=9600, tx=Pin(0),rx=Pin(1))
time_zone = -3 # fuso horario
gps = MicropyGPS(time_zone) # ajuste de time zone
 
#Botoes
botao_a = Pin(5,Pin.IN, Pin.PULL_UP)
botao_b = Pin(6,Pin.IN, Pin.PULL_UP)

def msg(text=''):
    lora.send_to_wait(f"{text}",SERVER_ADDRESS)

def convert_coordinates(sections):
    if sections[0] == 0:
        return None
    
    data = sections[0] +(sections[1]/60.0)

    if sections[2] == 'S':
        data = -data
    if sections[2] == 'W':
        data = -data

    data = '{0:.6f}'.format(data)
    return str(data) # retorna  o dado no formato string

while True:
    length = gps_module.any()
    if length >0:
        data = gps_module.read(length)
        for byte in data:
            message = gps.update(chr(byte))

    latitude = convert_coordinates(gps.latitude)
    longitude = convert_coordinates(gps.longitude)

    if latitude is None or longitude is None:
        oled.fill(0)
        oled.text('Data unavailable',0,10)
        oled.text('No coordinates',22,40)
        oled.show()
        continue


    oled.fill(0)
    oled.text('Satelites: '+ str(gps.satellites_in_use),10,0)
    oled.text('Lat: ' + latitude,0,18)
    oled.text('Long: '+ longitude,0,36)
    print('Long: ' + longitude)
    print('Lat: ' + latitude)
    data_gps=(f"{latitude},{longitude}")
    oled.show()

    if botao_a.value() == 0:
        oled.fill(0)
        oled.text(f"coordinates send", 0, 50, 1)
        oled.show()
        msg(data_gps)





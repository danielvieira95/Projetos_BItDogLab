from machine import Pin, SoftI2C
from time import sleep
from ulora import LoRa, ModemConfig, SPIConfig
from ssd1306 import SSD1306_I2C

#configuração do OLED
i2c = SoftI2C(scl = Pin(15),sda = Pin(14))
oled = SSD1306_I2C(128,64,i2c)

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

lora.set_mode_rx() # modo de recebimento continuo

#Botoes
botao_a = Pin(5,Pin.IN, Pin.PULL_UP)
botao_b = Pin(6,Pin.IN, Pin.PULL_UP)

#arquivo para salvar as informações
file_path = 'data2.txt'
oled.text("BitDogLab",0,0,1)
oled.show()

#função para receber os dados da comunicação LoRa
def on_recv(payload):
    print("From: ",payload.header_from)
    print("Received: ",payload.message)
    print("RSSI: {}, SNR: {}".format(payload.rssi, payload.snr))

    oled.fill(0) # limpa o oled
    oled.text(f"From: {payload.header_from}",0,10,1)
    oled.text(f" {payload.message}",0,20,1)
    oled.text(f"RSSI: {payload.rssi}",0,40,1)
    oled.text(f"SNR: {payload.snr}",0,50,1)
    oled.show()

    try: 
        file = open(file_path,'a')
        file.write(f"{payload.message}, RSSI: {payload.rssi}, SNR: {payload.snr} \n")
        print("Dado salvo")
        file.close()

    except OSError as e:
        print("Erro: ",e)
        oled.fill(0)
        oled.text(f"Erro",20,0,1)
        oled.show()
lora.on_recv = on_recv
while True:
    sleep(0.1)

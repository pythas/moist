from mqtt_as import MQTTClient, config
import uasyncio as asyncio
import dht
import machine
import json
import env

config['ssid'] = env.WIFI_SSID
config['wifi_pw'] = env.WIFI_PASSWORD
config['server'] = env.BROKER
config["queue_len"] = 1

async def messages(client):
    async for topic, msg, retained in client.queue:
        print((topic, msg, retained))

async def up(client):
    while True:
        await client.up.wait()
    
        client.up.clear()

async def main(client):
    await client.connect()
    
    for coroutine in (up, messages):
        asyncio.create_task(coroutine(client))
    
    d = dht.DHT22(machine.Pin(28))
    led = machine.Pin("LED", machine.Pin.OUT)

    while True:
        await asyncio.sleep(60)
        
        d.measure()
        
        await client.publish('dht22', json.dumps({
            "temperature": d.temperature(),
            "humidity": d.humidity(),
        }), qos = 1)
        
        # Blink LED
        led.on()
        await asyncio.sleep(0.2)
        led.off()

# MQTTClient.DEBUG = True

client = MQTTClient(config)

try:
    asyncio.run(main(client))
finally:
    client.close()

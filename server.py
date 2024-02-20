import gpiod
import time
from flask import Flask, request, jsonify, make_response

DOOR_PIN=7
LED_PIN=0
#pi = pigpio.pi()
chip = gpiod.Chip('gpiochip4')

led_line = chip.get_line(LED_PIN)
door_line = chip.get_line(DOOR_PIN)

#led_line.active_state= led_line.ACTIVE_LOW
led_line.request(consumer="LED",type=gpiod.LINE_REQ_DIR_OUT)
door_line.request(consumer="DOOR",type=gpiod.LINE_REQ_DIR_OUT)

#The device is set as a value of 1=on and 0=off however a relay works the opposite
#In our case if we want the circuit to complete we need a value of 0. If we want to turn off the circuit we use 1

#Set initial Value
door_line.set_value(1)
led_line.set_value(1)


def set_relay_controller(relay, value):
    #read 2 comments back
    if relay == "door":
        door_line.set_value(0)
        time.sleep(1)
        door_line.set_value(1)
    elif relay == "light":
        led_line.set_value(0)
        time.sleep(1)
        led_line.set_value(1)


app = Flask(__name__)


@app.route("/", methods=["POST", "OPTIONS"])
def slider_data():
    if request.method == "OPTIONS":
        response = make_response()
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        response.headers["Access-Control-Max-Age"] = "86400"
        return response

    data = request.json
    relay = data.get("relay")
    value = data.get("value")

    if not relay or value is None:
        return jsonify({"message": "Invalid data received"}), 400

    if relay in ["door", "light"]:
        set_relay_controller(relay, value)

    print(f"Received value {value} from {relay}")

    response = jsonify({"message": "Data received successfully"})
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response


if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", port=8000)
    finally:
        led_line.release()

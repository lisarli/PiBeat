import board
import adafruit_mma8451
i2c = board.I2C()
sensor = adafruit_mma8451.MMA8451(i2c)

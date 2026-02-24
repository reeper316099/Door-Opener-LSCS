import RPi.GPIO as GPIO
import time


class Control:

    IN1 = 10
    IN2 = 9
    ENA = 25
    BTN = 14

    LED_R = 17
    LED_G = 27
    LED_B = 22

    battery_supply = 100
    pwm_r = None
    pwm_g = None
    pwm_b = None
    current_color = (0, 0, 0)

    @staticmethod
    def setup():
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(Control.IN1, GPIO.OUT)
        GPIO.setup(Control.IN2, GPIO.OUT)
        GPIO.setup(Control.ENA, GPIO.OUT)
        GPIO.setup(Control.BTN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        GPIO.setup(Control.LED_R, GPIO.OUT)
        GPIO.setup(Control.LED_G, GPIO.OUT)
        GPIO.setup(Control.LED_B, GPIO.OUT)

        # Setup PWM for RGB LED, off by default only if not already initialized
        if Control.pwm_r is None:
            Control.pwm_r = GPIO.PWM(Control.LED_R, 100)
            Control.pwm_g = GPIO.PWM(Control.LED_G, 100)
            Control.pwm_b = GPIO.PWM(Control.LED_B, 100)
            Control.pwm_r.start(0)
            Control.pwm_g.start(0)
            Control.pwm_b.start(0)
            Control.current_color = (0, 0, 0)

        if Control.verified_open():
            Control.setRGB(0, 255, 0)
        else:
            Control.setRGB(255, 0, 0)

    @staticmethod
    def close():
        GPIO.output(Control.ENA, GPIO.HIGH)
        GPIO.output(Control.IN1, GPIO.HIGH)
        GPIO.output(Control.IN2, GPIO.LOW)

    @staticmethod
    def open():
        GPIO.output(Control.ENA, GPIO.HIGH)
        GPIO.output(Control.IN1, GPIO.LOW)
        GPIO.output(Control.IN2, GPIO.HIGH)

    @staticmethod # lord save me
    def verified_open():
        if GPIO.input(Control.BTN) == 0:
            Control.setRGB(0, 255, 0)
            return True

        Control.setRGB(255, 0, 0)
        return False

    @staticmethod
    def get_estimated_power():
        return 100

    @staticmethod
    def setRGB(r, g, b):
        duty_r = (r / 255.0) * 100
        duty_g = (g / 255.0) * 100
        duty_b = (b / 255.0) * 100
        Control.current_color = (r, g, b)
        Control.pwm_r.ChangeDutyCycle(duty_r)
        Control.pwm_g.ChangeDutyCycle(duty_g)
        Control.pwm_b.ChangeDutyCycle(duty_b)

    @staticmethod
    def clean():
        if Control.pwm_r:
            Control.pwm_r.stop()
        if Control.pwm_g:
            Control.pwm_g.stop()
        if Control.pwm_b:
            Control.pwm_b.stop()
        GPIO.cleanup()

if __name__ == "__main__":
    Control.setup()
    print("setup complete")
    time.sleep(3)

    print("opening door")
    Control.open()
    time.sleep(5)
    print("closing door")
    Control.close()
    #
    # while True:
    #     print(GPIO.input(Control.BTN))
    #     time.sleep(1)
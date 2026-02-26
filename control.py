import RPi.GPIO as GPIO
import time


class Control:
    """Low-level GPIO control for motor movement and RGB status indication."""

    # Motor driver pins (BCM numbering).
    IN1 = 10
    IN2 = 9
    ENA = 25

    # Digital input from a door-position switch/button.
    BTN = 14

    # RGB LED pins.
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
        """Initialize GPIO and PWM channels."""
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(Control.IN1, GPIO.OUT)
        GPIO.setup(Control.IN2, GPIO.OUT)
        GPIO.setup(Control.ENA, GPIO.OUT)
        GPIO.setup(Control.BTN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        GPIO.setup(Control.LED_R, GPIO.OUT)
        GPIO.setup(Control.LED_G, GPIO.OUT)
        GPIO.setup(Control.LED_B, GPIO.OUT)

        # Create PWM controllers once; keep them around for future requests.
        if Control.pwm_r is None:
            Control.pwm_r = GPIO.PWM(Control.LED_R, 100)
            Control.pwm_g = GPIO.PWM(Control.LED_G, 100)
            Control.pwm_b = GPIO.PWM(Control.LED_B, 100)
            Control.pwm_r.start(0)
            Control.pwm_g.start(0)
            Control.pwm_b.start(0)
            Control.current_color = (0, 0, 0)

        # Refresh LED color based on current sensor state.
        if Control.verified_open():
            Control.setRGB(0, 255, 0)
        else:
            Control.setRGB(255, 0, 0)

    @staticmethod
    def close():
        """Drive motor in the closing direction."""
        GPIO.output(Control.ENA, GPIO.HIGH)
        GPIO.output(Control.IN1, GPIO.HIGH)
        GPIO.output(Control.IN2, GPIO.LOW)

    @staticmethod
    def open():
        """Drive motor in the opening direction."""
        GPIO.output(Control.ENA, GPIO.HIGH)
        GPIO.output(Control.IN1, GPIO.LOW)
        GPIO.output(Control.IN2, GPIO.HIGH)

    @staticmethod
    def verified_open():
        """Check sensor state and update LED color accordingly."""
        if GPIO.input(Control.BTN) == 0:
            Control.setRGB(0, 255, 0)
            return True

        Control.setRGB(255, 0, 0)
        return False

    @staticmethod
    def get_estimated_power():
        """Return placeholder power estimate for API compatibility."""
        return 100

    @staticmethod
    def setRGB(r, g, b):
        """Set RGB LED value using PWM duty cycles."""
        duty_r = (r / 255.0) * 100
        duty_g = (g / 255.0) * 100
        duty_b = (b / 255.0) * 100
        Control.current_color = (r, g, b)
        Control.pwm_r.ChangeDutyCycle(duty_r)
        Control.pwm_g.ChangeDutyCycle(duty_g)
        Control.pwm_b.ChangeDutyCycle(duty_b)

    @staticmethod
    def clean():
        """Stop PWM channels and release GPIO resources."""
        if Control.pwm_r:
            Control.pwm_r.stop()
        if Control.pwm_g:
            Control.pwm_g.stop()
        if Control.pwm_b:
            Control.pwm_b.stop()
        GPIO.cleanup()


if __name__ == "__main__":
    # Minimal hardware smoke test when run directly on device.
    Control.setup()
    print("setup complete")
    time.sleep(3)

    print("opening door")
    Control.open()
    time.sleep(5)
    print("closing door")
    Control.close()

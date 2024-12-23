from serial import Serial
import ReflowPID
from temp_graph import TempGraph

from PID import PID


# ARDUINO_PORT = 'COM5'
ARDUINO_BAUD = 115200

LOOP_DELAY = float(1)

SETPOINT = 50


def main():
    profile = ReflowPID.LeadFreeProfile()
    # profile = ReflowPID.LeadProfile()
    controller = ReflowPID.ReflowController(profile)

    # pid = PID(25, 0, 80)
    # pid.sample_time = 1
    # pid.SetPoint = 90.0

    graph = TempGraph(profile)

    ARDUINO_PORT = str(input("Please enter a COM port: "))

    with Serial(ARDUINO_PORT, ARDUINO_BAUD, timeout=1) as ser:
        while True:
            temp = ser.readline()
            try:
                temp = float(temp.decode().strip())
            except ValueError:
                continue

            # pid.update(temp)
            # duty = int(round(pid.output))

            controller.update(temp)
            duty = int(round(controller.output))

            ser.write(str(duty).encode())
            ser.write(b'\n')

            if controller.current_state != controller.st_preheat_until:
                graph.update(controller.get_elapsed_time(), temp, controller.pid.SetPoint)

            print("Temp: {:.2f}, Duty: {}, Setpoint: {:.2f}".format(temp, duty, controller.pid.SetPoint))

            # time.sleep(LOOP_DELAY)


if __name__ == '__main__':
    main()

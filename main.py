import socket
from thermocouples_reference import thermocouples
import time
from serial import Serial
import ReflowPID
from temp_graph import TempGraph

DMM_IP = '192.168.1.105'
DMM_PORT = 5555

ARDUINO_PORT = 'COM5'
ARDUINO_BAUD = 115200

# ambient temperature
T_REF = 23

typek = thermocouples['K']

LOOP_DELAY = float(1)

SETPOINT = 50


def main():
    # profile = ReflowPID.LeadFreeProfile()
    profile = ReflowPID.LeadProfile()
    controller = ReflowPID.ReflowController(profile)

    graph = TempGraph(profile)

    with Serial(ARDUINO_PORT, ARDUINO_BAUD, timeout=1) as ser:
        while True:
            temp = ser.readline()
            try:
                temp = float(temp.decode().strip())
            except ValueError:
                continue

            controller.update(temp)
            duty = int(round(controller.output))

            ser.write(str(duty).encode())
            ser.write(b'\n')

            if controller.current_state != controller.st_preheat_until:
                graph.update(controller.get_elapsed_time(), temp, controller.pid.SetPoint)

            print("Temp: {:.2f}, Duty: {}, Setpoint: {}".format(temp, duty, controller.pid.SetPoint))

            # time.sleep(LOOP_DELAY)


if __name__ == '__main__':
    main()

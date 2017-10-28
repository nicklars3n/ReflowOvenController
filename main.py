import socket
from thermocouples_reference import thermocouples
import time
from serial import Serial
import ReflowPID
from temp_graph import TempGraph

DMM_IP = '192.168.1.105'
DMM_PORT = 5555

ARDUINO_PORT = 'COM9'
ARDUINO_BAUD = 115200

# ambient temperature
T_REF = 23

typek = thermocouples['K']

LOOP_DELAY = float(1)

SETPOINT = 50


def main():

    controller = ReflowPID.ReflowController()
    profile = ReflowPID.ReflowProfile()
    graph = TempGraph(profile)

    with Serial(ARDUINO_PORT, ARDUINO_BAUD, timeout=1) as ser:
        while True:
            temp = get_temperature()
            controller.update(temp)
            duty = int(round(controller.output))

            ser.write(str(duty).encode())
            ser.write(b'\n')

            if controller.current_state != controller.st_preheat_until:
                graph.update(controller.get_elapsed_time(), temp, controller.pid.SetPoint)

            print("Temp: {:.2f}, Duty: {}, Setpoint: {}".format(temp, duty, controller.pid.SetPoint))

            with open('log.csv', 'a') as f:
                f.write("{:.2f},{}\n".format(temp, duty))

            time.sleep(LOOP_DELAY)


def get_temperature():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((DMM_IP, DMM_PORT))

        s.send(b':meas:volt:dc?\n')
        resp = s.recv(1024).decode('utf-8')
        temp_mv = float(resp) * 1000
        temp_c = typek.inverse_CmV(temp_mv, Tref=T_REF)

        return temp_c


def relay_on(ser):
    ser.write(b'1')


def relay_off(ser):
    ser.write(b'0')

if __name__ == '__main__':
    main()

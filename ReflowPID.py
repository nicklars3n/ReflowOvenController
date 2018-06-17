from PID import PID
import time
import enum
from numpy import interp


class LeadFreeProfile:
    ramp = {'up_max': 1,    # max temp gradient degC/sec
            'down_max': 3,
            'up_duration': 10,
            'duty': 100,
            'prevision_time': 10}

    preheat = {'duty': 75,
               'end_temp': 60}

    soak = {'temp_min': 190,
            'temp_max': 200,
            'duration': 120}

    reflow = {'peak': 250,
              'dwell': 30}


class LeadProfile:
    ramp = {'up_max': 1,    # max temp gradient degC/sec
            'down_max': 3,
            'up_duration': 10,
            'duty': 100,
            'prevision_time': 10}

    preheat = {'duty': 75,
               'end_temp': 60}

    soak = {'temp_min': 130,
            'temp_max': 145,
            'duration': 120}

    reflow = {'peak': 210,
              'dwell': 30}


class ReflowController:
    def __init__(self, profile):
        self.pid = PID(25, 0, 80)
        self.pid.sample_time = 1
        self.output = 0

        self.current_state = self.st_preheat_until

        self.current_time = time.time()
        self.start_time = self.current_time
        self.state_begin = self.current_time
        self.state_elapsed = 0

        self.profile = profile

    def get_elapsed_time(self):
        return self.current_time - self.start_time

    def update(self, temp):
        self.current_time = time.time()
        self.state_elapsed = self.current_time - self.state_begin

        self.current_state(temp)

    def set_current_state(self, next_st):
        self.current_time = time.time()
        self.state_begin = self.current_time
        self.state_elapsed = 0
        self.current_state = next_st

    def st_preheat_until(self, temp):
        """
        Preheat open loop until the required temperature
        """
        self.output = self.profile.preheat['duty']

        if temp > self.profile.preheat['end_temp']:
            self.set_current_state(self.st_preheat)
            self.start_time = time.time()

    def st_preheat(self, temp):
        """
        Preheat closed loop until the required temperature
        """
        self.pid.SetPoint = self.profile.preheat['end_temp'] + \
                            (self.state_elapsed + self.profile.ramp['prevision_time']) * self.profile.ramp['up_max']

        self.pid.update(temp)
        self.output = self.pid.output

        if self.pid.SetPoint > self.profile.soak['temp_min']:
            self.set_current_state(self.st_soak)

    def st_soak(self, temp):
        """
        Follow the soak profile using the PID controller
        """
        slope = (self.profile.soak['temp_max'] - self.profile.soak['temp_min']) / (self.profile.soak['duration'])
        self.pid.SetPoint = slope * (self.state_elapsed + self.profile.ramp['prevision_time']) +\
                            self.profile.soak['temp_min']

        self.pid.update(temp)
        self.output = self.pid.output

        if self.state_elapsed > self.profile.soak['duration']:
            self.set_current_state(self.st_ramp_up_fixed)

    def st_ramp_up_fixed(self, temp):
        """
        Open loop ramp for fixed duration
        """
        self.output = self.profile.ramp['duty']

        if self.state_elapsed > self.profile.ramp['up_duration']:
            self.set_current_state(self.st_ramp_up)

    def st_ramp_up(self, temp):
        """
        Closed loop ramp up for controller
        """
        self.pid.SetPoint = self.profile.soak['temp_max'] + \
                            (self.state_elapsed + self.profile.ramp['prevision_time']) * self.profile.ramp['up_max']

        self.pid.update(temp)
        self.output = self.pid.output

        if self.pid.SetPoint > self.profile.reflow['peak']:
            self.set_current_state(self.st_dwell)

    def st_dwell(self, temp):
        """
        Closed loop dwell at peak temperature
        """
        self.pid.SetPoint = self.profile.reflow['peak']

        self.pid.update(temp)
        self.output = self.pid.output

        if self.state_elapsed > self.profile.reflow['dwell']:
            self.set_current_state(self.st_ramp_down)

    def st_ramp_down(self, temp):
        self.output = 0
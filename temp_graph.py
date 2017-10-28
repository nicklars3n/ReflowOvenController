import matplotlib.pyplot as plt


class TempGraph:
    def __init__(self, profile):

        plt.ion()
        self.fig, self.ax = plt.subplots()

        x = list()
        x.append(0.0)
        x.append(x[-1] + (profile.soak['temp_min'] - profile.preheat['end_temp']) / profile.ramp['up_max'])
        x.append(x[-1] + profile.soak['duration'])
        x.append(x[-1] + (profile.reflow['peak'] - profile.soak['temp_max']) / profile.ramp['up_max'])
        x.append(x[-1] + profile.reflow['dwell'])
        x.append(x[-1] + (profile.reflow['peak'] - 60) / profile.ramp['down_max'])

        self.profile_x = x

        self.profile_y = [profile.preheat['end_temp'], profile.soak['temp_min'], profile.soak['temp_max'],
                          profile.reflow['peak'], profile.reflow['peak'], 60]

        self.x = []
        self.y = []

    def update(self, new_x, new_y, set_y):
        self.x.append(new_x)
        self.y.append(new_y)

        self.ax.clear()
        plt.xlabel('Time, s')
        plt.ylabel('Temperature, \xb0C')
        self.ax.plot(self.profile_x, self.profile_y)
        self.ax.plot(self.x, self.y)

        plt.axvline(new_x, linewidth=0.5, color='k', linestyle='--')
        plt.axhline(set_y, linewidth=0.5, color='k', linestyle='--')

        plt.pause(0.0001)


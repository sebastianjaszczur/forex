import csv
import collections

from settings import START_CAPITAL, SPREAD, LEVERAGE, NUMBER_TYPE
from datetime import datetime
from copy import deepcopy

VERSION_NUMBER = 1.1

print("API version {version}".format(version=VERSION_NUMBER))

DataRecord = collections.namedtuple('DataRecord', [
    'timestamp', 'open', 'high', 'low', 'close', 'volume'])


def timecsv_to_datetime(timecsv):
    year = int(timecsv[:4])
    month = int(timecsv[4:6])
    day = int(timecsv[6:8])

    blank = timecsv[8]

    hour = int(timecsv[9:11])
    minute = int(timecsv[11:13])
    seconds = int(timecsv[13:15])
    return datetime(year, month, day, hour, minute, seconds)


class RawData(list):
    def __init__(self, filename):
        with open(filename, 'r') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=';', quotechar='|')
            for row in list(spamreader):
                row[0] = timecsv_to_datetime(row[0])
                row[1:-1] = [NUMBER_TYPE(x) for x in row[1:-1]]
                row[-1] = int(row[-1])
                self.append(DataRecord(*row))
        self.filename = filename

    def __hash__(self):
        return hash(self.filename)


class Simulation(object):
    def __init__(self, raw_data, raw_history_data, spread=SPREAD,
                 start_capital=START_CAPITAL, leverage=LEVERAGE):
        self.spread = NUMBER_TYPE(str(spread))
        self._raw_data = raw_data
        self._history_raw_data = deepcopy(raw_history_data)
        self.current_time = -1
        self.capital = NUMBER_TYPE(start_capital)
        self.currency = NUMBER_TYPE(0.0)
        self.leverage = NUMBER_TYPE(leverage)

    def __iter__(self):
        return self

    @property
    def currency_value(self):
        return self.currency * (self.price[0] if self.currency < 0
                                else self.price[1]) / self.leverage

    @property
    def all_value(self):
        return self.capital + self.currency_value

    def reset(self):
        self.buy(-self.currency / self.leverage)

    def buy(self, value):
        if value >= 0:
            self.currency += value * self.leverage
            self.capital -= value * self.price[1]
        else:
            self.currency += value * self.leverage
            self.capital -= value * self.price[0]

        self.check_for_bankruptcy()

    def sell(self, value):
        return self.buy(-value)

    def check_for_bankruptcy(self):
        if self.all_value < 0:
            raise ValueError("Bankrupt because of no money!")
        if (self.all_value * self.leverage <
            abs(self.currency / (self.price[0] if self.currency < 0
                                 else self.price[1]))):
            raise ValueError("Bankrupt because of leverage!")

    def __next__(self):
        return self.next()

    def next(self):
        self.check_for_bankruptcy()
        self._history_raw_data.append(self._raw_data[self.current_time])

        self.current_time += 1
        if self.current_time >= len(self._raw_data):
            raise StopIteration()
        result = self.price
        return result

    def history_price(self, index):
        if index == 0:
            return self.price
        if index > 0:
            raise ValueError("You cannot see the future.")
        return (self._history_raw_data[index].open,
                self._history_raw_data[index].open+self.spread)

    @property
    def timedelta(self):
        try:
            return (self._raw_data[self.current_time+1].timestamp -
                    self._raw_data[self.current_time].timestamp).total_seconds()
        except IndexError:
            return 1000000.0

    @property
    def price(self):
        try:
            return (self._raw_data[self.current_time].open,
                    self._raw_data[self.current_time].open+self.spread)
        except IndexError:
            return (self._raw_data[self.current_time-1].close,
                    self._raw_data[self.current_time-1].close+self.spread)


def simulate(raw_data, old_data, decisioner, executioner, **kwargs):
    simulation = Simulation(raw_data, old_data, **kwargs)
    for price in simulation:
        decision = decisioner.decision(simulation)

        executioner.execute(simulation, decision)
    simulation.reset()
    return simulation.all_value


# this is the end of library things


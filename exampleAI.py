from settings import DATA_FILES, START_CAPITAL
from forex import RawData, simulate
import random


class Executioner(object):

    def execute(self, simulation, decision):
        if decision == "BUY":
            simulation.buy(simulation.all_value * 0.9)
        elif decision == "SELL":
            simulation.sell(simulation.all_value * 0.9)
        elif decision == "RESET":
            simulation.reset()
        elif decision == "HOLD":
            pass
        else:
            raise ValueError("Wrong decision '{0}'".format(decision))


class Decisioner(object):
    choices = [
        "BUY", "SELL", "RESET", "HOLD"
    ]

    def __init__(self):
        pass

    def decision(self, simulation):

        if simulation.timedelta > 300:
            return "RESET"

        decision = None
        if simulation.history_price(-1) > simulation.history_price(-2):
            decision = -1
        elif simulation.history_price(-1) < simulation.history_price(-2):
            decision = 1
        else:
            decision = 0

        # decision = random.randint(-1, 1)

        if decision == 0:
            if simulation.currency == 0:
                return "HOLD"
            else:
                return "RESET"
        elif decision == 1:
            if simulation.currency > 0:
                return "HOLD"
            elif simulation.currency == 0:
                return "BUY"
            elif simulation.currency < 0:
                return "RESET"
            else:
                raise ValueError("Wrong decision!", decision)
        elif decision == -1:
            if simulation.currency < 0:
                return "HOLD"
            elif simulation.currency == 0:
                return "SELL"
            elif simulation.currency > 0:
                return "RESET"
            else:
                raise ValueError("Wrong decision!", decision)
        else:
            raise ValueError("Wrong decision!", decision)

        raise ValueError("Something uncatched in tree!", decision)

# end of definitions of functions

executioner = Executioner()
decisioner = Decisioner()

raw_data = dict([(year, RawData(DATA_FILES[year]))
                 for year in [2010, 2011, 2012, 2013]])

for year in [2011, 2012, 2013]:
    print("Result for {year}".format(year=year))
    end_cash = simulate(raw_data[year], raw_data[year - 1], decisioner,
                        executioner)
    print("{end_cash} - {percent}%".format(
        end_cash=end_cash, percent=round(end_cash / START_CAPITAL * 100, 3)))

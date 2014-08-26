from settings import DATA_FILES
from forex import RawData, simulate
import random


class Executioner(object):
    def execute(self, simulation, decision):
        if decision == "BUY":
            simulation.buy(simulation.all_value*0.9)
        elif decision == "SELL":
            simulation.sell(simulation.all_value*0.9)
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

        #decision = random.randint(-1, 1)

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

for year in [2011, 2012, 2013]:
    print "Result for {year}".format(year=year)
    print simulate(RawData(DATA_FILES[year]), RawData(DATA_FILES[year-1]),
                   decisioner, executioner)

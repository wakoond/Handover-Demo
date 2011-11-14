
from threading import Thread
from time import sleep, time
import threading
from RaClient import RaClient


class RacAutoThread (Thread):

    RAT_ST_IDLE = '1'
    RAT_ST_AR1 = '2'
    RAT_ST_BOTH_AR1 = '3'
    RAT_ST_BOTH_AR2 = '4'
    RAT_ST_AR2 = '5'

    def __init__(self, rac, interval):
        self._rac = rac
        self._interval = interval
        Thread.__init__(self)

        self._both_interval = 5
        self._state = RacAutoThread.RAT_ST_IDLE
        self._stop = threading.Event()

    def SetBothInterval(self, i):
        self._both_interval = i

    def Stop(self):
        self._stop.set()
        self.join()

    def _IsStopped(self):
        return self._stop.isSet()

    def run(self):
        self._rac.SendStart(RaClient.AR2)
        self._rac.SendStart(RaClient.AR1)
        self._state = RacAutoThread.RAT_ST_BOTH_AR1

        sleep_itval = 0
        while not self._IsStopped():
            if self._state == RacAutoThread.RAT_ST_BOTH_AR1:
                self._rac.SendStop(RaClient.AR1)
                sleep_itval = self._interval
                self._state == RacAutoThread.RAT_ST_AR2
            elif self._state == RacAutoThread.RAT_ST_AR2:
                self._rac.SendStart(RaClient.AR1)
                sleep_itval = self._both_interval
                self._state == RacAutoThread.RAT_ST_BOTH_AR2
            elif self._state == RacAutoThread.RAT_ST_BOTH_AR2:
                self._rac.SendStop(RaClient.AR2)
                sleep_itval = self._interval
                self._state == RacAutoThread.RAT_ST_AR1
            elif self._state == RacAutoThread.RAT_ST_AR1:
                self._rac.SendStart(RaClient.AR2)
                sleep_itval = self._both_interval
                self._state == RacAutoThread.RAT_ST_BOTH_AR1
            sleep(sleep_itval)

# DC Metro Board
import time

import board
import digitalio

from config import config
from train_board import TrainBoard
from metro_api import MetroApi, MetroApiOnFireException, _network

STATION_CODE = config['metro_station_code']
TRAIN_GROUP = config['train_group']
ALT_TRAIN_GROUP = config['alt_train_group']
WEEKEND_START_HOUR = config['weekend_start_hour']
REFRESH_INTERVAL = config['refresh_interval'] * 10

button_up = digitalio.DigitalInOut(board.BUTTON_UP)
button_up.direction = digitalio.Direction.INPUT
button_up.pull = digitalio.Pull.UP

button_down = digitalio.DigitalInOut(board.BUTTON_DOWN)
button_down.direction = digitalio.Direction.INPUT
button_down.pull = digitalio.Pull.UP

byWeekDay = True
weekDaySwitch = False

def refresh_trains() -> [dict]:
    try:
        today = time.localtime()
        print(today)
        dayNum = today.tm_wday
        hour = today.tm_hour
        if dayNum > 4:
            isWeekend = True
            print('Its the Weekend')
        elif dayNum == 4 and hour > WEEKEND_START_HOUR:
            isWeekend = True
            print('Its the Weekend on Friday')
        else:
            isWeekend = False
            print('Its the Week')

        useAlt = not isWeekend
        if not byWeekDay:
            useAlt = not useAlt == weekDaySwitch

        if not useAlt:
            currentTrainGroup = TRAIN_GROUP
        else:
            currentTrainGroup = ALT_TRAIN_GROUP

        return MetroApi.fetch_train_predictions(STATION_CODE, currentTrainGroup)
    except MetroApiOnFireException:
        print('WMATA Api is currently on fire. Trying again later ...')
        return None

train_board = TrainBoard(refresh_trains)
# Set the time from the internet
_network.get_local_time()

counter = 0
while True:
    if not button_up.value:
        byWeekDay = True
        weekDaySwitch = False
    elif not button_down.value:
        byWeekDay = False
        weekDaySwitch = not weekDaySwitch
    elif counter != REFRESH_INTERVAL:
        counter = counter + 1
        time.sleep(0.1)
        continue

    counter = 0
    train_board.refresh()
    time.sleep(0.1)

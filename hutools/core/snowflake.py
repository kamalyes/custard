# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@File    :  snowflake.py
@Time    :  2022/5/27 12:09 AM
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  None
"""
import time

twepoch = 1292978355588

worker_id_bits = 5
data_center_id_bits = 5
max_worker_id = -1 ^ (-1 << worker_id_bits)
max_data_center_id = -1 ^ (-1 << data_center_id_bits)
sequence_bits = 12
worker_id_shift = sequence_bits
data_center_id_shift = sequence_bits + worker_id_bits
timestamp_left_shift = sequence_bits + worker_id_bits + data_center_id_bits
sequence_mask = -1 ^ (-1 << sequence_bits)


def snowflake_to_timestamp(_id):
    _id = _id >> 22  # strip the lower 22 bits
    _id += twepoch  # adjust for twitter epoch
    _id = _id / 1000  # convert from milliseconds to seconds
    return _id


def generator(worker_id, data_center_id, sleep=lambda x: time.sleep(x / 1000.0)):
    assert 0 <= worker_id <= max_worker_id
    assert 0 <= data_center_id <= max_data_center_id

    last_timestamp = -1
    sequence = 0

    while True:
        timestamp = int(time.time() * 1000)

        if last_timestamp > timestamp:
            print("clock is moving backwards. waiting until %i" % last_timestamp)
            sleep(last_timestamp - timestamp)
            continue

        if last_timestamp == timestamp:
            sequence = (sequence + 1) & sequence_mask
            if sequence == 0:
                print("sequence overrun")
                sequence = -1 & sequence_mask
                sleep(1)
                continue
        else:
            sequence = 0

        last_timestamp = timestamp
        yield (((timestamp - twepoch) << timestamp_left_shift) |
               (data_center_id << data_center_id_shift) |
               (worker_id << worker_id_shift) |
               sequence)


if __name__ == '__main__':
    s = generator(1, 1)
    for i in range(1000000):
        print(s.__next__())

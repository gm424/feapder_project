# snowflake/generator.py

import time
import threading

class Snowflake:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(Snowflake, cls).__new__(cls)
                    cls._instance._init(*args, **kwargs)
        return cls._instance

    def _init(self, data_center_id=1, machine_id=1, sequence=0):
        self.data_center_id = data_center_id
        self.machine_id = machine_id
        self.sequence = sequence

        self.data_center_id_bits = 5
        self.machine_id_bits = 5
        self.sequence_bits = 12

        self.max_data_center_id = -1 ^ (-1 << self.data_center_id_bits)
        self.max_machine_id = -1 ^ (-1 << self.machine_id_bits)
        self.max_sequence = -1 ^ (-1 << self.sequence_bits)

        self.data_center_id_shift = self.sequence_bits + self.machine_id_bits
        self.machine_id_shift = self.sequence_bits
        self.timestamp_shift = self.sequence_bits + self.machine_id_bits + self.data_center_id_bits

        self.epoch = 1288834974657

        self.last_timestamp = -1

        if self.data_center_id > self.max_data_center_id or self.data_center_id < 0:
            raise ValueError(f"data_center_id can't be greater than {self.max_data_center_id} or less than 0")
        if self.machine_id > self.max_machine_id or self.machine_id < 0:
            raise ValueError(f"machine_id can't be greater than {self.max_machine_id} or less than 0")

    def _current_timestamp(self):
        return int(time.time() * 1000)

    def _wait_for_next_millis(self, last_timestamp):
        timestamp = self._current_timestamp()
        while timestamp <= last_timestamp:
            timestamp = self._current_timestamp()
        return timestamp

    def generate_id(self):
        with self._lock:
            timestamp = self._current_timestamp()

            if timestamp < self.last_timestamp:
                raise Exception("Clock moved backwards. Refusing to generate id")

            if self.last_timestamp == timestamp:
                self.sequence = (self.sequence + 1) & self.max_sequence
                if self.sequence == 0:
                    timestamp = self._wait_for_next_millis(self.last_timestamp)
            else:
                self.sequence = 0

            self.last_timestamp = timestamp

            id = ((timestamp - self.epoch) << self.timestamp_shift) | \
                 (self.data_center_id << self.data_center_id_shift) | \
                 (self.machine_id << self.machine_id_shift) | \
                 self.sequence

            return str(id).zfill(19)

# 全局获取 Snowflake 实例的函数
def get_snowflake_id():
    return Snowflake().generate_id()

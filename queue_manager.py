import constants
import datetime
import math
import time


class QueueManager:
    class Node:
        def __init__(self, token, time):
            self.token = token
            self.time = time
            self.next = None

    def __init__(self, tokens):
        time_in_seconds = datetime.datetime.today().timestamp()
        self.head = self.Node(tokens[0], time_in_seconds)
        self.holder = self.head

        for token in tokens[1:]:
            time_in_seconds = datetime.datetime.today().timestamp()
            node = self.Node(token, time_in_seconds)

            self.holder.next = node
            self.holder = node

        self.holder.next = self.head
        self.holder = self.head

    def get_available_bot_token(self):
        current_time_in_seconds = datetime.datetime.today().timestamp()
        elapsed_time_in_seconds = current_time_in_seconds - self.holder.time
        min_allowed_elapsed_time_in_seconds = constants.TIME_LIMIT * \
            constants.MAX_RESPONSE_PER_MINUTE / 2
        remaining_time_in_seconds = math.ceil(
            min_allowed_elapsed_time_in_seconds - elapsed_time_in_seconds)

        if elapsed_time_in_seconds < min_allowed_elapsed_time_in_seconds:
            time.sleep(remaining_time_in_seconds)

        return self.holder.token

    def dequeue(self):
        current_time_in_seconds = math.ceil(
            datetime.datetime.today().timestamp())
        self.holder.time = current_time_in_seconds
        self.holder = self.holder.next

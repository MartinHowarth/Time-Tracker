import logging


class Week(object):
    def __init__(self, week_index, details):
        logging.debug("Creating week with index: %d" % week_index)
        self.time_tracked = details
        self.index = week_index

    def add_subtask(self):
        self.time_tracked.append(0)

    def get_total_time(self):
        """
        Gets the total time spent this week on given task.
        :return float:
        """
        count = 0
        for value in self.time_tracked:
            count += value

        return count

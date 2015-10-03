import logging


class WeekSlot(object):
    """
    Object that stores the time tracked against each task and its subtasks in a given week.
    """
    def __init__(self, week_index, details):
        """

        :param int week_index: Index of week
        :param list details: Initial values to store. List of floats.
        :return:
        """
        logging.debug("Creating week with index: %d" % week_index)
        self.time_tracked = details
        self.index = week_index

    def add_subtask(self):
        """
        Adds a subtask. Adds a blank (0) entry to the internal storage list.
        :return:
        """
        logging.debug("Adding new blank subtask to a week with index %d" % self.index)
        self.time_tracked.append(0)

    def get_total_time(self):
        """
        Gets the total time tracked in this WeekSlot. This is equivalent to the time tracked against a specific task
        in this week.
        :return float:
        """
        count = 0
        for value in self.time_tracked:
            count += value

        return count

    def get_time_in_entry(self, index):
        """
        Gets the time from a specific tracking entry box.
        That is either the main task, or any of its subtasks.
        Index 0 = Main task; higher are subtasks in order.
        :param int index: Index to get entered data from.
        :return:
        """
        logging.debug("Getting time for week index %d in subtask slot %d" % (self.index, index))
        if index > len(self.time_tracked) - 1:
            # Return 0 for weeks that existed before this subtask was added.
            return 0
        else:
            return self.time_tracked[index]

    def update_values(self, values):
        """
        Overwrite the stored values with provided values. The provided values overwrite the stored ones in a linear
        manner starting from the 0 index.
        E.g. If len(values) is less than the number of stored values, the last stored values will remain unchanged.
        :param list values: List of floats to overwrite stored values with
        :return:
        """
        if len(values) > len(self.time_tracked):
            logging.error("Too many values provided for week %d. Expected %d values, got %d" %
                          (self.index, len(self.time_tracked), len(values)))

        for i, value in enumerate(values):
            self.time_tracked[i] = value
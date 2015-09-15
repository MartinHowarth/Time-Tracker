import logging


class WeekSlot(object):
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

    def get_time_in_entry(self, index):
        logging.debug("Getting time for week index %d in subtask slot %d" % (self.index, index))
        print len(self.time_tracked)
        if index > len(self.time_tracked) - 1:
            # Return 0 for weeks that existed before this subtask was added.
            return 0
        else:
            return self.time_tracked[index]

    def update_values(self, values):
        if len(values) != len(self.time_tracked):
            logging.error("New values provided for week index %d are not of correct length. Expected length %d, "
                          "got length %d" %
                          (self.index, len(self.time_tracked), len(values)))
        self.time_tracked = values
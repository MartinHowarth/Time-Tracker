import weekslot
import logging


class Task(object):
    def __init__(self, name, first_week_id, subtasks=None, weeks=None, archived=False):
        """
        Task object. Stores time tracking about a task for all weeks.
        :param str name: Name of this task
        :param first_week_id: ID of the first week that this task appears.
        :param list subtasks: Name of each subtask, in order to be displayed.
        :param list weeks: List of lists. Each list is the time spent on
            corresponding subtasks in that week.
        :param bool archived: Whether this task is to be displayed or not.
        :return:
        """
        self.task_name = name
        self.first_week_id = first_week_id
        self.archived = archived

        if subtasks is None:
            self.subtasks = []
        else:
            for subtask in subtasks:
                self.add_subtask(subtask)

        self.weeks = []
        if weeks is None:
            # Add one week. Expect that if no details are passed in,
            # then this will be the highest week index.
            # I.e. the most recent week.
            self.add_week(self.first_week_id)
        else:
            for i, _week in enumerate(weeks):
                week_index = self.first_week_id + i
                self.add_week(week_index, _week)

    def add_subtask(self, subtask_name):
        self.subtasks.append(subtask_name)

        # Add subtask slot to latest week only.
        if self.weeks:
            self.weeks[-1].add_subtask()

    def add_week(self, week_index, details=None):
        if self.archived:  # Archived tasks do not get weeks added to them.
            return

        if details is None:
            # Add 0 at start for overall task.
            details = [0] + [0 for _ in self.subtasks]
        self.weeks.append(weekslot.WeekSlot(week_index, details))

    def get_total_time(self):
        count = 0
        for _week in self.weeks:
            count += _week.get_total_time()
        return count

    def get_total_subtask_times(self):
        counter = [self.get_time_for_subtask(subtask_name) for
                   subtask_name in self.subtasks]

        return counter

    def get_time_for_subtask(self, subtask_name):
        logging.debug("Getting time for subtask %s" % subtask_name)
        counter = 0

        # Subtask index is actually 1 higher for a week object because the first slot is for the main task entry.
        subtask_index = self.subtasks.index(subtask_name) + 1
        for _week in self.weeks:
            counter += _week.get_time_in_entry(subtask_index)

        return counter

    def get_time_for_week(self, week_index):
        logging.debug("Getting time for week %d" % week_index)
        if week_index >= self.first_week_id:
            return self.weeks[week_index - self.first_week_id].get_total_time()
        else:
            return 0

    def __repr__(self):
        return str(self)

    def __str__(self):
        return self.task_name
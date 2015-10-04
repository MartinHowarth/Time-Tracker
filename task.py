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
        self.archive_after_update = False

        if subtasks is None:
            # If we are creating a new task, initialise an empty list of subtasks
            self.subtasks = []
        else:
            # Otherwise, set the subtask list to be that passed in.
            self.subtasks = subtasks

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


    def check_subtask_name_validity(self, name):
        """
        Checks whether a sub task name already exists in this task.
        :param str name: Name to check
        :return bool: True if the supplied name doesn't already exist. False if it does.
        """
        if name in self.subtasks:
            logging.warning("A subtask with name %s already exists." % name)
            return False
        return True

    def rename_subtask(self, old_name, new_name):
        """
        Rename a subtask. Preserves subtask ordering.
        :param str old_name: Old name of the subtask
        :param str new_name: New name of the subtask
        :return:
        """
        if self.check_subtask_name_validity(new_name):
            subtask_index = self.subtasks.index(old_name)
            self.subtasks[subtask_index] = new_name

    def add_subtask(self, subtask_name):
        """
        Adds a subtask to this task.
        Consists of adding the subtask name to the list of subtasks, and adding a blank entry to the latest week that
        this task is present in.
        :param str subtask_name: Name of new subtask
        :return:
        """
        self.subtasks.append(subtask_name)

        # Add subtask slot to latest week only.
        if self.weeks:
            self.weeks[-1].add_subtask()

    def add_week(self, week_index, details=None):
        """
        Adds a new week to this task.
        Do not add a new week to archived tasks.
        Creates a WeekSlot object for the new week and populates it with specified or default values.
        :param int week_index: Index of week to add
        :param list details: List of floats containing initial values to fill in the week with.
        :return:
        """
        if self.archived:  # Archived tasks do not get weeks added to them.
            logging.debug("Not adding week to task %s because it is archived." % self)
            return

        if details is None:
            # Add 0 at start for overall task.
            details = [0] + [0 for _ in self.subtasks]
        self.weeks.append(weekslot.WeekSlot(week_index, details))

    def get_total_time(self):
        """
        Gets the total time tracked against this task across all weeks and subtasks.
        :return float: Total time tracked
        """
        count = 0
        for _week in self.weeks:
            count += _week.get_total_time()
        return count

    def get_total_subtask_times(self):
        """
        Gets the time tracked against each subtask across all weeks.
        :return list: List of floats for time tracked against each subtask, in name order
        """
        counter = [self.get_time_for_subtask(subtask_name) for
                   subtask_name in self.subtasks]

        return counter

    def get_time_for_subtask(self, subtask_name):
        """
        Gets the time tracked against a specific subtask across all weeks
        :param str subtask_name: Subtask name
        :return float: Time tracked against specific subtask
        """
        logging.debug("Getting time for subtask %s" % subtask_name)
        counter = 0

        # Subtask index is actually 1 higher for a week object because the first slot is for the main task entry.
        subtask_index = self.subtasks.index(subtask_name) + 1
        for _week in self.weeks:
            counter += _week.get_time_in_entry(subtask_index)

        return counter

    def get_time_for_week(self, week_index):
        """
        Gets the total time tracked for a specified week, across all subtasks and the main task entry
        :param int week_index: Week index
        :return float: Time tracked this week for this task.
        """
        logging.debug("Getting time for week %d" % week_index)
        if week_index >= self.first_week_id:
            offset_index = week_index - self.first_week_id
            if offset_index > len(self.weeks) - 1:
                logging.debug("Week has been archived since before week index %d was added." % week_index)
            else:
                return self.weeks[offset_index].get_total_time()
        return 0

    def __repr__(self):
        return str(self)

    def __str__(self):
        return self.task_name
import weekslot
import logging
import subtask


class Task(object):
    def __init__(self, name, first_week_id, subtasks=None, weeks=None, archived=False):
        """
        Task object. Stores time tracking about a task for all weeks.
        :param str name: Name of this task
        :param first_week_id: ID of the first week that this task appears.
        :param list[subtask.Subtask] subtasks: List of each subtask, in order to be displayed.
        :param list weeks: List of lists. Each list is the time spent on
            corresponding subtasks in that week.
        :param bool archived: Whether this task is to be displayed or not.
        :return:
        """
        self.task_name = name
        self.first_week_id = first_week_id
        self.archived = False
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
                # Make a copy of the list to pass in so we're not using the instance of the list that exists in the
                # datastore
                self.add_week(week_index, list(_week))

        # After object has been created correctly, flag whether it should be hidden or not.
        self.archived = archived

    @property
    def estimate(self):
        """
        Gets the cumulative estimate over all subtasks.
        :return int: Total estimate for all subtasks combined.
        """
        est = 0
        for sub in self.subtasks:
            est += sub.estimate

        return est

    def check_subtask_name_validity(self, name):
        """
        Checks whether a sub task name already exists in this task.
        :param str name: Name to check
        :return bool: True if the supplied name doesn't already exist. False if it does.
        """
        if name in [sub.name for sub in self.subtasks]:
            logging.warning("A subtask with name %s already exists." % name)
            return False
        return True

    def rename_subtask(self, _subtask, new_name):
        """
        Rename a subtask. Preserves subtask ordering.
        :param subtask.Subtask _subtask: Subtask to be renamed
        :param str new_name: New name of the subtask
        :return:
        """
        if self.check_subtask_name_validity(new_name):
            subtask_index = self.subtasks.index(_subtask)
            self.subtasks[subtask_index].name = new_name
            _subtask.name = new_name

    def add_subtask(self, subtask_name):
        """
        Adds a subtask to this task.
        Consists of adding the subtask name to the list of subtasks, and adding a blank entry to the latest week that
        this task is present in.
        :param str subtask_name: Name of new subtask
        :return:
        """
        new_subtask = subtask.Subtask(subtask_name)
        self.subtasks.append(new_subtask)

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
            details = [0 for _ in self.subtasks]
        self.weeks.append(weekslot.WeekSlot(week_index, details))

    def get_weekslot(self, week_index):
        """
        Gets the reference to a week (from self.weeks) by global index. Accounts for offset due to not all tasks
        starting in the same week
        :param int week_index: Global week index to translate
        :return week.Week: Internal week.
        :return None: If that week doesn't exist internally.
        """
        for _week in self.weeks:
            if _week.index == week_index:
                return _week

        logging.debug("Task has no data for requested week with index: %s" % week_index)
        return None

    def get_total_time_spent(self):
        """
        Gets the total time tracked against this task across all weeks and subtasks.
        :return float: Total time tracked
        """
        count = 0
        for _week in self.weeks:
            count += _week.get_total_time_spent()
        return count

    def get_total_subtask_times(self):
        """
        Gets the time tracked against each subtask across all weeks.
        :return list: List of floats for time tracked against each subtask, in name order
        """
        counter = [self.get_time_for_subtask(_subtask) for
                   _subtask in self.subtasks]

        return counter

    def get_time_for_subtask(self, _subtask):
        """
        Gets the time tracked against a specific subtask across all weeks
        :param subtask.Subtask _subtask: Subtask
        :return float: Time tracked against specific subtask
        """
        logging.debug("Getting time for subtask %s" % _subtask.name)
        counter = 0

        subtask_index = self.subtasks.index(_subtask)
        for _week in self.weeks:
            counter += _week.get_time_in_entry(subtask_index)

        return counter

    def get_time_for_subtask_in_week(self, _subtask, week_index):
        """
        Gets the time tracked for a given subtask in a given week.
        :param subtask.Subtask _subtask: Subtask to query
        :param int week_index: Week to query
        :return float: Time tracked
        """
        subtask_index = self.subtasks.index(_subtask)
        _week = self.get_weekslot(week_index)
        if _week is not None:
            return self.get_weekslot(week_index).get_time_in_entry(subtask_index)
        else:
            return 0

    def get_time_for_week(self, week_index):
        """
        Gets the total time tracked for a specified week, across all subtasks and the main task entry
        :param int week_index: Week index
        :return float: Time tracked this week for this task.
        """
        logging.debug("Getting time for week %d" % week_index)
        if week_index >= self.first_week_id:
            _week = self.get_weekslot(week_index)
            if _week is not None:
                return self.get_weekslot(week_index).get_total_time_spent()
        return 0

    def week_summary(self, week_index):
        """
        Generate formatted text containing details of time tracked on this task in a given week.
        :param int week_index: Week to summarise
        :return string: Summary of week for this task.
        """
        summary = "%s: %s\n" % (self.task_name, self.get_time_for_week(week_index))
        for _subtask in self.subtasks:
            summary += "\t%s: %s\n" % (_subtask.name, self.get_time_for_subtask_in_week(_subtask, week_index))
        return summary

    def __repr__(self):
        return str(self)

    def __str__(self):
        return self.task_name

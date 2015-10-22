import logging
import json
import task
import datetime
import os

"""
Data stored as follows:
{tasks: {task_name: {weeks: [
                                [<time tracked>, ...]  # Time tracked per task in same order as subtasks.
                             ],
                     first_week_id: <int>,  # ID of first week this task appears in.
                     subtasks: [<sub tasks>],  # Defines name and ordering of subtasks.
                     archived: <boolean>  # Defines whether task is to be displayed.
                     }
        }
task_order = [task_name]  # list of task names which is the order in which they are shown.
first_date = <date>
archived_week_index = <int>
}
"""


class DataStore(object):
    """
    Object that saves and loads text files.
    Responsible for abstracting the contents of the file into a
    form that can be easily passed to the Tracker object.
    """
    def __init__(self, filename=None):
        """
        :param str filename: Filename with file path for where to load/save.
        :return:
        """
        self.filename = filename
        self.raw_data = {}

        if self.filename and os.path.exists(filename):
            self.load_from_file()
        else:
            self.raw_data['task_order'] = []
            self.raw_data['tasks'] = {}
            self.raw_data['first_date'] = datetime.datetime.strftime(datetime.datetime.today(), "%Y-%m-%d")
            self.raw_data['archived_week_index'] = 0

    @property
    def tasks(self):
        """
        Read-only access to the raw task data
        :return dict: Dict of {task_name: task_details}
        """
        return self.raw_data['tasks']

    @property
    def task_order(self):
        """
        Read-only access to the task order.
        :return list[str]:
        """
        return self.raw_data['task_order']

    @property
    def archived_week_index(self):
        """
        Read-only access to the archived week index.
        :return int: Archived week index
        """
        return self.raw_data['archived_week_index']

    @property
    def first_date(self):
        """
        Returns the date of the first week as a datetime.datetime object.
        :return datetime.datetime: Date of the first week
        """
        return datetime.datetime.strptime(self.raw_data['first_date'], "%Y-%m-%d")

    def load_from_file(self):
        """
        Load from preconfigured filename. Populates self.raw_data dictionary from the file contents.
        Expects a file in JSON format, following the structure described at the top of this file.
        """
        logging.debug("Loading datastore from file: %s" % self.filename)
        with open(self.filename, 'r') as save_file:
            file_contents = ''.join(save_file.readlines())
            self.raw_data = json.loads(file_contents)

    def save_to_file(self):
        """
        Saves the raw_data dict to pre-specified filename. Stores in JSON format, according to structure at the top of
        this file.
        """
        logging.debug("Saving datastore to file: %s" % self.filename)
        json_to_save = json.dumps(self.raw_data)

        with open(self.filename, 'w') as save_file:
            save_file.writelines(json_to_save)

    def get_raw_task(self, task_name):
        """
        Gets the raw task details associated with a given task name.
        :param str task_name:
        :return dict: Dict of raw task details
        """
        return self.tasks[task_name]

    def get_highest_week_id(self):
        """
        Returns the ID of the latest week. This tells us how many weeks exist.
        :return int: Highest stored week index.
        """
        highest_index = 0
        for _task in self.tasks.itervalues():
            last_task_index = _task['first_week_id'] + len(_task['weeks'])
            if last_task_index > highest_index:
                highest_index = last_task_index

        return highest_index

    def create_task(self, task_name):
        """
        Creates a Task object by parsing the stored data for given task name.
        :param str task_name: Task name to create a task for.
        :return task.Task: Task object for given task name.
        """
        # Get the raw task dict
        raw_task = self.get_raw_task(task_name)

        # Pluck out required information
        first_week_id = raw_task['first_week_id']
        subtasks = raw_task['subtasks']
        weeks = raw_task['weeks']
        archived = raw_task['archived']

        # Create the new task and store it.
        return task.Task(task_name, first_week_id, subtasks, weeks, archived)

    def save_task(self, _task):
        """
        Converts a live instance of a task into an entry in the raw_data dict.
        :param task.Task _task: Task to be stored.
        """
        task_dict = {'archived': _task.archived,
                     'subtasks': _task.subtasks,
                     'first_week_id': _task.first_week_id,
                     'weeks': [week.time_tracked for week in _task.weeks],
                     }

        self.raw_data['tasks'][_task.task_name] = task_dict

    def save_archived_week_index(self, index):
        """
        Stores the archived week index into the raw_data dict.
        :param int index: Archived week index to store
        """
        self.raw_data['archived_week_index'] = index

    def save_first_date(self, date):
        """
        Stores the date of the first week into the raw_data dict.
        :param datetime.datetime date: Date of the first week.
        """
        self.raw_data['first_date'] = datetime.datetime.strftime(date, "%Y-%m-%d")

    def save_task_order(self, task_order):
        """
        Stores the order that tasks are displayed in.
        :param list[str] task_order: String list of task names.
        """
        self.raw_data['task_order'] = task_order

    def save_tracker(self, tracker):
        """
        Saves all members of a tracker object.
        :param tracker.Tracker tracker: Tracker object to store.
        """
        for _task in tracker.tasks.itervalues():
            self.save_task(_task)

        self.save_archived_week_index(tracker.archived_week_index)
        self.save_first_date(tracker.first_date)
        self.save_task_order(tracker.task_order)

        print self.raw_data
        self.save_to_file()
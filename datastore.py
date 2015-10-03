import logging
import json
import task
import datetime

"""
Data stored as follows:
{tasks: [{weeks: [
                    [<time tracked>, ...]  # Time tracked per task in same order as subtasks.
                 ],
         first_week_id: <int>,  # ID of first week this task appears in.
         subtasks: [<sub tasks>],  # Defines name and ordering of subtasks.
         archived: <boolean>  # Defines whether task is to be displayed.
         }
        ]
task_order = [<tasks>]
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

        if self.filename:
            self.load_from_file()
        else:
            self.raw_data['task_order'] = []
            self.raw_data['tasks'] = []
            self.raw_data['first_date'] = str(datetime.datetime.strptime(str(datetime.date.today()),
                                                                         "%Y-%m-%d"))
            self.raw_data['archived_week_index'] = 0

    @property
    def raw_tasks(self):
        """
        Easy way to access the raw task data.
        :return list: List of raw task dicts
        """
        return self.raw_data['tasks']

    @property
    def task_order(self):
        """
        Easy way to access the raw ordered task list.
        :return list: List of task names.
        """
        return self.raw_data['task_order']

    @property
    def archived_week_index(self):
        """
        Easy way to access the archived week index.
        :return int: Archived week index
        """
        return self.raw_data['archived_week_index']

    def load_from_file(self):
        """
        Load from preconfigured filename. Populates self.raw_data dictionary from the file contents.
        Expects a file in json format, following the structure described at the top of this file.
        :return:
        """
        logging.debug("Loading datastore from file: %s" % self.filename)
        with open(self.filename, 'r') as save_file:
            self.raw_data = json.loads(save_file)

    def save_to_file(self):
        """
        Saves to preconfigured filename. Creates json according to format at the top of this file.
        :return:
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
        task_index = self.task_order.find(task_name)
        return self.raw_tasks[task_index]

    def get_archived_list(self):
        """
        Produces a list of all of the archived tasks.
        :return list: List of all the archived task names.
        """
        archive_list = []
        for task_name in self.task_order:
            if self.get_raw_task(task_name)['archived']:
                archive_list.append(task_name)

        return archive_list

    def get_first_date(self):
        """
        Returns the date of the first week as a datetime.datetime object.
        :return datetime.datetime: Date of the first week
        """
        return datetime.datetime.strptime(self.raw_data['first_date'], "%Y-%m-%d %M:%S:%f")

    def get_highest_week_id(self):
        """
        Returns the week with the highest ID. This tells us how many weeks exist.
        :return int: Highest stored week index.
        """
        highest_index = 0
        for _task in self.raw_tasks:
            last_task_index = _task.first_week_id + len(_task.weeks)
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

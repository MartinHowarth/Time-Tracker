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
}
"""


class DataStore(object):
    def __init__(self, filename=None):
        self.filename = filename
        self.raw_data = {}

        if self.filename:
            self.load_from_file()
        else:
            self.raw_data['task_order'] = []
            self.raw_data['tasks'] = []
            self.raw_data['first_date'] = str(datetime.datetime.strptime(str(datetime.date.today()),
                                                                         "%Y-%m-%d"))

    @property
    def raw_tasks(self):
        return self.raw_data['tasks']

    @property
    def task_order(self):
        return self.raw_data['task_order']

    def load_from_file(self):
        logging.debug("Loading datastore from file: %s" % self.filename)
        with open(self.filename, 'r') as save_file:
            self.raw_data = json.loads(save_file)

    def save_to_file(self):
        logging.debug("Saving datastore to file: %s" % self.filename)
        json_to_save = json.dumps(self.raw_data)
        with open(self.filename, 'w') as save_file:
            save_file.writelines(json_to_save)

    def get_raw_task(self, task_name):
        task_index = self.task_order.find(task_name)
        return self.raw_tasks[task_index]

    def get_archived_list(self):
        archive_list = []
        for task_name in self.task_order:
            if self.get_raw_task(task_name)['archived']:
                archive_list.append(task_name)

        return archive_list

    def get_first_date(self):
        return datetime.datetime.strptime(self.raw_data['first_date'], "%Y-%m-%d %M:%S:%f")

    def get_highest_week_id(self):
        highest_index = 0
        for _task in self.raw_tasks:
            last_task_index = _task.first_week_id + len(_task.weeks)
            if last_task_index > highest_index:
                highest_index = last_task_index

        return highest_index

    def create_task(self, task_name):
        # Get the raw task dict
        raw_task = self.get_raw_task(task_name)

        # Pluck out required information
        first_week_id = raw_task['first_week_id']
        subtasks = raw_task['subtasks']
        weeks = raw_task['weeks']
        archived = raw_task['archived']

        # Create the new task and store it.
        return task.Task(task_name, first_week_id, subtasks, weeks, archived)

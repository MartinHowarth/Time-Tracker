import Tkinter
from datastore import DataStore
import task
import display
import datetime
import logging
import os

logging.basicConfig(level=logging.DEBUG)

save_folder = "C:/blah/blah"


class Tracker(object):
    first_task_index = 1
    first_week_index = 2

    def __init__(self, tkinter_root, _datastore):
        self.parent = tkinter_root
        self.datastore = _datastore

        self.tasks = {}
        self.unfiltered_task_order = self.datastore.task_order
        self.archived_tasks = self.datastore.get_archived_list()
        # remove archived tasks from the order so they don't get shown
        self.task_order = [_task for _task in self.unfiltered_task_order if _task not in self.archived_tasks]
        self.first_date = self.datastore.get_first_date()

        self.tracker_display = display.TrackerDisplay(self.parent, self)

        self.week_index = self.first_week_index  # Offset column for first week to allow for task labels etc.
        for week_id in range(self.datastore.get_highest_week_id()):
            self.add_week(init_setup=True)

        self.task_index = self.first_task_index  # Offset row for first task to allow for headers, etc.
        for task_name in self.task_order:
            self.create_task_from_store(task_name)

    def get_week_name(self, week_id):
        new_date = self.first_date + datetime.timedelta(days=7*(week_id - self.first_week_index))
        new_date = new_date.strftime("%d %b")  # Prints in format like "14 Sep"
        return str(new_date)

    def create_task_from_store(self, task_name):
        _task = self.datastore.create_task(task_name)
        self._new_task(_task)

    def create_new_task(self, task_name):
        # Create task with week slot for latest existing week.
        # That week has index self.week_index - 1
        if self.week_index <= self.first_week_index:
            logging.warning("Add at least one week before creating tasks. Aborting task creation.")
            return

        _task = task.Task(task_name, self.week_index - 1)
        self._new_task(_task)

    def _new_task(self, _task):
        name = _task.task_name
        if name in self.tasks.keys():
            logging.warning("Task with name %s already exists, aborting creation." % name)
            return

        self.task_order.append(name)
        self.tasks[name] = _task
        self.add_task_display(_task)

    def add_task_display(self, _task):
        self.tracker_display.add_task_display(_task,
                                              self.task_index)
        self.task_index += 1

    def add_week(self, init_setup=False):
        """
        Add a new week to all tasks, unless the task is being created from storage.
        Also add new week label.
        :param bool init_setup: Whether the week is being created from storage or not.
            If it's a new week, then we add a new week slot to each task.
        :return:
        """
        self.tracker_display.add_week_label(self.get_week_name(self.week_index),
                                            self.week_index)

        if not init_setup:
            for _task in self.tasks.itervalues():
                _task.add_week(self.week_index)
                self.tracker_display.add_week_slot(_task, _task.weeks[-1])

        self.week_index += 1

    def update_all(self, _=None):
        self.tracker_display.update_all_task_labels()
        self.update_week_labels()

    def update_week_labels(self):
        for week_index, week_label in enumerate(self.tracker_display.week_labels):
            counter = 0
            for _task in self.tasks.itervalues():
                counter += _task.get_time_for_week(week_index + self.first_week_index)

            week_label.update_to_value(counter)


if False:#os.listdir(save_folder):
    filename = save_folder + "newest file in folder"
    datastore = DataStore(filename)
else:  # First time use
    datastore = DataStore()



root = Tkinter.Tk()
root.wm_title("Time Tracker")
root.resizable()


tracker = Tracker(root, datastore)


root.mainloop()



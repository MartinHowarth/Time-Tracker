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
    def __init__(self, tkinter_root, _datastore):
        self.parent = tkinter_root
        self.datastore = _datastore

        self.tasks = {}
        self.task_order = self.datastore.task_order
        self.first_date = self.datastore.get_first_date()
        self.archived_week_index = self.datastore.archived_week_index

        self.week_index = 0
        for week_id in range(self.datastore.get_highest_week_id()):
            self.add_week(init_setup=True)

        self.task_index = 0
        for task_name in self.task_order:
            self.create_task_from_store(task_name)

        self.tracker_display = display.TrackerDisplay(self.parent, self)

    def get_week_name(self, week_id):
        new_date = self.first_date + datetime.timedelta(days=7*week_id)
        new_date = new_date.strftime("%d %b")  # Prints in format like "14 Sep"
        return str(new_date)

    def create_task_from_store(self, task_name):
        _task = self.datastore.create_task(task_name)
        self._new_task(_task)

    def create_new_task(self, task_name):
        # Create task with week slot for latest existing week.
        # That week has index self.week_index - 1
        if self.week_index == 0:
            logging.warning("Add at least one week before creating tasks. Aborting task creation.")
            return

        _task = task.Task(task_name, self.week_index - 1)
        self._new_task(_task)

    def get_task_and_index(self, task_name):
        return self.tasks[task_name], self.task_order.index(task_name)

    def _new_task(self, _task):
        name = _task.task_name
        if name in self.tasks.keys():
            logging.warning("Task with name %s already exists, aborting creation." % name)
            return

        self.task_order.append(name)
        self.tasks[name] = _task

    def add_week(self, init_setup=False):
        """
        Add a new week to all tasks, unless the task is being created from storage.
        Also add new week label.
        :param bool init_setup: Whether the week is being created from storage or not.
            If it's a new week, then we add a new week slot to each task.
        :return:
        """
        if not init_setup:
            for _task in self.tasks.itervalues():
                _task.add_week(self.week_index)

        self.week_index += 1

    def update(self):
        """
        Complete redraw the display. Does not recreate the Tkinter root.
        :return:
        """
        self.tracker_display.destroy()
        self.tracker_display = display.TrackerDisplay(self.parent, self)



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



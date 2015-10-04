import Tkinter
from datastore import DataStore
import task
import display
import datetime
import logging
import os

# logging.basicConfig(level=logging.DEBUG)

save_folder = "C:/blah/blah"


class Tracker(object):
    """
    :type first_date: datetime.datetime
    :type _archived_week_index: int
    """
    def __init__(self, tkinter_root, _datastore):
        """
        :param Tkinter.Tk tkinter_root: Root display object.
        :param datastore.DataStore _datastore: Datastore object.
        :return:
        """
        self.parent = tkinter_root
        self.datastore = _datastore

        self.tasks = {}  # {task_name: task.Task}
        self.task_order = []  # [task_names]
        self.first_date = None
        self._archived_week_index = None

        self.week_index = 0

        self.load()

        self.tracker_display = display.TrackerDisplay(self.parent, self)

    @property
    def archived_week_index(self):
        return self._archived_week_index

    @archived_week_index.setter
    def archived_week_index(self, value):
        if value < 0:
            return
        if value > self.week_index:
            return
        self._archived_week_index = value

    def _re_initialise(self):
        """
        Restore variables to their default values. This allows clean loading of saved data.
        """
        self.tasks = {}  # {task_name: task.Task}
        self.task_order = []  # [task_names]
        self.first_date = None
        self._archived_week_index = None

        self.week_index = 0

    def _get_details_from_datastore(self):
        # self.task_order = self.datastore.task_order
        self.first_date = self.datastore.first_date
        self._archived_week_index = self.datastore.archived_week_index
        for task_name in self.datastore.task_order:
            _task = self.datastore.create_task(task_name)
            self._handle_new_task(_task)

    def get_week_name(self, week_id):
        new_date = self.first_date + datetime.timedelta(days=7*week_id)
        new_date = new_date.strftime("%d %b")  # Prints in format like "14 Sep"
        return str(new_date)

    def create_new_task(self, task_name):
        # Create task with week slot for latest existing week.
        # That week has index self.week_index - 1
        if self.week_index == 0:
            logging.warning("Add at least one week before creating tasks. Aborting task creation.")
            return

        _task = task.Task(task_name, self.week_index - 1)
        self._handle_new_task(_task)

    def get_task_and_index(self, task_name):
        return self.tasks[task_name], self.task_order.index(task_name)

    def get_archived_task_list(self):
        """
        Gets a list of all tasks that are archived.
        :return list[task.Task]: List of task objects that are archived.
        """
        archived_tasks = []
        for _task in self.tasks.itervalues():
            if _task.archived:
                archived_tasks.append(_task)

        return archived_tasks

    def check_task_name_validity(self, name):
        if name in self.tasks.keys():
            logging.warning("Task with name %s already exists" % name)
            return False
        return True

    def _handle_new_task(self, _task):
        """
        Checks whether a new task is valid (unique name), and then adds it to the list of tasks that exist.
        :param task.Task _task: Task that has just been created.
        """
        name = _task.task_name
        if self.check_task_name_validity(name):
            self.task_order.append(name)
            self.tasks[name] = _task
        else:
            logging.debug("Task name already exists, aborting creation.")

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

    def save(self):
        """
        Triggers the associated datastore to save all data about this Tracker object.
        """
        self.datastore.save_tracker(self)

    def load(self):
        """
        Triggers loading of stored details from the associated datastore.
        """
        self._re_initialise()

        # Add weeks until we reach the highest recorded week index.
        self.week_index = 0
        for week_id in range(self.datastore.get_highest_week_id()):
            self.add_week(init_setup=True)

        self._get_details_from_datastore()



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



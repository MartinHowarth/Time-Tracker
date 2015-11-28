import Tkinter
import datetime
import logging

from datastore import DataStore
import task
from display import tracker_display


# logging.basicConfig(level=logging.DEBUG)

save_folder = ""
filename = "testing.trk"


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

        self.tracker_display = tracker_display.TrackerDisplay(self.parent, self)

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
        logging.debug("Tracker: Reinitialising")
        self.tasks = {}  # {task_name: task.Task}
        self.task_order = []  # [task_names]
        self.first_date = None
        self._archived_week_index = None

        self.week_index = 0

    def _get_details_from_datastore(self):
        """
        Populate this tracker with details from the datastore.
        """
        logging.debug("Tracker: Reading from datastore")
        self.first_date = self.datastore.first_date
        self._archived_week_index = self.datastore.archived_week_index
        for task_name in self.datastore.task_order:
            _task = self.datastore.create_task(task_name)
            self._handle_new_task(_task)

    def get_week_name(self, week_id):
        """
        Generates a string form of a week from a given week ID.
        :param int week_id: ID of the week. Number of weeks since the tracker was first created.
        :return str: <creation date> + week_id*7 days in human readable form.
        """
        new_date = self.first_date + datetime.timedelta(days=7*week_id)
        new_date = new_date.strftime("%d %b")  # Prints in format like "14 Sep"
        return str(new_date)

    def create_new_task(self, task_name):
        """
        Create a new task. Will be created with a week slot for the latest week.
        :param str task_name: Name of the new task.
        """
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
        """
        Check whether a task name is already in use.
        :param str name: Name to check for existence
        :return bool: True if a task with given name already exists. False otherwise.
        """
        if name in self.tasks.keys():
            logging.warning("Task with name %s already exists" % name)
            return False
        return True

    def rename_task(self, _task, new_name):
        """
        Rename a given task
        :param task.Task _task: Task to be renamed
        :param str new_name: New name of the task
        """
        old_name = _task.task_name
        _task.task_name = new_name  # Set the new name

        # Change the name in the tasks dict
        del self.tasks[old_name]
        self.tasks[_task.task_name] = _task

        # Change the name in the tasks order list
        index = self.task_order.index(old_name)
        self.task_order[index] = new_name

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
        logging.debug("Tracker: adding week. init_setup: %s" % init_setup)
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
        self.tracker_display = tracker_display.TrackerDisplay(self.parent, self)

    def save(self):
        """
        Triggers the associated datastore to save all data about this Tracker object.
        """
        self.datastore.save_to_file(self)

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


root = Tkinter.Tk()
root.wm_title("Time Tracker")
root.resizable()


datastore = DataStore(save_folder + filename)
tracker = Tracker(root, datastore)


def save_and_exit():
    tracker.save()
    exit()

root.protocol("WM_DELETE_WINDOW", save_and_exit)
root.mainloop()



import Tkinter
import logging


def prompt_for_value(parent, function_to_call, title):
    def prompt():
        window = Tkinter.Toplevel(parent)
        window.wm_title(title)
        entry = Tkinter.Entry(window, width=20)
        entry.pack()
        entry.focus_set()

        def accept(_=None):
            logging.debug("New %s value: %s" % (title, entry.get()))
            function_to_call(entry.get())
            window.destroy()

        Tkinter.Button(window, text="Accept", command=accept).pack()
        window.bind('<Return>', accept)

    return prompt


class TrackerDisplay(Tkinter.Frame):
    def __init__(self, parent, _tracker):
        """

        :param Tkinter.Tk parent: Tkinter root.
        :return:
        """
        self.tracker = _tracker

        self.parent = parent
        Tkinter.Frame.__init__(self, self.parent)

        self.add_task_button = Tkinter.Button(self,
                                              text="+Task",
                                              command=prompt_for_value(self,
                                                                       self.add_task,
                                                                       "Enter task name"))

        self.add_week_button = Tkinter.Button(self,
                                              text="+Week",
                                              command=self.add_week)

        self.task_displays = {}
        self.week_labels = []

        self.parent.bind('<Return>', self.tracker.update_all)

        self.draw()

    def add_task(self, name):
        logging.debug("Add task button pressed with name: %s" % name)
        self.tracker.create_new_task(name)
        self.draw()

    def add_week(self):
        logging.debug("Add week button pressed.")
        self.tracker.add_week()
        self.draw()

    def add_task_display(self, _task, task_index):
        self.task_displays[_task] = TaskDisplay(self, _task, task_index)

    def add_week_label(self, week_name, week_index):
        self.week_labels.append(WeekLabel(self, week_name, week_index))

    def add_week_slot(self, _task, week):
        self.task_displays[_task].add_week(week)

    def draw(self):
        self.grid(row=1, column=0)
        self.add_task_button.grid(row=0, column=0, sticky=Tkinter.W)
        self.add_week_button.grid(row=0, column=1, sticky=Tkinter.W)

    def update_all_task_labels(self):
        for task_display in self.task_displays.itervalues():
            task_display.update_all()


class TaskDisplay(Tkinter.Frame):
    def __init__(self, parent, _task, row_id):
        """

        :param TrackerDisplay parent: Tkinter Frame within which this frame resides.
        :param task.Task _task: Datastore that this class will draw.
        :return:
        """
        logging.debug("Creating display for task %s" % str(_task))

        self.task = _task

        self.parent = parent
        self.row_id = row_id
        Tkinter.Frame.__init__(self,
                               self.parent,
                               borderwidth=2,
                               relief=Tkinter.GROOVE)

        # Create a label with a variable text field so that we can update it later.
        self._label_text = Tkinter.StringVar()
        self.label = Tkinter.Label(self,
                                   textvariable=self._label_text)

        self.update_counter()

        # Create a button that prompts for a name, then creates a new subtask.
        self.add_new_subtask_button = Tkinter.Button(self,
                                                     text="+",
                                                     command=prompt_for_value(self.parent,
                                                                              self.add_subtask,
                                                                              "Enter subtask name"))

        # Create a label for each pre-existing subtask.
        self.subtask_labels = []
        for subtask in self.task.subtasks:
            self.add_subtask_label(subtask)

        self.week_displays = []
        for _week in self.task.weeks:
            logging.debug(self.task.weeks)
            self.add_week(_week)
        logging.debug(self.week_displays)

        self.draw()

    def add_subtask(self, name):
        """
        Intended to be called when the "new subtask" button is pressed.
        Creates a new subtask in the task.
        Also creates a label for the new subtask.
        :param str name: Subtask name.
        :return:
        """
        if name in self.task.subtasks:
            logging.info("A subtask with name %s already exists. Creation aborted." % name)
            return

        self.task.add_subtask(name)
        self.add_subtask_label(name)
        self.week_displays[-1].add_subtask()  # Add entry in latest week for new subtask.

    def add_subtask_label(self, name):
        """
        Add a label to describe the subtask.
        :param str name: Subtask name
        :return:
        """
        self.subtask_labels.append(SubTaskLabel(self, name))

    def add_week(self, _week):
        self.week_displays.append(WeekDisplay(self.parent, _week, self.row_id, _week.index))

    def draw(self):
        self.grid(row=self.row_id, sticky=Tkinter.W)  # Draw task details onto main grid in correct row.
        self.label.grid(row=0, sticky=Tkinter.W)  # Draw task label in sub-grid that belongs to this task.
        self.add_new_subtask_button.grid(row=0, column=1, sticky=Tkinter.E)  # Draw new subtask button next to label.

    def update_all(self):
        logging.debug("Updating all week slots, task labels and subtask labels.")
        for week_display in self.week_displays:
            week_display.update_values()

        self.update_counter()
        for subtask_label in self.subtask_labels:
            subtask_label.update_counter()

    def update_counter(self):
        self._update_to_value(self.task.get_total_time())

    def _update_to_value(self, value):
        """
        Update the label to keep the same name, but with a new value.
        :param float value: Value to display.
        :return:
        """
        self._label_text.set("%s: %d" % (self.task.task_name, value))


class SubTaskLabel(Tkinter.Label):
    def __init__(self, parent_task_display, name):
        self.parent = parent_task_display
        self.name = name

        # Create the label with a variable text field so we can change it later.
        self.text = Tkinter.StringVar()
        Tkinter.Label.__init__(self,
                               parent_task_display,
                               textvariable=self.text)

        # Initialise label with default value.
        self.update_counter()

        self.grid(sticky=Tkinter.W)

    def update_counter(self):
        logging.debug("Updating counter for subtask %s" % self.name)
        self._update_to_value(self.parent.task.get_time_for_subtask(self.name))

    def _update_to_value(self, value):
        """
        Update the label to keep the same name, but with a new value.
        :param float value: Value to display.
        :return:
        """
        self.text.set(self.name + ": " + str(value))


class WeekDisplay(Tkinter.Frame):
    def __init__(self, parent, _week, row_index, column_index):
        """
        Displays a single task/week grid space.
        Has an entry per subtask (and one for the general task).
        :param TrackerDisplay parent: Tkinter Frame within which this frame resides.
        :param weekslot.WeekSlot _week: Datastore that this class will draw.
        :return:
        """
        logging.debug("Creating display for week %s" % str(_week))

        self.parent = parent
        Tkinter.Frame.__init__(self,
                               self.parent)

        self.row_index = row_index
        self.column_index = column_index

        self.week = _week
        self.entries = []

        # Add a subtask text entry box for each value in the week.
        for time in self.week.time_tracked:
            self.add_subtask(time)

        self.draw()

    def add_subtask(self, init_time=0):
        """
        Creates a new entry field for the new subtask.
        :param float init_time: Initial time for the entry to be filled with.
        :return:
        """
        new_entry = Tkinter.Entry(self, width=5)
        new_entry.insert(0, str(init_time))  # insert the supplied value at position 0.
        self.entries.append(new_entry)
        self.draw()

    def draw(self):
        self.grid(row=self.row_index, column=self.column_index, sticky=Tkinter.N)

        for index, entry in enumerate(self.entries):
            entry.grid(row=index)

    def update_values(self):
        """
        Put the values in the field entries into the week object.
        :return:
        """
        logging.debug("Updating values for week slot in row %d, column %d" % (self.row_index, self.column_index))
        values = []
        for entry in self.entries:
            values.append(float(entry.get()))
        self.week.update_values(values)


class WeekLabel(Tkinter.Label):
    def __init__(self, parent, date_string, column_index):
        """

        :param Tkinter.Frame parent: Tkinter Frame within which this frame resides.
        :param str date_string: Date in string format
        :param int column_index: Grid index to draw this label.
        :return:
        """
        logging.debug("Creating Label for week %s" % str(date_string))

        # Create the label with a variable text field so we can change it later.
        self.text = Tkinter.StringVar()
        Tkinter.Label.__init__(self, parent, textvariable=self.text)

        self.date_string = date_string
        self.column_index = column_index

        # Set to a default value of 0
        self.update_to_value(0)

        self.draw()

    def update_to_value(self, value):
        """
        Update the label to keep the same name, but with a new value.
        :param float value: Value to display.
        :return:
        """
        logging.debug("Updating week label %s to value %d" % (self.date_string, value))
        self.text.set("%s\n%d" % (self.date_string, value))

    def draw(self):
        self.grid(row=0, column=self.column_index)


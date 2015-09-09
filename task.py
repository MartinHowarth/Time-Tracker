import Tkinter
import timeslot
from collections import defaultdict
import logging


class Task(Tkinter.Frame):
    """
    Single task. May have sub tasks.
    Receives one entry per week to track general time spent on a given task.
    """
    _task_id_counter = 1

    def __init__(self, top_level_frame, name):
        """

        :param Tracker top_level_frame: Main tracker object. Also a Tkinter
            Frame. This is the highest level frame we put things in.
        :param str name: Task name.
        :return:
        """
        logging.debug("Creating Task %s" % name)
        Tkinter.Frame.__init__(self,
                               top_level_frame,
                               borderwidth=2,
                               relief=Tkinter.GROOVE)
        self.name = name
        self.parent = top_level_frame
        self.task_id = Task._task_id_counter
        Task._task_id_counter += 1

        self.text = Tkinter.StringVar()
        self.label = Tkinter.Label(self,
                                   textvariable=self.text)
        self.update_to_value(0)

        self.subtasks = []

        self.add_subtask_button = Tkinter.Button(self,
                                                 text="+",
                                                 command=self.add_subtask)

        self.label.grid(row=0, sticky=Tkinter.W)
        self.grid(row=self.task_id, sticky=Tkinter.W)
        self.add_subtask_button.grid(row=0, column=1, sticky=Tkinter.E)

        self.week_slots = {}

    def add_subtask(self, name=None):
        """
        Adds a subtask. Prompts for name is one is not supplied.
        :param str name: Name of sub task.
        :return:
        """
        if name is None:
            window = Tkinter.Toplevel(self.parent)
            window.wm_title("Enter sub task name")
            entry = Tkinter.Entry(window, width=20)
            entry.pack()

            def accept():
                self.add_subtask(entry.get())
                window.destroy()

            Tkinter.Button(window, text="Accept", command=accept).pack()
        else:
            logging.info("New subtask added: " + name)
            new_subtask = SubTask(self, name)
            self.subtasks.append(new_subtask)
            self.week_slots[self.parent.week_index_counter].add_subtask_time()

    def add_week(self):
        """
        Adds a week to this task. This creates a timeslot in the added week for
        both the general task and each sub task.
        :return:
        """
        logging.debug("Adding week to %s" % self)
        column = self.parent.week_index_counter
        self.week_slots[column] = timeslot.TaskTime(self.parent,
                                                    self.task_id,
                                                    column)
        for _ in self.subtasks:
            self.week_slots[column].add_subtask_time()

    def get_value_in_week(self, column):
        """
        Sums the total time tracked in a given week for this task and all
        sub tasks.
        :param int column: Index of week.
        :return float: Sum of time spent in a given week on this task.
        """
        if column in self.week_slots:
            return self.week_slots[column].get_task_time_total()
        else:
            return 0

    def update_times(self):
        """
        Triggers updating of the labels with the time spent in each task and
        sub task.
        :return:
        """
        counter = defaultdict(int)
        total_count = 0
        for week in self.week_slots.itervalues():
            for row, sub_task_time in week.subtask_times.iteritems():
                counter[row] += sub_task_time.get_task_time()
                total_count += sub_task_time.get_task_time()

        for row, value in counter.iteritems():
            if row == 0:
                self.update_to_value(value)
            else:
                self.subtasks[row-1].update_to_value(value)

        self.update_to_value(total_count)

    def update_to_value(self, value):
        """
        Update the label of this task.
        :param float value: Time spent on this task in total (across all weeks)
        :return:
        """
        self.text.set(self.name + ": " + str(value))

    def __str__(self):
        return self.name


class SubTask(Tkinter.Label):
    """
    A sub task under a task. Can track time against sub tasks independently.
    """
    def __init__(self, parent_task, name):
        self.text = Tkinter.StringVar()
        self.parent = parent_task
        self.name = name

        Tkinter.Label.__init__(self,
                               parent_task,
                               textvariable=self.text)

        self.update_to_value(0)

        self.grid(sticky=Tkinter.W)

    def update_to_value(self, value):
        self.text.set(self.name + ": " + str(value))
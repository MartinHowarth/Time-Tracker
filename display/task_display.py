import Tkinter
import logging
import subtask_display
import week_display
from misc_display_functions import prompt_for_value, ROW_OFFSET


class TaskDisplay(Tkinter.Frame):
    TOTAL_COLUMN_OFFSET = 2
    SUBTASK_ROW_OFFSET = 2

    def __init__(self, parent, _task, row_id):
        """

        :param TrackerDisplay parent: Tkinter Frame within which this frame resides.
        :param task.Task _task: Datastore that this class will draw.
        :return:
        """
        logging.debug("Creating display for task %s" % _task)

        self.task = _task

        if self.task.archived:
            logging.debug("Aborting display for task %s as it is archived." % _task)
            return

        self.parent = parent
        self.row_id = row_id
        Tkinter.Frame.__init__(self,
                               self.parent,
                               borderwidth=2,
                               relief=Tkinter.GROOVE)

        # Create a button which can be clicked to change the task name
        self.task_name = Tkinter.Button(self,
                                        text=self.task.task_name,
                                        command=prompt_for_value(self, self.set_name, "Enter new task name"))

        # Create a button that prompts for a name, then creates a new subtask.
        self.add_new_subtask_button = Tkinter.Button(self,
                                                     text="+Subtask",
                                                     command=prompt_for_value(self.parent,
                                                                              self.add_subtask,
                                                                              "Enter subtask name"))
        # Create a button that archives this task when pressed.
        self.archive_task_button = Tkinter.Button(self,
                                                  text="Hide",
                                                  command=self.archive_self)

        # Create the headers for the total, estimate and remaining columns
        self.spent_header = Tkinter.Label(self, text="Spent")
        self.estimate_header = Tkinter.Label(self, text="Estimate")
        self.remaining_header = Tkinter.Label(self, text="Remaining")

        # Create the labels/entries for the total, estimate and remaining for the entire task.
        total_spent = self.task.get_total_time_spent()
        self.spent_value = Tkinter.Label(self, text=str(total_spent))
        self.estimate_entry = Tkinter.Entry(self, width=5)
        self.estimate_entry.insert(0, self.task.estimate)
        self.remaining_value = Tkinter.Label(self, text=str(self.task.estimate - total_spent))

        # Create a label for each subtask.
        self.subtask_displays = []
        for subtask in self.task.subtasks:
            self.add_subtask_display(subtask)

        # Create a set of entries (a week display) for each week this task exists for
        self.week_displays = []
        for _week in self.task.weeks:
            self.add_week(_week)

        self.draw()

    def set_name(self, name):
        if self.parent.tracker.check_task_name_validity(name):
            self.parent.tracker.rename_task(self.task, name)
            self.parent.update()
        else:
            logging.debug("Task name already exists, abandoning rename.")

    def add_subtask(self, name):
        """
        Intended to be called when the "new subtask" button is pressed.
        Creates a new subtask in the task.
        Also creates a label for the new subtask.
        :param str name: Subtask name.
        :return:
        """
        if self.task.check_subtask_name_validity(name):

            self.task.add_subtask(name)
            self.parent.update()

    def add_subtask_display(self, subtask):
        """
        Add a label to describe the subtask.
        :param subtask.Subtask subtask: Subtask object.
        :return:
        """
        self.subtask_displays.append(subtask_display.SubTaskDisplay(self, subtask))

    def add_week(self, _week):
        self.week_displays.append(week_display.WeekDisplay(self.parent, _week, self.row_id, _week.index))

    def archive_self(self):
        self.task.archived = True
        self.parent.update()

    def draw(self):
        # Draw task details onto main grid in correct row based on defined task order.
        self.grid(row=self.row_id + ROW_OFFSET, sticky=Tkinter.W)
        # Draw task label in sub-grid that belongs to this task.
        self.task_name.grid(row=1, sticky=Tkinter.W)
        # Draw add subtask button next to label.
        self.add_new_subtask_button.grid(row=0, column=0)
        # Draw archive button next to add subtask button
        self.archive_task_button.grid(row=0, column=1)

        self.estimate_header.grid(row=0, column=self.TOTAL_COLUMN_OFFSET)
        self.spent_header.grid(row=0, column=self.TOTAL_COLUMN_OFFSET + 1)
        self.remaining_header.grid(row=0, column=self.TOTAL_COLUMN_OFFSET + 2)

        self.estimate_entry.grid(row=1, column=self.TOTAL_COLUMN_OFFSET)
        self.spent_value.grid(row=1, column=self.TOTAL_COLUMN_OFFSET + 1)
        self.remaining_value.grid(row=1, column=self.TOTAL_COLUMN_OFFSET + 2)

        for row, _subtask in enumerate(self.subtask_displays):
            row += self.SUBTASK_ROW_OFFSET
            _subtask.draw(row, self.TOTAL_COLUMN_OFFSET)

    def gather_input(self):
        if not self.task.archived:
            logging.debug("Gathering input from entries.")
            for _week_display in self.week_displays:
                _week_display.update_values()

            try:
                float_value = float(self.estimate_entry.get())
            except ValueError:
                float_value = 0.0
            self.task.estimate = float_value

            for _subtask_display in self.subtask_displays:
                _subtask_display.gather_input()

        # Archive the tasks if it has been flagged for archiving
        if self.task.archive_after_update:
            self.task.archived = False
            self.task.archive_after_update = False

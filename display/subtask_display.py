import Tkinter
import logging
from misc_display_functions import prompt_for_value


class SubTaskDisplay(object):
    def __init__(self, parent, subtask):
        self.subtask = subtask
        self.name_button = SubTaskButton(parent, self.subtask)

        total_spent = parent.task.get_time_for_subtask(self.subtask)
        self.spent_label = Tkinter.Label(parent, text=str(total_spent))
        self.estimate_entry = Tkinter.Entry(parent, width=5)
        self.estimate_entry.insert(0, self.subtask.estimate)
        self.remaining_label = Tkinter.Label(parent, text=str(self.subtask.estimate - total_spent))

    def gather_input(self):
        try:
            float_value = float(self.estimate_entry.get())
        except ValueError:
            float_value = 0.0
        self.subtask.estimate = float_value

    def draw(self, row, column_offset):
        self.name_button.grid(row=row, sticky=Tkinter.W, padx=10)
        self.estimate_entry.grid(row=row, column=column_offset)
        self.spent_label.grid(row=row, column=column_offset + 1)
        self.remaining_label.grid(row=row, column=column_offset + 2)


class SubTaskButton(Tkinter.Button):
    def __init__(self, parent_task_display, subtask):
        """
        :param TaskDisplay parent_task_display: Task display object that owns this subtask
        :param subtask.Subtask subtask: subtask object
        :return:
        """
        self.parent = parent_task_display
        self.subtask = subtask

        # Create a button whose action is to rename the subtask
        Tkinter.Button.__init__(self,
                                parent_task_display,
                                text=self.subtask.name,
                                command=prompt_for_value(self, self.set_name, "Enter new subtask name"))

    def set_name(self, name):
        """
        Change the name of this subtask.
        :param str name: New name for this subtask.
        :return:
        """
        self.parent.task.rename_subtask(self.subtask, name)
        self.parent.parent.update()

import Tkinter
import logging
from misc_display_functions import prompt_for_value


class SubTaskDisplay(object):
    def __init__(self, parent, name):
        self.name_label = SubTaskLabel(parent, name)

        total = parent.task.get_time_for_subtask(name)
        estimate = 0
        gain = 0
        self.total_label = Tkinter.Label(parent, text=str(total))
        self.estimate_entry = Tkinter.Entry(parent, width=5)
        self.gain_label = Tkinter.Label(parent, text=str(gain))

    def draw(self, row, column_offset):
        self.name_label.grid(row=row, sticky=Tkinter.W)
        self.total_label.grid(row=row, column=column_offset)
        self.estimate_entry.grid(row=row, column=column_offset + 1)
        self.gain_label.grid(row=row, column=column_offset + 2)


class SubTaskLabel(Tkinter.Button):
    def __init__(self, parent_task_display, name):
        """
        :param TaskDisplay parent_task_display: Task display object that owns this subtask
        :param str name: subtask name
        :return:
        """
        self.parent = parent_task_display
        self.name = name

        # Create the label with a variable text field so we can change it later.
        # self.text = Tkinter.StringVar()
        Tkinter.Button.__init__(self,
                                parent_task_display,
                                text=self.name,
                                command=prompt_for_value(self, self.set_name, "Enter new subtask name"))

        # Initialise label with default value.
        # self.update_counter()


    def set_name(self, name):
        """
        Change the name of this subtask.
        :param str name: New name for this subtask.
        :return:
        """
        self.parent.task.rename_subtask(self.name, name)
        self.parent.parent.update()

    # def update_counter(self):
    #     """
    #     Update the summation of time tracked against this task.
    #     :return:
    #     """
    #     logging.debug("Updating counter for subtask %s" % self.name)
    #     self._update_to_value(self.parent.task.get_time_for_subtask(self.name))
    #
    # def _update_to_value(self, value):
    #     """
    #     Update the label to keep the same name, but with a new value.
    #     :param float value: Value to display.
    #     :return:
    #     """
    #     self.text.set(self.name + ": " + str(value))

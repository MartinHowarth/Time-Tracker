import Tkinter
import logging


class ArchiveDisplay(Tkinter.Toplevel):
    def __init__(self, parent):
        """
        :param TrackerDisplay parent:
        """
        Tkinter.Toplevel.__init__(self, parent)
        self.wm_title("Click tasks to restore them")

        self.parent = parent

        self.hide_self_button = Tkinter.Button(self,
                                               text="Close",
                                               command=self.parent.hide_archive)

        self.description_label = Tkinter.Label(self, text="Click tasks to restore them.")

        self.archived_task_list = self.parent.tracker.get_archived_task_list()

        self.restore_task_buttons = {}

        for _task in self.archived_task_list:
            self.restore_task_buttons[_task] = Tkinter.Button(self,
                                                              text=str(_task),
                                                              command=self.unarchive_task(_task))

        self.draw()

    def unarchive_task(self, _task):
        """
        Trigger this task to become unarchived on the next update of the display.
        :param task.Task _task: Task to un-archive.
        """
        def do_the_work():
            # Set just unarchived so that we don't try and read the entry values from this task before we redraw.
            _task.archive_after_update = True
            self.restore_task_buttons[_task].destroy()
            self.parent.update()
        return do_the_work

    def draw(self):
        self.description_label.pack()
        for button in self.restore_task_buttons.itervalues():
            button.pack()
        self.hide_self_button.pack()


import Tkinter
import logging
from misc_display_functions import ROW_OFFSET, COLUMN_OFFSET


class WeekDisplay(Tkinter.Frame):
    ROW_HEIGHT = 24
    ENTRY_ROW_OFFSET = 2

    def __init__(self, parent, _week, row_index, column_index):
        """
        Displays a single task/week grid space.
        Has an entry per subtask (and one for the general task).
        :param TrackerDisplay parent: Tkinter Frame within which this frame resides.
        :param weekslot.WeekSlot _week: Datastore that this class will draw.
        """
        logging.debug("Creating display for week %s" % str(_week))

        self.parent = parent
        Tkinter.Frame.__init__(self,
                               self.parent)

        for i in range(self.ENTRY_ROW_OFFSET):
            self.rowconfigure(i, minsize=self.ROW_HEIGHT)

        self.row_index = row_index
        self.column_index = column_index

        self.week = _week
        self.entries = []

        # Add a subtask text entry box for each value in the week.
        for time in self.week.time_tracked:
            self.add_subtask(time)

        # Only display if this week is not archived.
        if self.column_index >= self.parent.tracker.archived_week_index:
            self.draw()
        else:
            logging.debug("Not displaying week slot in column %d because it is archived." % self.column_index)

    def add_subtask(self, init_time):
        """
        Creates a new entry field for the new subtask.
        :param float init_time: Initial time for the entry to be filled with.
        """
        new_entry = Tkinter.Entry(self, width=5)
        if init_time != 0:
            # insert the supplied value into the entry. Leave blank if value is 0
            new_entry.insert(0, str(init_time))
        self.entries.append(new_entry)

    def draw(self):
        """
        Draws this week display object in the correct grid slot of the TrackerDisplay object.
        Also draws the entries for each subtask within this week object.
        """
        self.grid(row=self.row_index + ROW_OFFSET,
                  column=self.column_index + COLUMN_OFFSET,
                  sticky=Tkinter.N)

        for index, entry in enumerate(self.entries):
            entry.grid(row=index + self.ENTRY_ROW_OFFSET, pady=5)

    def update_values(self):
        """
        Gather the values from the displayed entries and put into the week object.
        """
        logging.debug("Updating values for week slot in row %d, column %d" % (self.row_index, self.column_index))
        values = []
        for entry in self.entries:
            # Try convert the string value stored in the entry to a float. If this fails, assume it is 0.
            # Specifically this covers the case where the field is an empty string which signifies 0.
            try:
                float_value = float(entry.get())
            except ValueError:
                float_value = 0.0
            values.append(float_value)
        self.week.update_values(values)


class WeekLabel(Tkinter.Label):
    def __init__(self, parent, date_string, column_index):
        """

        :param TrackerDisplay parent: Tkinter Frame within which this frame resides.
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

        # Only display if this week is not archived.
        if self.column_index >= parent.tracker.archived_week_index:
            self.draw()
        else:
            logging.debug("Not displaying week label in column %d because it is archived." % self.column_index)

    def update_to_value(self, value):
        """
        Update the label to keep the same name, but with a new value.
        :param float value: Value to display.
        :return:
        """
        logging.debug("Updating week label %s to value %.2f" % (self.date_string, value))
        if value == 5:
            self.text.set("%s" % self.date_string)
        else:
            self.text.set("%s\n%.2f" % (self.date_string, value))

    def draw(self):
        """
        Draws this week label in the first row of the correct column of the TrackerDisplay grid.
        :return:
        """
        self.grid(row=0, column=self.column_index + COLUMN_OFFSET)

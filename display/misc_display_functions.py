import Tkinter
import logging


ROW_OFFSET = 2
COLUMN_OFFSET = 2


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

import urwid
import signal

from redial.utils import append_to_config


def question(content):
    return urwid.Pile([urwid.Edit(('I say', content + " "))])


def sigint_handler(signum, frame):
    exit_program()


def exit_program():
    raise urwid.ExitMainLoop()


class ConversationListBox(urwid.ListBox):
    def __init__(self, questions):
        self.answers = []
        body = urwid.SimpleFocusListWalker([question(questions[0])])
        super(ConversationListBox, self).__init__(body)

    def keypress(self, size, key):
        key = super(ConversationListBox, self).keypress(size, key)
        if key != 'enter':
            return key
        answer = self.focus[0].edit_text
        if not answer:
            raise urwid.ExitMainLoop()
        self.answers.append(answer)
        pos = self.focus_position
        # add a new question
        if len(questions) > pos+1:
            self.body.insert(pos + 1, question(questions[pos+1]))
            self.focus_position = pos + 1
        else:
            raise urwid.ExitMainLoop()
        
palette = [('I say', 'default,bold', 'default'), ]
questions = ["Host: ", "hostname(ip): ", "user: ", "port: "]


def init_dialog():
    conversation = ConversationListBox(questions)
    urwid.MainLoop(conversation, palette).run()
    append_to_config(conversation.answers)
    urwid.ExitMainLoop()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, sigint_handler)
    init_dialog()
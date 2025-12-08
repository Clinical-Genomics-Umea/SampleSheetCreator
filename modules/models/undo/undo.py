

class UndoStack:
    def __init__(self):
        self.stack = []
        self.redo_stack = []

    def push(self, command):
        self.stack.append(command)
        self.redo_stack = []

    def pop(self):
        if self.stack:
            command = self.stack.pop()
            self.redo_stack.append(command)
            return command
        return None

    def redo(self):
        if self.redo_stack:
            command = self.redo_stack.pop()
            self.stack.append(command)
            return command
        return None
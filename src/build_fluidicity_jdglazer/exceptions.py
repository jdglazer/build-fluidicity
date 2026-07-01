class BuildException(Exception):

    def __init__(self, message: str = ""):
        self.message = message
        # Forward the message to the parent Exception class
        super().__init__(self.message)
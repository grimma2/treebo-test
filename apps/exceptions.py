class NameOrEmailNotPassed(Exception):
    """Exception raised when attempting to create a user without a name or email.

    Attributes:
        telegram_id -- ID of the user trying to create
        message -- explanation of the error
    """

    def __init__(self, telegram_id, message=None):
        if message is None:
            message = f"Can't create user with id {telegram_id} because name or email is not passed"
        self.telegram_id = telegram_id
        self.message = message
        super().__init__(self.message)

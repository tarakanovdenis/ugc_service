from dataclasses import dataclass


@dataclass
class Messages:
    SUCCESSFULLY_SENDING_WELCOME_NEW_USER_EMAIL = (
        "The Welcome new user message was successfully sent."
    )
    UNSUCCESSFULL_SENDING_WELCOME_NEW_USER_EMAIL = (
        "The Welcome new user message was not sent."
    )

    SUCCESSFULLY_SENDING_RESET_PASSWORD_TOKEN_EMAIL = (
        "The message with reset password token was successfully sent."
    )
    UNSUCCESSFULL_SENDING_RESET_PASSWORD_TOKEN_EMAIL = (
        "The message with reset password token was not sent."
    )


messages = Messages()

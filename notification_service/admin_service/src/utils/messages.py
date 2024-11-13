from dataclasses import dataclass


@dataclass
class Messages:
    MESSAGE_WAS_SENT = (
        "The message was sent successfully."
    )


messages = Messages()

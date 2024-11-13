from abc import ABC, abstractmethod
from uuid import UUID
import ast

from aio_pika.abc import AbstractIncomingMessage


class Notification(ABC):
    @abstractmethod
    def send(self, user_id: UUID, message: AbstractIncomingMessage) -> None:
        '''Send a notification to the user.'''
        pass


class SMSNotification(Notification):
    def send(self, user_id: UUID, message: AbstractIncomingMessage) -> None:
        '''
        Send a SMS-notification to the user using query to the auth service
        to get user phone number information
        '''
        pass


async def send_sms_notification_to_the_user(
    message: dict[str, str],
):
    '''Send SMS-notification using SMSNotification instance.'''

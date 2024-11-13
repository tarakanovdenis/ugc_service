from enum import Enum


class DefaultRoleEnum(Enum):
    ADMIN = "admin"
    SUPER_USER = "super_user"
    PUBLIC_USER = "public_user"
    SUBSCRIBER = "subscriber"

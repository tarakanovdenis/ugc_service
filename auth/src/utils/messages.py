from dataclasses import dataclass


@dataclass
class Messages:
    USER_NOT_FOUND = "User with this ID not found."
    DENIED_ACCESS = "You don't have the appropriate access permissions."
    NOT_AUTHENTICATED = "Not authenticated."

    INVALID_USERNAME_OR_PASSWORD = "Invalid username or password."
    INVALID_TOKEN_ERROR = "Invalid token error."
    INVALID_TOKEN_TYPE = "Invalid token type."

    TOO_MANY_REQUESTS = "Too Many Requests."

    OLD_PASSWORD_IS_INCORRECT = "The old password entered is incorrect."
    PASSWORDS_DO_NOT_MATCH = "The entered passwords don't match."
    PASSWORD_UPDATED = "The password was successfully updated."

    TOKEN_IS_EXPIRED_OR_USER_IS_INACTIVE = (
        "Token has expired or user is inactive."
    )

    CHECK_RESET_PASSWORD_TOKEN_EMAIL = (
        "An email with a link to reset your password has been sent "
        "to your email address."
    )

    SUBSCRIPTION_WAS_ASSIGNED_TO_THE_USER = (
        "The subscription was successfully assigned to the user."
    )
    USER_SUBSCRIPTION_WAS_CANCELLED = (
        "The user's subscription was successfully cancelled."
    )


messages = Messages()

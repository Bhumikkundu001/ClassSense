from classesense.auth.security import (
    hash_password,
    verify_password
)


class AuthService:
    """
    Handles user registration and authentication.
    """


    def __init__(
        self,
        user_repository
    ):

        self.user_repository = (
            user_repository
        )


    def register_user(
        self,
        username,
        password,
        role="faculty"
    ):
        """
        Register a new user.
        """

        existing_user = (
            self.user_repository
            .get_user_by_username(
                username
            )
        )


        if existing_user is not None:

            return {
                "success": False,
                "message": (
                    "Username already exists."
                )
            }


        user_data = {
            "username": username,
            "password_hash": hash_password(
                password
            ),
            "role": role
        }


        self.user_repository.create_user(
            user_data
        )


        return {
            "success": True,
            "message": (
                "User registered successfully."
            )
        }


    def login_user(
        self,
        username,
        password
    ):
        """
        Authenticate a user.
        """

        user = (
            self.user_repository
            .get_user_by_username(
                username
            )
        )


        if user is None:

            return {
                "success": False,
                "message": (
                    "Invalid username or password."
                )
            }


        password_valid = (
            verify_password(
                password,
                user[
                    "password_hash"
                ]
            )
        )


        if not password_valid:

            return {
                "success": False,
                "message": (
                    "Invalid username or password."
                )
            }


        return {
            "success": True,
            "message": (
                "Login successful."
            ),
            "username": user[
                "username"
            ],
            "role": user[
                "role"
            ]
        }
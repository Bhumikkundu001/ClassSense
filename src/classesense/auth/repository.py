import json

from pathlib import Path


class UserRepository:
    """
    Handles persistent storage and retrieval
    of ClassSense user accounts.
    """


    def __init__(
        self,
        storage_file
    ):

        self.storage_file = Path(
            storage_file
        )

        # Create the parent directory if needed
        self.storage_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )


    def get_all_users(
        self
    ):
        """
        Return all registered users.
        """

        if not self.storage_file.exists():

            return []


        try:

            with open(
                self.storage_file,
                "r",
                encoding="utf-8"
            ) as file:

                return json.load(
                    file
                )


        except (
            json.JSONDecodeError,
            OSError
        ):

            return []


    def save_all_users(
        self,
        users
    ):
        """
        Save all users to the storage file.
        """

        with open(
            self.storage_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                users,
                file,
                indent=4
            )


    def get_user_by_username(
        self,
        username
    ):
        """
        Find a user using their username.
        """

        users = self.get_all_users()


        for user in users:

            if (
                user.get(
                    "username"
                ) == username
            ):

                return user


        return None


    def create_user(
        self,
        user_data
    ):
        """
        Save a new user account.
        """

        users = self.get_all_users()


        users.append(
            user_data
        )


        self.save_all_users(
            users
        )


        return user_data
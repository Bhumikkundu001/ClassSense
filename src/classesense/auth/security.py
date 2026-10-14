from passlib.context import CryptContext


# --------------------------------------------------
# PASSWORD HASHING CONFIGURATION
# --------------------------------------------------

password_context = CryptContext(
    schemes=[
        "bcrypt"
    ],
    deprecated="auto"
)


# --------------------------------------------------
# HASH PASSWORD
# --------------------------------------------------

def hash_password(
    password
):
    """
    Convert a plain password into
    a secure hashed password.
    """

    return password_context.hash(
        password
    )


# --------------------------------------------------
# VERIFY PASSWORD
# --------------------------------------------------

def verify_password(
    plain_password,
    hashed_password
):
    """
    Check whether the provided password
    matches the stored hashed password.
    """

    return password_context.verify(
        plain_password,
        hashed_password
    )
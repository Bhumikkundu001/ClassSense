from datetime import datetime
from pathlib import Path


# --------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------

# Folder containing this file:
# C:\classsense\src\classesense
PACKAGE_DIR = Path(__file__).resolve().parent

# C:\classsense\src
SRC_DIR = PACKAGE_DIR.parent

# C:\classsense
PROJECT_ROOT = SRC_DIR.parent


# --------------------------------------------------
# DATA DIRECTORIES
# --------------------------------------------------

DATA_DIR = PROJECT_ROOT / "data"

STUDENTS_DIR = DATA_DIR / "students"
REAL_STUDENTS_DIR = DATA_DIR / "students"
CLASSROOM_DIR = DATA_DIR / "classroom"
CLASSROOM_RESULTS_DIR = DATA_DIR / "classroom_results"
def create_session_results_dir():
    """
    Create and return a unique folder for one attendance session.
    """

    timestamp = datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S"
    )

    session_dir = (
        CLASSROOM_RESULTS_DIR /
        f"session_{timestamp}"
    )

    session_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    return session_dir

TEST_DIR = DATA_DIR / "lfw_test"
UNKNOWN_DIR = DATA_DIR / "lfw_unknown"

MULTI_FACE_DIR = DATA_DIR / "multi_face"

MULTI_IMAGE_TEST_DIR = DATA_DIR / "multi_image_test"
MULTI_IMAGE_RESULTS_DIR = DATA_DIR / "multi_image_results"


# --------------------------------------------------
# FACE RECOGNITION SETTINGS
# --------------------------------------------------

# Minimum similarity score required
# to recognize a student.
MATCH_THRESHOLD = 0.40


# InsightFace model configuration
MODEL_NAME = "buffalo_l"

PROVIDERS = [
    "CPUExecutionProvider"
]


# Face detection image size
DETECTION_SIZE = (
    640,
    640
)


# --------------------------------------------------
# OUTPUT SETTINGS
# --------------------------------------------------

# Image file formats supported by
# the ClassSense application.
SUPPORTED_IMAGE_EXTENSIONS = (
    ".jpg",
    ".jpeg",
    ".png"
)
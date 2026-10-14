import cv2
import numpy as np
from pathlib import Path
from insightface.app import FaceAnalysis


# ============================================================
# PATHS
# ============================================================

KNOWN_FOLDER = Path("data/lfw_test")
UNKNOWN_FOLDER = Path("data/lfw_unknown")

OUTPUT_FOLDER = Path("data/multi_face")
OUTPUT_PATH = OUTPUT_FOLDER / "clean_multi_face_test.jpg"


# ============================================================
# LOAD INSIGHTFACE
# ============================================================

print("Loading InsightFace...")

app = FaceAnalysis(
    name="buffalo_l",
    providers=["CPUExecutionProvider"]
)

app.prepare(
    ctx_id=0,
    det_size=(640, 640)
)

print("InsightFace loaded successfully!\n")


# ============================================================
# SELECT IMAGES
# ============================================================

image_paths = [
    KNOWN_FOLDER / "Aaron_Peirsol.jpg",
    KNOWN_FOLDER / "Abdullah.jpg",
    KNOWN_FOLDER / "Abel_Pacheco.jpg",
    UNKNOWN_FOLDER / "Aaron_Sorkin.jpg",
    UNKNOWN_FOLDER / "Abdel_Nasser_Assidi.jpg",
]


# ============================================================
# EXTRACT LARGEST FACE
# ============================================================

def extract_main_face(image_path):

    image = cv2.imread(str(image_path))

    if image is None:
        print(f"Could not read: {image_path}")
        return None

    faces = app.get(image)

    if len(faces) == 0:
        print(f"No face found: {image_path}")
        return None

    # Select the largest detected face
    face = max(
        faces,
        key=lambda f:
        (f.bbox[2] - f.bbox[0]) *
        (f.bbox[3] - f.bbox[1])
    )

    x1, y1, x2, y2 = face.bbox.astype(int)

    # Add some margin around the face
    margin = 25

    x1 = max(0, x1 - margin)
    y1 = max(0, y1 - margin)

    x2 = min(image.shape[1], x2 + margin)
    y2 = min(image.shape[0], y2 + margin)

    face_crop = image[y1:y2, x1:x2]

    if face_crop.size == 0:
        return None

    # Make every face the same size
    face_crop = cv2.resize(
        face_crop,
        (250, 250)
    )

    return face_crop


# ============================================================
# EXTRACT ALL FIVE FACES
# ============================================================

faces = []

for image_path in image_paths:

    print(f"Processing: {image_path.name}")

    face_crop = extract_main_face(image_path)

    if face_crop is not None:

        faces.append(face_crop)

        print("  Main face extracted successfully.")

    else:

        print("  ERROR: Face could not be extracted.")


# ============================================================
# CREATE MULTI-FACE IMAGE
# ============================================================

if len(faces) != 5:

    print(
        f"\nERROR: Expected 5 faces "
        f"but extracted {len(faces)}."
    )

    exit()


# First row: 3 faces
row1 = np.hstack([
    faces[0],
    faces[1],
    faces[2]
])


# Second row: 2 faces + blank space
blank = np.ones(
    (250, 250, 3),
    dtype=np.uint8
) * 255

row2 = np.hstack([
    faces[3],
    faces[4],
    blank
])


# Combine both rows
multi_face_image = np.vstack([
    row1,
    row2
])


# ============================================================
# SAVE
# ============================================================

OUTPUT_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)

cv2.imwrite(
    str(OUTPUT_PATH),
    multi_face_image
)


print("\n========================================")
print("CLEAN MULTI-FACE IMAGE CREATED")
print("========================================")

print(f"\nFaces included: {len(faces)}")

print("\nKnown:")
print("Aaron_Peirsol")
print("Abdullah")
print("Abel_Pacheco")

print("\nUnknown:")
print("Aaron_Sorkin")
print("Abdel_Nasser_Assidi")

print(f"\nSaved to:\n{OUTPUT_PATH}")
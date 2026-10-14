import cv2
import numpy as np
from pathlib import Path


# ============================================================
# SETTINGS
# ============================================================

KNOWN_FOLDER = Path("data/lfw_test")
UNKNOWN_FOLDER = Path("data/lfw_unknown")

OUTPUT_FOLDER = Path("data/multi_face")
OUTPUT_PATH = OUTPUT_FOLDER / "multi_face_test.jpg"


# ============================================================
# SELECT THE FACES
# ============================================================

image_paths = [
    KNOWN_FOLDER / "Aaron_Peirsol.jpg",
    KNOWN_FOLDER / "Abdullah.jpg",
    KNOWN_FOLDER / "Abel_Pacheco.jpg",

    UNKNOWN_FOLDER / "Aaron_Sorkin.jpg",
    UNKNOWN_FOLDER / "Abdel_Nasser_Assidi.jpg",
]


# ============================================================
# LOAD AND RESIZE IMAGES
# ============================================================

faces = []

for image_path in image_paths:

    image = cv2.imread(str(image_path))

    if image is None:
        print(f"Could not read: {image_path}")
        continue

    # Resize every image to the same size
    image = cv2.resize(image, (250, 250))

    faces.append(image)

    print(f"Loaded: {image_path.name}")


# ============================================================
# CREATE THE MULTI-FACE IMAGE
# ============================================================

if len(faces) < 5:

    print("ERROR: Not all images were loaded.")

else:

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

    # Create output folder
    OUTPUT_FOLDER.mkdir(
        parents=True,
        exist_ok=True
    )

    # Save image
    cv2.imwrite(
        str(OUTPUT_PATH),
        multi_face_image
    )

    print("\n========================================")
    print("MULTI-FACE TEST IMAGE CREATED")
    print("========================================")

    print(f"\nSaved to: {OUTPUT_PATH}")

    print("\nFaces included:")
    print("1. Aaron_Peirsol (KNOWN)")
    print("2. Abdullah (KNOWN)")
    print("3. Abel_Pacheco (KNOWN)")
    print("4. Aaron_Sorkin (UNKNOWN)")
    print("5. Abdel_Nasser_Assidi (UNKNOWN)")
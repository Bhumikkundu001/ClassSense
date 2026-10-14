import cv2
import numpy as np
from pathlib import Path
from insightface.app import FaceAnalysis


# ============================================================
# PATHS
# ============================================================

KNOWN_FOLDER = Path("data/lfw_test")
UNKNOWN_FOLDER = Path("data/lfw_unknown")

OUTPUT_FOLDER = Path("data/multi_image_test")


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
# EXTRACT MAIN FACE
# ============================================================

def extract_main_face(image_path):

    image = cv2.imread(str(image_path))

    if image is None:
        print(f"Could not read: {image_path}")
        return None

    faces = app.get(image)

    if len(faces) == 0:
        print(f"No face detected: {image_path}")
        return None

    # Select largest face
    face = max(
        faces,
        key=lambda f:
        (f.bbox[2] - f.bbox[0]) *
        (f.bbox[3] - f.bbox[1])
    )

    x1, y1, x2, y2 = face.bbox.astype(int)

    # Add margin
    margin = 25

    x1 = max(0, x1 - margin)
    y1 = max(0, y1 - margin)
    x2 = min(image.shape[1], x2 + margin)
    y2 = min(image.shape[0], y2 + margin)

    crop = image[y1:y2, x1:x2]

    if crop.size == 0:
        return None

    return cv2.resize(crop, (250, 250))


# ============================================================
# CREATE ONE TEST IMAGE
# ============================================================

def create_test_image(image_name, image_paths):

    crops = []

    for image_path in image_paths:

        crop = extract_main_face(image_path)

        if crop is not None:
            crops.append(crop)

    if len(crops) == 0:
        print(f"No faces available for {image_name}")
        return

    # Make a grid with 3 columns
    blank = np.ones(
        (250, 250, 3),
        dtype=np.uint8
    ) * 255

    while len(crops) < 3:
        crops.append(blank.copy())

    row = np.hstack(crops[:3])

    output_path = OUTPUT_FOLDER / image_name

    cv2.imwrite(
        str(output_path),
        row
    )

    print(
        f"Created: {output_path}"
    )


# ============================================================
# CREATE OUTPUT FOLDER
# ============================================================

OUTPUT_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# IMAGE 1
# ============================================================

create_test_image(
    "image1.jpg",
    [
        KNOWN_FOLDER / "Aaron_Peirsol.jpg",
        KNOWN_FOLDER / "Abdullah.jpg",
        UNKNOWN_FOLDER / "Aaron_Sorkin.jpg",
    ]
)


# ============================================================
# IMAGE 2
# ============================================================

create_test_image(
    "image2.jpg",
    [
        KNOWN_FOLDER / "Abdullah.jpg",
        KNOWN_FOLDER / "Abel_Pacheco.jpg",
        UNKNOWN_FOLDER / "Abdel_Nasser_Assidi.jpg",
    ]
)


# ============================================================
# IMAGE 3
# ============================================================

create_test_image(
    "image3.jpg",
    [
        KNOWN_FOLDER / "Aaron_Peirsol.jpg",
        KNOWN_FOLDER / "Abel_Pacheco.jpg",
        KNOWN_FOLDER / "Abdullah.jpg",
    ]
)


print("\n========================================")
print("MULTI-IMAGE TEST DATA CREATED")
print("========================================")

print("\nExpected attendance:")
print("Aaron_Peirsol")
print("Abdullah")
print("Abel_Pacheco")

print("\nExpected unknown faces: 2")    

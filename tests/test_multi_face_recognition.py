import cv2
import numpy as np
from pathlib import Path
from insightface.app import FaceAnalysis


# ============================================================
# SETTINGS
# ============================================================

MATCH_THRESHOLD = 0.40

STUDENTS_FOLDER = Path("data/lfw_students")
TEST_IMAGE_PATH = Path(
    "data/multi_face/clean_multi_face_test.jpg"
)

OUTPUT_PATH = Path(
    "data/multi_face/clean_multi_face_result.jpg"
)


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
# BUILD STUDENT DATABASE
# ============================================================

def get_largest_face_embedding(image_path):

    image = cv2.imread(str(image_path))

    if image is None:
        return None

    faces = app.get(image)

    if len(faces) == 0:
        return None

    largest_face = max(
        faces,
        key=lambda f:
        (f.bbox[2] - f.bbox[0]) *
        (f.bbox[3] - f.bbox[1])
    )

    return largest_face.normed_embedding


student_database = {}

print("Building student database...\n")

for student_folder in sorted(STUDENTS_FOLDER.iterdir()):

    if not student_folder.is_dir():
        continue

    embeddings = []

    for image_path in sorted(student_folder.glob("*.jpg")):

        embedding = get_largest_face_embedding(
            image_path
        )

        if embedding is not None:
            embeddings.append(embedding)

    if len(embeddings) == 0:
        continue

    # Average enrollment embeddings
    reference_embedding = np.mean(
        embeddings,
        axis=0
    )

    # Normalize
    reference_embedding /= np.linalg.norm(
        reference_embedding
    )

    student_database[
        student_folder.name
    ] = reference_embedding

    print(
        f"Loaded {student_folder.name}: "
        f"{len(embeddings)} images"
    )


# ============================================================
# RECOGNIZE FACE
# ============================================================

def recognize_face(embedding):

    best_person = None
    best_score = -1

    for person_name, reference in student_database.items():

        score = float(
            np.dot(
                embedding,
                reference
            )
        )

        if score > best_score:

            best_score = score
            best_person = person_name

    if best_score >= MATCH_THRESHOLD:

        decision = "MATCH"

    else:

        decision = "UNKNOWN"

    return best_person, best_score, decision


# ============================================================
# LOAD MULTI-FACE IMAGE
# ============================================================

image = cv2.imread(
    str(TEST_IMAGE_PATH)
)

if image is None:

    print(
        f"ERROR: Could not load "
        f"{TEST_IMAGE_PATH}"
    )

    exit()


print("\n========================================")
print("MULTI-FACE RECOGNITION TEST")
print("========================================")


# ============================================================
# DETECT ALL FACES
# ============================================================

faces = app.get(image)

print(
    f"\nTotal faces detected: {len(faces)}"
)


# ============================================================
# PROCESS EVERY FACE
# ============================================================

present_students = set()
unknown_faces = 0


for index, face in enumerate(faces, start=1):

    embedding = face.normed_embedding

    person, score, decision = recognize_face(
        embedding
    )

    print(f"\nFace {index}")
    print(f"Best candidate: {person}")
    print(f"Similarity: {score:.4f}")
    print(f"Decision: {decision}")

    # Bounding box
    bbox = face.bbox.astype(int)

    x1, y1, x2, y2 = bbox

    if decision == "MATCH":

        present_students.add(person)

        label = (
            f"{person} "
            f"({score:.2f})"
        )

        color = (0, 255, 0)

    else:

        unknown_faces += 1

        label = (
            f"UNKNOWN "
            f"({score:.2f})"
        )

        color = (0, 0, 255)

    # Draw bounding box
    cv2.rectangle(
        image,
        (x1, y1),
        (x2, y2),
        color,
        2
    )

    # Draw label
    cv2.putText(
        image,
        label,
        (x1, max(y1 - 10, 20)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        color,
        2
    )


# ============================================================
# SAVE RESULT
# ============================================================

cv2.imwrite(
    str(OUTPUT_PATH),
    image
)


# ============================================================
# FINAL RESULTS
# ============================================================

print("\n========================================")
print("FINAL RESULTS")
print("========================================")

print(
    f"\nRecognized students: "
    f"{len(present_students)}"
)

for person in sorted(present_students):

    print(f"{person} -> PRESENT")

print(
    f"\nUnknown faces: "
    f"{unknown_faces}"
)

print(
    f"\nResult image saved to:\n"
    f"{OUTPUT_PATH}"
)

print("\n========================================")
print("TEST COMPLETE")
print("========================================")
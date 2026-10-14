import cv2
import numpy as np
from pathlib import Path
from insightface.app import FaceAnalysis


# ============================================================
# 1. LOAD INSIGHTFACE
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
# 2. GET MAIN FACE EMBEDDING
# ============================================================

def get_face_embedding(image_path):

    image = cv2.imread(str(image_path))

    if image is None:
        print(f"ERROR: Cannot read {image_path}")
        return None

    faces = app.get(image)

    if len(faces) == 0:
        print("ERROR: No face detected.")
        return None

    # Controlled test:
    # choose the largest face.
    face = max(
        faces,
        key=lambda f:
        (f.bbox[2] - f.bbox[0]) *
        (f.bbox[3] - f.bbox[1])
    )

    return face.normed_embedding


# ============================================================
# 3. COSINE SIMILARITY
# ============================================================

def cosine_similarity(a, b):

    return float(np.dot(a, b))


# ============================================================
# 4. BUILD STUDENT DATABASE
# ============================================================

students_folder = Path("data/students")

student_database = {}


for student_folder in students_folder.iterdir():

    if not student_folder.is_dir():
        continue

    student_id = student_folder.name

    enrollment_images = list(
        student_folder.glob("*.jpg")
    )

    embeddings = []

    for image_path in enrollment_images:

        embedding = get_face_embedding(
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

    student_database[student_id] = (
        reference_embedding
    )

    print(
        f"Loaded {student_id}: "
        f"{len(embeddings)} images"
    )


print(
    f"\nStudents loaded: "
    f"{len(student_database)}"
)


# ============================================================
# 5. LOAD UNKNOWN PERSON
# ============================================================

unknown_path = Path(
    "data/classroom/unknown_test.jpg"
)

unknown_embedding = get_face_embedding(
    unknown_path
)

if unknown_embedding is None:
    print("\nCould not process unknown image.")
    exit()


# ============================================================
# 6. COMPARE UNKNOWN AGAINST ALL STUDENTS
# ============================================================

print("\n========================================")
print("UNKNOWN PERSON TEST")
print("========================================")

best_student = None
best_score = -1


for student_id, reference_embedding in student_database.items():

    score = cosine_similarity(
        unknown_embedding,
        reference_embedding
    )

    print(
        f"Unknown → {student_id}: "
        f"{score:.4f}"
    )

    if score > best_score:

        best_score = score
        best_student = student_id


# ============================================================
# 7. SHOW BEST MATCH
# ============================================================

print("\n========================================")
print("BEST MATCH")
print("========================================")

print("Best candidate:", best_student)
print(f"Similarity: {best_score:.4f}")

print("\nNo automatic UNKNOWN threshold is being")
print("applied yet. We are collecting data first.")
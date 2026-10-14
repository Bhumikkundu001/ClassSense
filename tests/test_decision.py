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
# 2. GET FACE EMBEDDING
# ============================================================

def get_face_embedding(image_path):

    image = cv2.imread(str(image_path))

    if image is None:
        print(f"ERROR: Cannot read {image_path}")
        return None

    faces = app.get(image)

    if len(faces) == 0:
        print(f"ERROR: No face detected in {image_path}")
        return None

    # For this experiment, select the largest face.
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

for student_folder in sorted(students_folder.iterdir()):

    if not student_folder.is_dir():
        continue

    student_id = student_folder.name

    enrollment_images = sorted(
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

    # Create one reference embedding
    reference = np.mean(
        embeddings,
        axis=0
    )

    reference /= np.linalg.norm(reference)

    student_database[student_id] = reference

    print(
        f"Loaded {student_id}: "
        f"{len(embeddings)} enrollment images"
    )


print(
    f"\nStudents loaded: "
    f"{len(student_database)}"
)


# ============================================================
# 5. DECISION FUNCTION
# ============================================================

def classify_face(
    query_embedding,
    threshold=0.40
):

    best_student = None
    best_score = -1

    for student_id, reference in student_database.items():

        score = cosine_similarity(
            query_embedding,
            reference
        )

        if score > best_score:

            best_score = score
            best_student = student_id


    # ----------------------------------------
    # Temporary decision rule
    # ----------------------------------------

    if best_score >= threshold:

        decision = "MATCH"

    else:

        decision = "UNKNOWN"


    return (
        best_student,
        best_score,
        decision
    )


# ============================================================
# 6. TEST UNKNOWN PERSON
# ============================================================

print("\n========================================")
print("UNKNOWN PERSON")
print("========================================")

unknown_path = Path(
    "data/classroom/unknown_test.jpg"
)

unknown_embedding = get_face_embedding(
    unknown_path
)

if unknown_embedding is not None:

    student, score, decision = classify_face(
        unknown_embedding
    )

    print("Best candidate:", student)
    print(f"Similarity: {score:.4f}")
    print("Decision:", decision)


# ============================================================
# 7. TEST REAL CLASSROOM IMAGE
# ============================================================

print("\n========================================")
print("CLASSROOM TEST")
print("========================================")

classroom_path = Path(
    "data/classroom/1000296545.jpg"
)

image = cv2.imread(
    str(classroom_path)
)

if image is None:

    print("ERROR: Classroom image not found.")
    exit()


faces = app.get(image)

print(
    f"Faces detected: {len(faces)}"
)


for index, face in enumerate(faces):

    embedding = face.normed_embedding

    student, score, decision = classify_face(
        embedding
    )

    print(
        f"\nFace {index + 1}"
    )

    print(
        f"Candidate: {student}"
    )

    print(
        f"Similarity: {score:.4f}"
    )

    print(
        f"Decision: {decision}"
    )


print("\n========================================")
print("DECISION TEST COMPLETE")
print("========================================")
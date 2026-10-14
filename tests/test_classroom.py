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
# 2. LOAD STUDENT REFERENCE EMBEDDINGS
# ============================================================

student_database = {}

students_folder = Path("data/students")


def get_largest_face(faces):

    if len(faces) == 0:
        return None

    return max(
        faces,
        key=lambda face:
        (face.bbox[2] - face.bbox[0]) *
        (face.bbox[3] - face.bbox[1])
    )


for student_folder in students_folder.iterdir():

    if not student_folder.is_dir():
        continue

    student_id = student_folder.name

    # Ignore folders such as "test"
    enrollment_images = [
        image_path
        for image_path in student_folder.glob("*.jpg")
    ]

    embeddings = []

    for image_path in enrollment_images:

        image = cv2.imread(str(image_path))

        if image is None:
            continue

        faces = app.get(image)

        face = get_largest_face(faces)

        if face is not None:
            embeddings.append(face.normed_embedding)

    if len(embeddings) == 0:
        continue

    # Average the student's enrollment embeddings
    reference_embedding = np.mean(
        embeddings,
        axis=0
    )

    # Normalize
    reference_embedding /= np.linalg.norm(
        reference_embedding
    )

    student_database[student_id] = reference_embedding

    print(
        f"Loaded {student_id}: "
        f"{len(embeddings)} enrollment images"
    )


print(
    f"\nStudents in database: "
    f"{len(student_database)}\n"
)


# ============================================================
# 3. COSINE SIMILARITY
# ============================================================

def cosine_similarity(a, b):

    return float(np.dot(a, b))


# ============================================================
# 4. LOAD CLASSROOM IMAGE
# ============================================================

image_path = Path("data/classroom/1000296545.jpg")

image = cv2.imread(str(image_path))

if image is None:

    print("ERROR: Classroom image could not be loaded.")

    exit()


print("Classroom image loaded.")


# ============================================================
# 5. DETECT ALL FACES
# ============================================================

faces = app.get(image)

print(
    f"Faces detected in classroom: "
    f"{len(faces)}\n"
)


# ============================================================
# 6. RECOGNIZE EVERY FACE
# ============================================================

results = []


for index, face in enumerate(faces):

    query_embedding = face.normed_embedding

    best_student = None
    best_score = -1

    # Compare against every enrolled student
    for student_id, reference_embedding in student_database.items():

        score = cosine_similarity(
            query_embedding,
            reference_embedding
        )

        if score > best_score:

            best_score = score
            best_student = student_id

    results.append(
        (best_student, best_score, face)
    )


# ============================================================
# 7. DISPLAY RESULTS
# ============================================================

print("========================================")
print("CLASSROOM RECOGNITION RESULTS")
print("========================================")

for index, (student_id, score, face) in enumerate(results):

    print(
        f"Face {index + 1}: "
        f"{student_id} "
        f"(similarity = {score:.4f})"
    )


# ============================================================
# 8. DRAW RESULTS ON IMAGE
# ============================================================

for student_id, score, face in results:

    x1, y1, x2, y2 = face.bbox.astype(int)

    label = f"{student_id} {score:.2f}"

    cv2.rectangle(
        image,
        (x1, y1),
        (x2, y2),
        (0, 255, 0),
        2
    )

    cv2.putText(
        image,
        label,
        (x1, y1 - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2
    )


# ============================================================
# 9. SAVE RESULT
# ============================================================

output_path = "data/classroom/result.jpg"

cv2.imwrite(
    output_path,
    image
)

print("\nResult image saved to:")
print(output_path)
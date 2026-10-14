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
# 2. GET MAIN FACE EMBEDDINGS FOR ENROLLMENT
# ============================================================

def get_enrollment_embedding(image_path):

    image = cv2.imread(str(image_path))

    if image is None:
        return None

    faces = app.get(image)

    if len(faces) == 0:
        return None

    # Enrollment photos should contain one main face.
    face = max(
        faces,
        key=lambda f:
        (f.bbox[2] - f.bbox[0]) *
        (f.bbox[3] - f.bbox[1])
    )

    return face.normed_embedding


# ============================================================
# 3. BUILD STUDENT DATABASE
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

        embedding = get_enrollment_embedding(
            image_path
        )

        if embedding is not None:
            embeddings.append(embedding)

    if len(embeddings) == 0:
        continue

    # Average the student's enrollment embeddings
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
# 4. COSINE SIMILARITY
# ============================================================

def cosine_similarity(a, b):

    return float(np.dot(a, b))


# ============================================================
# 5. PROCESS CLASSROOM IMAGES
# ============================================================

classroom_folder = Path("data/classroom")

classroom_images = [
    classroom_folder / "1000296545.jpg"
]


all_results = []


for image_path in classroom_images:

    print("\n========================================")
    print(f"CLASSROOM IMAGE: {image_path.name}")
    print("========================================")

    image = cv2.imread(str(image_path))

    if image is None:

        print("Could not read image.")
        continue

    faces = app.get(image)

    print(
        f"Faces detected: {len(faces)}"
    )

    image_results = []

    # --------------------------------------------------------
    # Recognize EVERY detected face
    # --------------------------------------------------------

    for index, face in enumerate(faces):

        query_embedding = face.normed_embedding

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

        image_results.append(
            (best_student, best_score)
        )

        print(
            f"Face {index + 1}: "
            f"{best_student} "
            f"(similarity = {best_score:.4f})"
        )

    all_results.append(
        (image_path.name, image_results)
    )


# ============================================================
# 6. COLLECT UNIQUE IDENTITIES
# ============================================================

print("\n========================================")
print("UNIQUE IDENTITIES FOUND")
print("========================================")


unique_students = set()


for image_name, results in all_results:

    for student_id, score in results:

        unique_students.add(student_id)


for student_id in sorted(unique_students):

    print(student_id)


print(
    f"\nTotal unique identities: "
    f"{len(unique_students)}"
)


print("\n========================================")
print("MULTI-IMAGE TEST COMPLETE")
print("========================================")
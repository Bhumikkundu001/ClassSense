import cv2
import numpy as np
from pathlib import Path
from insightface.app import FaceAnalysis


# ============================================================
# SETTINGS
# ============================================================

MATCH_THRESHOLD = 0.40


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
# GET FACE EMBEDDING
# ============================================================

def get_embedding(image_path):

    image = cv2.imread(str(image_path))

    if image is None:
        print(f"Could not read: {image_path}")
        return None

    faces = app.get(image)

    if len(faces) == 0:
        print(f"No face detected: {image_path}")
        return None

    # Choose the largest face
    face = max(
        faces,
        key=lambda f:
        (f.bbox[2] - f.bbox[0]) *
        (f.bbox[3] - f.bbox[1])
    )

    return face.normed_embedding


# ============================================================
# COSINE SIMILARITY
# ============================================================

def cosine_similarity(a, b):
    return float(np.dot(a, b))


# ============================================================
# BUILD ENROLLMENT DATABASE
# ============================================================

students_folder = Path("data/lfw_students")

student_database = {}

print("Building student database...\n")

for student_folder in sorted(students_folder.iterdir()):

    if not student_folder.is_dir():
        continue

    student_name = student_folder.name

    embeddings = []

    for image_path in sorted(student_folder.glob("*.jpg")):

        embedding = get_embedding(image_path)

        if embedding is not None:
            embeddings.append(embedding)

    if not embeddings:
        continue

    # Average the enrollment embeddings
    reference = np.mean(
        embeddings,
        axis=0
    )

    # Normalize the averaged embedding
    reference /= np.linalg.norm(reference)

    student_database[student_name] = reference

    print(
        f"Loaded {student_name}: "
        f"{len(embeddings)} enrollment images"
    )


print(
    f"\nTotal enrolled students: "
    f"{len(student_database)}"
)


# ============================================================
# RECOGNITION FUNCTION
# ============================================================

def recognize_face(query_embedding):

    best_person = None
    best_score = -1

    for person_name, reference in student_database.items():

        score = cosine_similarity(
            query_embedding,
            reference
        )

        if score > best_score:

            best_score = score
            best_person = person_name

    if best_score >= MATCH_THRESHOLD:

        return best_person, best_score, "MATCH"

    return best_person, best_score, "UNKNOWN"


# ============================================================
# PROCESS KNOWN TEST FACES
# ============================================================

known_folder = Path("data/lfw_test")
unknown_folder = Path("data/lfw_unknown")

present_students = set()
unknown_faces = 0


print("\n========================================")
print("LFW ATTENDANCE SESSION")
print("========================================")


# ------------------------------------------------------------
# PROCESS KNOWN PEOPLE
# ------------------------------------------------------------

print("\n--- PROCESSING KNOWN TEST FACES ---")

for image_path in sorted(known_folder.glob("*.jpg")):

    print(f"\nProcessing: {image_path.name}")

    embedding = get_embedding(image_path)

    if embedding is None:
        continue

    person, score, decision = recognize_face(
        embedding
    )

    print(f"Candidate: {person}")
    print(f"Similarity: {score:.4f}")
    print(f"Decision: {decision}")

    if decision == "MATCH":

        present_students.add(person)

    else:

        unknown_faces += 1


# ------------------------------------------------------------
# PROCESS UNKNOWN PEOPLE
# ------------------------------------------------------------

print("\n--- PROCESSING UNKNOWN TEST FACES ---")

for image_path in sorted(unknown_folder.glob("*.jpg")):

    print(f"\nProcessing: {image_path.name}")

    embedding = get_embedding(image_path)

    if embedding is None:
        continue

    person, score, decision = recognize_face(
        embedding
    )

    print(f"Best candidate: {person}")
    print(f"Similarity: {score:.4f}")
    print(f"Decision: {decision}")

    if decision == "MATCH":

        print("WARNING: Unknown person incorrectly matched!")

        present_students.add(person)

    else:

        unknown_faces += 1


# ============================================================
# FINAL ATTENDANCE
# ============================================================

print("\n========================================")
print("FINAL ATTENDANCE")
print("========================================")


for person in sorted(present_students):

    print(f"{person} -> PRESENT")


print("\n========================================")
print("SUMMARY")
print("========================================")

print(
    f"Present students: "
    f"{len(present_students)}"
)

print(
    f"Unknown faces: "
    f"{unknown_faces}"
)

print(
    f"Absent students: "
    f"{len(student_database) - len(present_students)}"
)


print("\n========================================")
print("ATTENDANCE TEST COMPLETE")
print("========================================")
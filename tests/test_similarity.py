import cv2
import numpy as np
from pathlib import Path
from itertools import combinations
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

def get_embedding(image_path):

    image = cv2.imread(str(image_path))

    if image is None:
        print(f"Could not read: {image_path}")
        return None

    faces = app.get(image)

    if len(faces) == 0:
        print(f"No face detected: {image_path}")
        return None

    # For enrollment photos, choose the largest face.
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
# 4. LOAD ALL STUDENTS
# ============================================================

students_folder = Path("data/students")

student_embeddings = {}

for student_folder in sorted(students_folder.iterdir()):

    if not student_folder.is_dir():
        continue

    student_id = student_folder.name

    # Only enrollment images directly inside the student folder
    image_paths = sorted(
        student_folder.glob("*.jpg")
    )

    embeddings = []

    for image_path in image_paths:

        embedding = get_embedding(image_path)

        if embedding is not None:
            embeddings.append(embedding)

    if len(embeddings) == 0:
        continue

    student_embeddings[student_id] = embeddings

    print(
        f"{student_id}: "
        f"{len(embeddings)} embeddings loaded"
    )


print("\n========================================")
print("DATASET READY")
print("========================================")

print(
    "Students:",
    len(student_embeddings)
)


# ============================================================
# 5. SAME-STUDENT COMPARISONS
# ============================================================

same_scores = []

print("\n========================================")
print("SAME-STUDENT SIMILARITY")
print("========================================")

for student_id, embeddings in student_embeddings.items():

    if len(embeddings) < 2:
        continue

    scores = []

    for a, b in combinations(embeddings, 2):

        score = cosine_similarity(a, b)

        same_scores.append(score)
        scores.append(score)

    print(
        f"{student_id}: "
        f"min={min(scores):.4f}, "
        f"max={max(scores):.4f}, "
        f"avg={np.mean(scores):.4f}"
    )


# ============================================================
# 6. DIFFERENT-STUDENT COMPARISONS
# ============================================================

different_scores = []

print("\n========================================")
print("DIFFERENT-STUDENT SIMILARITY")
print("========================================")


student_ids = list(student_embeddings.keys())


for student_a, student_b in combinations(student_ids, 2):

    embeddings_a = student_embeddings[student_a]
    embeddings_b = student_embeddings[student_b]

    pair_scores = []

    for embedding_a in embeddings_a:

        for embedding_b in embeddings_b:

            score = cosine_similarity(
                embedding_a,
                embedding_b
            )

            different_scores.append(score)
            pair_scores.append(score)

    print(
        f"{student_a} vs {student_b}: "
        f"min={min(pair_scores):.4f}, "
        f"max={max(pair_scores):.4f}, "
        f"avg={np.mean(pair_scores):.4f}"
    )


# ============================================================
# 7. OVERALL STATISTICS
# ============================================================

print("\n========================================")
print("OVERALL RESULTS")
print("========================================")


if same_scores:

    print("\nSAME PERSON:")

    print(
        f"Minimum: {min(same_scores):.4f}"
    )

    print(
        f"Maximum: {max(same_scores):.4f}"
    )

    print(
        f"Average: {np.mean(same_scores):.4f}"
    )


if different_scores:

    print("\nDIFFERENT PEOPLE:")

    print(
        f"Minimum: {min(different_scores):.4f}"
    )

    print(
        f"Maximum: {max(different_scores):.4f}"
    )

    print(
        f"Average: {np.mean(different_scores):.4f}"
    )


print("\n========================================")
print("SIMILARITY TEST COMPLETE")
print("========================================")
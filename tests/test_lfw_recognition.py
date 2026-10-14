import cv2
import numpy as np
from pathlib import Path
from insightface.app import FaceAnalysis


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

    # Choose the largest detected face
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
        print(f"No valid images for {student_name}")
        continue

    # Average all enrollment embeddings
    reference_embedding = np.mean(
        embeddings,
        axis=0
    )

    # Normalize again
    reference_embedding /= np.linalg.norm(
        reference_embedding
    )

    student_database[student_name] = reference_embedding

    print(
        f"Loaded {student_name}: "
        f"{len(embeddings)} enrollment images"
    )


# ============================================================
# TEST UNSEEN PHOTOS
# ============================================================

test_folder = Path("data/lfw_test")

correct = 0
total = 0

print("\n========================================")
print("LFW RECOGNITION TEST")
print("========================================")


for test_image in sorted(test_folder.glob("*.jpg")):

    actual_person = test_image.stem

    query_embedding = get_embedding(test_image)

    if query_embedding is None:
        continue

    best_person = None
    best_score = -1

    print(f"\nTesting: {test_image.name}")

    for student_name, reference_embedding in student_database.items():

        score = cosine_similarity(
            query_embedding,
            reference_embedding
        )

        print(
            f"  {student_name}: {score:.4f}"
        )

        if score > best_score:

            best_score = score
            best_person = student_name

    total += 1

    if best_person == actual_person:

        correct += 1
        result = "CORRECT"

    else:

        result = "WRONG"

    print("\nBest Match:", best_person)
    print("Actual Person:", actual_person)
    print(f"Best Similarity: {best_score:.4f}")
    print("Result:", result)


# ============================================================
# FINAL ACCURACY
# ============================================================

print("\n========================================")
print("FINAL RESULTS")
print("========================================")

print(f"Correct recognitions: {correct}/{total}")

if total > 0:

    accuracy = (correct / total) * 100

    print(f"Accuracy: {accuracy:.2f}%")

else:

    print("No valid test images found.")

print("\n========================================")
print("TEST COMPLETE")
print("========================================")
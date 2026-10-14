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
# 2. FUNCTION TO GET THE MAIN FACE EMBEDDING
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

    # For this controlled experiment:
    # choose the largest detected face.
    face = max(
        faces,
        key=lambda f:
        (f.bbox[2] - f.bbox[0]) *
        (f.bbox[3] - f.bbox[1])
    )

    # ArcFace normalized embedding
    embedding = face.normed_embedding

    return embedding


# ============================================================
# 3. COSINE SIMILARITY
# ============================================================

def cosine_similarity(embedding1, embedding2):

    return float(
        np.dot(embedding1, embedding2)
    )


# ============================================================
# 4. LOAD BU001 ENROLLMENT PHOTOS
# ============================================================

enrollment_folder = Path("data/students/BU001")

enrollment_images = [
    enrollment_folder / "1000296538.jpg",
    enrollment_folder / "1000296539.jpg",
    enrollment_folder / "1000296540.jpg"
]


print("========================================")
print("BU001 ENROLLMENT")
print("========================================")

enrollment_embeddings = []

for image_path in enrollment_images:

    print(f"Processing: {image_path.name}")

    embedding = get_face_embedding(image_path)

    if embedding is not None:

        enrollment_embeddings.append(embedding)

        print("  Face detected")
        print("  Embedding shape:", embedding.shape)
        print()

    else:

        print("  FAILED\n")


# ============================================================
# 5. CREATE BU001 REFERENCE EMBEDDING
# ============================================================

if len(enrollment_embeddings) == 0:

    print("ERROR: No enrollment embeddings found.")
    exit()


# Average the enrollment embeddings
reference_embedding = np.mean(
    enrollment_embeddings,
    axis=0
)

# Normalize the resulting reference embedding
reference_embedding = (
    reference_embedding /
    np.linalg.norm(reference_embedding)
)


print("BU001 reference embedding created.")
print(
    "Number of enrollment photos:",
    len(enrollment_embeddings)
)


# ============================================================
# 6. LOAD TEST PHOTOS
# ============================================================

test_folder = enrollment_folder / "test"

test_images = sorted(
    test_folder.glob("*.jpg")
)


print("\n========================================")
print("BU001 RECOGNITION TEST")
print("========================================")


# ============================================================
# 7. TEST EACH PHOTO
# ============================================================

for image_path in test_images:

    print(f"\nTesting: {image_path.name}")

    test_embedding = get_face_embedding(
        image_path
    )

    if test_embedding is None:

        print("  Could not generate embedding.")
        continue

    similarity = cosine_similarity(
        reference_embedding,
        test_embedding
    )

    print(
        f"  Cosine similarity: {similarity:.4f}"
    )

    print(
        "  This is the similarity between "
        "the test face and BU001."
    )


print("\n========================================")
print("TEST COMPLETE")
print("========================================")
# ============================================================
# 8. TEST AGAINST ANOTHER STUDENT
# ============================================================

print("\n========================================")
print("DIFFERENT STUDENT TEST")
print("========================================")

other_student_folder = Path("data/students/BU002")

other_student_images = sorted(
    other_student_folder.glob("*.jpg")
)

for image_path in other_student_images:

    print(f"\nTesting: BU002/{image_path.name}")

    test_embedding = get_face_embedding(
        image_path
    )

    if test_embedding is None:
        print("  Could not generate embedding.")
        continue

    similarity = cosine_similarity(
        reference_embedding,
        test_embedding
    )

    print(
        f"  Similarity to BU001: {similarity:.4f}"
    )
    # ============================================================
# 9. UNKNOWN PERSON TEST
# ============================================================

print("\n========================================")
print("UNKNOWN PERSON TEST")
print("========================================")

unknown_image = Path(
    "data/classroom/unknown_test.jpg"
)

unknown_embedding = get_face_embedding(
    unknown_image
)

if unknown_embedding is None:

    print("Could not detect a face in unknown image.")

else:

    for student_id, reference_embedding in student_database.items():

        similarity = cosine_similarity(
            unknown_embedding,
            reference_embedding
        )

        print(
            f"Unknown person → {student_id}: "
            f"{similarity:.4f}"
        )
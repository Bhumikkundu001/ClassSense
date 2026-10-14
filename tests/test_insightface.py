import cv2
from pathlib import Path
from insightface.app import FaceAnalysis


# -----------------------------------
# 1. Load InsightFace
# -----------------------------------

print("Loading InsightFace...")

app = FaceAnalysis(
    name="buffalo_l",
    providers=["CPUExecutionProvider"]
)

app.prepare(
    ctx_id=0,
    det_size=(640, 640)
)

print("Model loaded successfully!\n")


# -----------------------------------
# 2. Only test BU001
# -----------------------------------

student_id = "BU001"

student_folder = Path("data") / "students" / student_id

print(f"Testing student: {student_id}")
print(f"Folder: {student_folder}\n")


# -----------------------------------
# 3. Process the 3 photos
# -----------------------------------

for image_path in sorted(student_folder.glob("*.jpg")):

    print(f"Processing: {image_path.name}")

    image = cv2.imread(str(image_path))

    if image is None:
        print("  ERROR: Could not read image.")
        continue

    faces = app.get(image)

    print(f"  Faces detected: {len(faces)}")

    for face in faces:

        print(
            f"  Detection confidence: "
            f"{face.det_score:.4f}"
        )

        print(
            f"  Embedding shape: "
            f"{face.embedding.shape}"
        )

    print()


print("Test completed.")
import cv2
import numpy as np
import csv
from pathlib import Path
from insightface.app import FaceAnalysis


# ============================================================
# SETTINGS
# ============================================================

MATCH_THRESHOLD = 0.40

STUDENTS_FOLDER = Path("data/lfw_students")
CLASSROOM_FOLDER = Path("data/multi_image_test")

OUTPUT_FOLDER = Path("data/multi_image_results")

OUTPUT_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)
CSV_OUTPUT_PATH = OUTPUT_FOLDER / "attendance.csv"


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
# GET LARGEST FACE EMBEDDING
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


# ============================================================
# BUILD STUDENT DATABASE
# ============================================================

print("Building student database...\n")

student_database = {}

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


print(
    f"\nTotal enrolled students: "
    f"{len(student_database)}"
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

        return best_person, best_score, "MATCH"

    return best_person, best_score, "UNKNOWN"


# ============================================================
# FINAL ATTENDANCE STORAGE
# ============================================================

present_students = set()

total_faces = 0
total_unknown_faces = 0


# ============================================================
# PROCESS ALL CLASSROOM IMAGES
# ============================================================

image_paths = sorted(
    CLASSROOM_FOLDER.glob("*.jpg")
)

print("\n========================================")
print("MULTI-IMAGE ATTENDANCE SESSION")
print("========================================")

print(
    f"\nClassroom images found: "
    f"{len(image_paths)}"
)


for image_path in image_paths:

    print("\n========================================")
    print(f"PROCESSING: {image_path.name}")
    print("========================================")

    image = cv2.imread(
        str(image_path)
    )

    if image is None:

        print("Could not read image.")
        continue

    # Detect all faces
    faces = app.get(image)

    print(
        f"Faces detected: {len(faces)}"
    )

    image_unknown_count = 0
    image_matches = set()


    # --------------------------------------------------------
    # PROCESS EACH FACE
    # --------------------------------------------------------

    for index, face in enumerate(
        faces,
        start=1
    ):

        total_faces += 1

        embedding = face.normed_embedding

        person, score, decision = recognize_face(
            embedding
        )

        print(f"\nFace {index}")
        print(f"Candidate: {person}")
        print(f"Similarity: {score:.4f}")
        print(f"Decision: {decision}")


        # Bounding box
        bbox = face.bbox.astype(int)

        x1, y1, x2, y2 = bbox


        if decision == "MATCH":

            # Add to final attendance
            present_students.add(person)

            # Add to this image's matches
            image_matches.add(person)

            label = (
                f"{person} "
                f"({score:.2f})"
            )

            color = (0, 255, 0)


        else:

            total_unknown_faces += 1
            image_unknown_count += 1

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


    # --------------------------------------------------------
    # SAVE ANNOTATED IMAGE
    # --------------------------------------------------------

    output_path = (
        OUTPUT_FOLDER /
        image_path.name
    )

    cv2.imwrite(
        str(output_path),
        image
    )


    print("\n--- IMAGE SUMMARY ---")

    print(
        "Recognized: "
        f"{len(image_matches)}"
    )

    for person in sorted(image_matches):

        print(f"{person} -> PRESENT")

    print(
        f"Unknown faces: "
        f"{image_unknown_count}"
    )

    print(
        f"Result saved: "
        f"{output_path}"
    )


# ============================================================
# FINAL ATTENDANCE REPORT
# ============================================================

print("\n")
print("========================================")
print("FINAL CLASS ATTENDANCE")
print("========================================")

print(
    f"\nTotal unique students present: "
    f"{len(present_students)}"
)

for person in sorted(present_students):

    print(f"{person} -> PRESENT")


# ============================================================
# ABSENT STUDENTS
# ============================================================

all_students = set(
    student_database.keys()
)

absent_students = (
    all_students -
    present_students
)


print("\n========================================")
print("ABSENT STUDENTS")
print("========================================")

print(
    f"\nTotal absent students: "
    f"{len(absent_students)}"
)

for person in sorted(absent_students):

    print(f"{person} -> ABSENT")


# ============================================================
# FINAL STATISTICS
# ============================================================

print("\n========================================")
print("FINAL STATISTICS")
print("========================================")

print(
    f"Classroom images processed: "
    f"{len(image_paths)}"
)

print(
    f"Total faces detected: "
    f"{total_faces}"
)

print(
    f"Unique students recognized: "
    f"{len(present_students)}"
)

print(
    f"Unknown faces detected: "
    f"{total_unknown_faces}"
)

print(
    f"Absent students: "
    f"{len(absent_students)}"
)


print("\n========================================")
print("MULTI-IMAGE ATTENDANCE TEST COMPLETE")
print("========================================")
# ============================================================
# SAVE ATTENDANCE TO CSV
# ============================================================

with open(
    CSV_OUTPUT_PATH,
    mode="w",
    newline="",
    encoding="utf-8"
) as csv_file:

    writer = csv.writer(csv_file)

    # CSV header
    writer.writerow([
        "Student_ID",
        "Attendance_Status"
    ])

    # Present students
    for student in sorted(present_students):

        writer.writerow([
            student,
            "PRESENT"
        ])

    # Absent students
    for student in sorted(absent_students):

        writer.writerow([
            student,
            "ABSENT"
        ])


print("\n========================================")
print("CSV ATTENDANCE REPORT")
print("========================================")

print(
    f"\nAttendance saved successfully to:\n"
    f"{CSV_OUTPUT_PATH}"
)
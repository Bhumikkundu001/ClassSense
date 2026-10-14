from pathlib import Path
import shutil


# ============================================================
# SOURCE LFW DATASET
# ============================================================

SOURCE_FOLDER = Path(
    "archive (1)/lfw-deepfunneled/lfw-deepfunneled"
)


# ============================================================
# FIND PEOPLE WITH AT LEAST 4 PHOTOS
# ============================================================

valid_people = []

for person_folder in sorted(SOURCE_FOLDER.iterdir()):

    if not person_folder.is_dir():
        continue

    images = sorted(person_folder.glob("*.jpg"))

    if len(images) >= 4:

        valid_people.append(
            (person_folder.name, images)
        )


print(
    f"People with at least 4 photos: "
    f"{len(valid_people)}"
)


# ============================================================
# SELECT FIRST 5 PEOPLE
# ============================================================

selected_people = valid_people[:5]


print("\nSELECTED PEOPLE:")

for name, images in selected_people:

    print(
        f"{name}: {len(images)} available images"
    )


# ============================================================
# CREATE DESTINATION FOLDERS
# ============================================================

students_folder = Path("data/lfw_students")
test_folder = Path("data/lfw_test")


students_folder.mkdir(
    parents=True,
    exist_ok=True
)

test_folder.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# COPY IMAGES
# ============================================================

for person_name, images in selected_people:

    # Create enrollment folder
    person_destination = (
        students_folder / person_name
    )

    person_destination.mkdir(
        exist_ok=True
    )


    # First 3 images → enrollment
    for index, image_path in enumerate(images[:3]):

        destination = (
            person_destination /
            f"{index + 1}.jpg"
        )

        shutil.copy2(
            image_path,
            destination
        )


    # Fourth image → test image
    test_destination = (
        test_folder /
        f"{person_name}.jpg"
    )

    shutil.copy2(
        images[3],
        test_destination
    )


print("\n========================================")
print("LFW DATA PREPARATION COMPLETE")
print("========================================")

print(
    f"\nEnrollment data: {students_folder}"
)

print(
    f"Test data: {test_folder}"
)
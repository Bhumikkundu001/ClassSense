from pathlib import Path
import shutil


# ============================================================
# SOURCE LFW DATASET
# ============================================================

SOURCE_FOLDER = Path(
    "archive (1)/lfw-deepfunneled/lfw-deepfunneled"
)


# ============================================================
# OUR ENROLLED PEOPLE
# ============================================================

enrolled_people = {
    "Aaron_Peirsol",
    "Abdoulaye_Wade",
    "Abdullah",
    "Abdullah_Gul",
    "Abel_Pacheco"
}


# ============================================================
# FIND UNKNOWN PEOPLE
# ============================================================

unknown_people = []

for person_folder in sorted(SOURCE_FOLDER.iterdir()):

    if not person_folder.is_dir():
        continue

    person_name = person_folder.name

    # Skip enrolled identities
    if person_name in enrolled_people:
        continue

    images = sorted(person_folder.glob("*.jpg"))

    # Select identities with at least 2 photos
    if len(images) >= 2:

        unknown_people.append(
            (person_name, images)
        )


# ============================================================
# SELECT 3 UNKNOWN IDENTITIES
# ============================================================

selected_unknowns = unknown_people[:3]

print("SELECTED UNKNOWN PEOPLE:\n")


# ============================================================
# DESTINATION FOLDER
# ============================================================

unknown_folder = Path(
    "data/lfw_unknown"
)

unknown_folder.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# COPY ONE TEST IMAGE PER UNKNOWN PERSON
# ============================================================

for person_name, images in selected_unknowns:

    source_image = images[-1]

    destination = (
        unknown_folder /
        f"{person_name}.jpg"
    )

    shutil.copy2(
        source_image,
        destination
    )

    print(
        f"{person_name} -> "
        f"{source_image.name}"
    )


print("\n========================================")
print("UNKNOWN DATA PREPARATION COMPLETE")
print("========================================")

print(
    f"Unknown test images: "
    f"{len(list(unknown_folder.glob('*.jpg')))}"
)
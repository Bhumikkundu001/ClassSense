
import cv2


class FaceDetector:
    """
    Handles InsightFace model loading and face detection.
    The heavy InsightFace import is deferred until needed.
    """

    def __init__(self):
        print("Loading InsightFace...")

        # Import only when a detector is actually initialized.
        from insightface.app import FaceAnalysis

        from classesense.core import (
            MODEL_NAME,
            PROVIDERS,
            DETECTION_SIZE,
        )

        self.app = FaceAnalysis(
            name=MODEL_NAME,
            providers=PROVIDERS,
        )

        self.app.prepare(
            ctx_id=0,
            det_size=DETECTION_SIZE,
        )

        print("InsightFace loaded successfully!\n")

    def detect_faces(self, image):
        """Detect faces in an OpenCV image."""
        return self.app.get(image)

    def get_largest_face_embedding(self, image_path):
        """Return the normalized embedding of the largest face."""
        image = cv2.imread(str(image_path))

        if image is None:
            return None

        faces = self.detect_faces(image)

        if not faces:
            return None

        largest_face = max(
            faces,
            key=lambda face: (
                (face.bbox[2] - face.bbox[0])
                * (face.bbox[3] - face.bbox[1])
            ),
        )

        return largest_face.normed_embedding

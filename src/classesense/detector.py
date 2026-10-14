import cv2
from insightface.app import FaceAnalysis

from classesense.core import (
    MODEL_NAME,
    PROVIDERS,
    DETECTION_SIZE,
)

class FaceDetector:
    """
    Handles InsightFace model loading and face detection.
    """

    def __init__(self):

        print("Loading InsightFace...")

        self.app = FaceAnalysis(
            name=MODEL_NAME,
            providers=PROVIDERS
        )

        self.app.prepare(
        ctx_id=0,
        det_size=DETECTION_SIZE
        )

        print("InsightFace loaded successfully!\n")


    def detect_faces(self, image):
        """
        Detect all faces in an OpenCV image.

        Returns:
            List of detected InsightFace face objects.
        """

        return self.app.get(image)


    def get_largest_face_embedding(self, image_path):
        """
        Read an image, detect faces, select the largest face,
        and return its normalized embedding.

        Returns:
            NumPy embedding or None if no face is found.
        """

        image = cv2.imread(
            str(image_path)
        )

        if image is None:
            return None

        faces = self.detect_faces(
            image
        )

        if len(faces) == 0:
            return None

        largest_face = max(
            faces,
            key=lambda face:
            (face.bbox[2] - face.bbox[0]) *
            (face.bbox[3] - face.bbox[1])
        )

        return largest_face.normed_embedding
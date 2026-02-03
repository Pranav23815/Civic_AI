from ultralytics import YOLO
from multiprocessing import freeze_support

if __name__ == "__main__":
    freeze_support()

    model = YOLO("yolov8n-seg.pt")

    model.train(
        data=r"D:\uDDDDD\civic_eye_project\Pothole_Segmentation_YOLOv8\data.yaml",
        epochs=40,
        imgsz=640,
        batch=8
    )

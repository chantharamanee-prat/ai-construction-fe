import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  fetchPercentageDataset,
  saveAnnotation,
  type Annotation,
  type PercentageDataset,
} from "../../api/annotationService";
import ImageViewer, { type ImageMetadata } from "./ImageViewer";
import DrawingCanvas from "./DrawingCanvas";
import ProgressForm from "./ProgressForm";
import ClassSelector, { type ClassId } from "./ClassSelector";

const AnnotationTool: React.FC = () => {
  const { datasetName, index } = useParams();

  const navigate = useNavigate();
  const [dataset, setDataset] = useState<PercentageDataset[] | null>(null);
  const [currentImageIndex, setCurrentImageIndex] = useState<number>(
    index ? +index : 0
  );
  const [annotation, setAnnotation] = useState<Annotation | null>(null);
  const [loading, setLoading] = useState(true);
  const [imageMetadata, setImageMetadata] = useState<ImageMetadata | null>(
    null
  );
  const [selectedClass, setSelectedClass] = useState<ClassId>(0);

  useEffect(() => {
    async function loadDataset() {
      try {
        if (!datasetName) {
          throw new Error("Dataset name is required");
        }

        const datasetData = await fetchPercentageDataset(datasetName);
        setDataset(datasetData);
        const dataIndex = datasetData[currentImageIndex];
        console.log(dataIndex);
        setAnnotation({
          boxes: dataIndex.boxes || [],
          progress: dataIndex.progress || 0,
          imageName: dataIndex.path,
        });
      } catch (error) {
        alert(
          "Failed to load dataset: " +
            (error instanceof Error ? error.message : String(error))
        );
      } finally {
        setLoading(false);
      }
    }
    loadDataset();
  }, [datasetName, index]);

  const handleBoxChange = (boxes: Annotation["boxes"]) => {
    if (annotation) {
      setAnnotation({ ...annotation, boxes });
    }
  };

  const handleProgressChange = (progress: number) => {
    if (annotation) {
      setAnnotation({ ...annotation, progress });
    }
  };

  const handleSave = async () => {
    if (annotation) {
      console.log("Saving annotation:", annotation);
      try {
        await saveAnnotation(annotation);
        alert("Annotation saved successfully");
      } catch (error) {
        alert(
          "Failed to save annotation: " +
            (error instanceof Error ? error.message : String(error))
        );
      }
    }
  };

  const handleNextImage = () => {
    if (dataset && currentImageIndex < dataset.length - 1) {
      const nextIndex = currentImageIndex + 1;
      setCurrentImageIndex(nextIndex);
      const nextImage = dataset[nextIndex];
      setAnnotation({
        boxes: nextImage.boxes || [],
        progress: nextImage.progress || 0,
        imageName: nextImage.path,
      });
      navigate(`/annotate/${datasetName}/${nextIndex}`);
    } else {
      navigate("/");
    }
  };

  const handleBackToList = () => {
    navigate("/");
  };

  const handleImageLoad = (metadata: ImageMetadata) => {
    setImageMetadata(metadata);
  };

  if (loading) {
    return <div>Loading dataset...</div>;
  }

  if (!dataset || dataset.length === 0) {
    return <div>No images found in dataset</div>;
  }

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between" }}>
        <h2>Annotation Tool</h2>
        <button onClick={handleBackToList}>Back to Dataset List</button>
      </div>
      <div>
        <p>Current Dataset: {dataset[currentImageIndex]?.path || "Unknown"}</p>
        <div
          style={{
            position: "relative",
            width: "600px",
            height: "400px",
            border: "1px solid #ccc",
            marginBottom: "10px",
          }}
        >
          <ImageViewer
            imagePath={dataset[currentImageIndex]?.path}
            onImageLoad={handleImageLoad}
          />
          <div
            style={{
              position: "absolute",
              top: 0,
              left: 0,
              width: "100%",
              height: "100%",
              pointerEvents: "auto",
              zIndex: 10,
            }}
          >
            <DrawingCanvas
              boxes={annotation?.boxes || []}
              onChange={handleBoxChange}
              imageMetadata={imageMetadata || undefined}
              selectedClass={selectedClass}
            />
          </div>
        </div>
        <ClassSelector
          selectedClass={selectedClass}
          onChange={setSelectedClass}
        />
        <ProgressForm
          progress={annotation?.progress || 0}
          onChange={handleProgressChange}
        />

        {/* Debug Information */}
        {imageMetadata && (
          <div
            style={{
              marginTop: "10px",
              padding: "10px",
              // backgroundColor: "#",
              fontSize: "12px",
            }}
          >
            <h4>Debug Info:</h4>
            <p>
              Image: {imageMetadata.naturalWidth} ×{" "}
              {imageMetadata.naturalHeight}
            </p>
            <p>
              Rendered: {Math.round(imageMetadata.renderedWidth)} ×{" "}
              {Math.round(imageMetadata.renderedHeight)}
            </p>
            <p>
              Position: ({Math.round(imageMetadata.renderedX)},{" "}
              {Math.round(imageMetadata.renderedY)})
            </p>
            <p>Boxes: {annotation?.boxes?.length || 0}</p>
            {annotation?.boxes && annotation.boxes.length > 0 && (
              <div>
                <h5>YOLO Coordinates:</h5>
                {annotation.boxes.map((box, i) => (
                  <p key={i}>
                    Box {i + 1}: Class {box.classId}, Center (
                    {box.xCenter.toFixed(3)}, {box.yCenter.toFixed(3)}), Size{" "}
                    {box.width.toFixed(3)} × {box.height.toFixed(3)}
                  </p>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
      <button style={{ marginRight: "20px" }} onClick={handleSave}>
        Save
      </button>

      <button
        onClick={handleNextImage}
        disabled={!dataset || currentImageIndex >= dataset.length - 1}
      >
        Next
      </button>
    </div>
  );
};

export default AnnotationTool;

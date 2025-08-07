import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import DatasetListPage from "./components/DatasetList/DatasetListPage";
import AnnotationTool from "./components/AnnotationTool/AnnotationTool";
import Menu from "./components/Menu";
import MLPredictPage from "./components/MLPredictPage";

function App() {
  return (
    <BrowserRouter>
      <Menu />
      <Routes>
        <Route path="/" element={<DatasetListPage />} />
        <Route
          path="/annotate/:datasetName/:index"
          element={<AnnotationTool />}
        />
        <Route path="/ml-predict" element={<MLPredictPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;

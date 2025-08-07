import './App.css'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import DatasetListPage from './components/DatasetList/DatasetListPage'
import AnnotationTool from './components/AnnotationTool/AnnotationTool'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<DatasetListPage />} />
        <Route path="/annotate/:datasetName" element={<AnnotationTool />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App

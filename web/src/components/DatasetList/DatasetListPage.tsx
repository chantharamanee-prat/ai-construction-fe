import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import './DatasetListPage.css'
import { fetchDatasets, type Dataset } from '../../api/annotationService'



export default function DatasetListPage() {
  const [datasets, setDatasets] = useState<Dataset[]>([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    const fetchData = async () => {
      try {
        let response = await fetchDatasets();
        response = response.sort((a,b) => a.progress - b.progress )
        setDatasets(response)
      } catch (error) {
        console.error('Error fetching datasets:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  const handleAnnotate = (datasetName: string) => {
    navigate(`/annotate/${encodeURIComponent(datasetName)}`)
  }

  if (loading) return <div>Loading datasets...</div>

  return (
    <div className="dataset-list-container">
      <h1>Datasets</h1>
      <table>
        <thead>
          <tr>
            <th>Dataset</th>
            <th>Images</th>
            <th>Annotated</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {datasets.map(dataset => (
            <tr key={dataset.name}>
              <td>{dataset.name}</td>
              <td>{dataset.image_count}</td>
              <td>{dataset.annotated_count}</td>
              <td>
                <button onClick={() => handleAnnotate(dataset.name)}>
                  Annotate
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

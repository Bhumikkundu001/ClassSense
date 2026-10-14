import { useState } from "react"
import "./App.css"

import Login from "./pages/Login"


const API_URL = "http://127.0.0.1:8000"


function App() {

  // ----------------------------------------------
  // AUTHENTICATION
  // ----------------------------------------------

  const [user, setUser] = useState(null)


  // ----------------------------------------------
  // ATTENDANCE IMAGES
  // ----------------------------------------------

  const [selectedImages, setSelectedImages] = (
    useState([])
  )

  const [previewUrls, setPreviewUrls] = (
    useState([])
  )

  const [result, setResult] = (
    useState(null)
  )

  const [isAnalyzing, setIsAnalyzing] = (
    useState(false)
  )

  const [isDownloadingReport, setIsDownloadingReport] = (
    useState(false)
  )

  const [error, setError] = (
    useState(null)
  )


  // ----------------------------------------------
  // ATTENDANCE HISTORY
  // ----------------------------------------------

  const [history, setHistory] = (
    useState([])
  )

  const [historyDate, setHistoryDate] = (
    useState("")
  )

  const [isLoadingHistory, setIsLoadingHistory] = (
    useState(false)
  )

  const [historyError, setHistoryError] = (
    useState(null)
  )


  // ----------------------------------------------
  // STUDENT MANAGEMENT
  // ----------------------------------------------

  const [students, setStudents] = (
    useState([])
  )

  const [isLoadingStudents, setIsLoadingStudents] = (
    useState(false)
  )

  const [studentsError, setStudentsError] = (
    useState(null)
  )


  // ----------------------------------------------
  // ADD STUDENT
  // ----------------------------------------------

  const [newStudentId, setNewStudentId] = (
    useState("")
  )

  const [studentImages, setStudentImages] = (
    useState([])
  )

  const [isAddingStudent, setIsAddingStudent] = (
    useState(false)
  )

  const [studentMessage, setStudentMessage] = (
    useState(null)
  )

  const [studentError, setStudentError] = (
    useState(null)
  )


  // ----------------------------------------------
  // IMAGE SELECTION
  // ----------------------------------------------

  function handleImageChange(event) {

    const files = Array.from(
      event.target.files
    )

    if (files.length === 0) {
      return
    }


    // Remove old preview URLs
    previewUrls.forEach(
      (url) => URL.revokeObjectURL(url)
    )


    setSelectedImages(
      files
    )


    const urls = files.map(
      (file) => URL.createObjectURL(file)
    )


    setPreviewUrls(
      urls
    )


    // Clear previous result
    setResult(null)

    setError(null)

  }


  // ----------------------------------------------
  // ANALYZE CLASSROOM IMAGES
  // ----------------------------------------------

  async function handleAnalyze() {

    if (
      selectedImages.length === 0
    ) {
      return
    }


    setIsAnalyzing(
      true
    )

    setError(
      null
    )

    setResult(
      null
    )


    try {

      const formData = new FormData()


      selectedImages.forEach(
        (image) => {

          formData.append(
            "images",
            image
          )

        }
      )


      const response = await fetch(
        `${API_URL}/attendance/multiple`,
        {
          method: "POST",
          body: formData,
        }
      )


      const data = await response.json()


      console.log(
        "API Response:",
        data
      )


      if (!response.ok) {

        throw new Error(
          data.detail ||
          "Failed to analyze classroom images."
        )

      }


      setResult(
        data
      )


    } catch (error) {

      console.error(
        "Analysis error:",
        error
      )


      setError(
        error.message
      )


    } finally {

      setIsAnalyzing(
        false
      )

    }

  }


  // ----------------------------------------------
  // DOWNLOAD PDF ATTENDANCE REPORT
  // ----------------------------------------------

  async function handleDownloadReport() {

    setIsDownloadingReport(
      true
    )

    setError(
      null
    )


    try {

      const response = await fetch(
        `${API_URL}/attendance/report/latest`
      )


      if (!response.ok) {

        let message = (
          "Failed to generate attendance report."
        )


        try {

          const data = await response.json()

          message = (
            data.detail ||
            message
          )

        } catch {
          // Keep the default error message.
        }


        throw new Error(
          message
        )
      }


      const pdfBlob = await response.blob()


      const contentDisposition = (
        response.headers.get(
          "content-disposition"
        )
      )


      let fileName = (
        "attendance_report.pdf"
      )


      const fileNameMatch = (
        contentDisposition?.match(
          /filename="?([^";]+)"?/
        )
      )


      if (fileNameMatch?.[1]) {

        fileName = (
          fileNameMatch[1]
        )
      }


      const downloadUrl = (
        URL.createObjectURL(
          pdfBlob
        )
      )


      const link = (
        document.createElement(
          "a"
        )
      )


      link.href = (
        downloadUrl
      )

      link.download = (
        fileName
      )


      document.body.appendChild(
        link
      )


      link.click()


      document.body.removeChild(
        link
      )


      URL.revokeObjectURL(
        downloadUrl
      )


    } catch (error) {

      console.error(
        "PDF download error:",
        error
      )


      setError(
        error.message
      )


    } finally {

      setIsDownloadingReport(
        false
      )
    }
  }


  // ----------------------------------------------
  // LOAD ATTENDANCE HISTORY
  // ----------------------------------------------

  async function handleLoadHistory() {

    setIsLoadingHistory(
      true
    )

    setHistoryError(
      null
    )


    try {

      let url = (
        `${API_URL}/attendance/history`
      )


      if (historyDate) {

        url += (
          `?date=${historyDate}`
        )

      }


      const response = await fetch(
        url
      )


      const data = await response.json()


      if (!response.ok) {

        throw new Error(
          data.detail ||
          "Failed to load attendance history."
        )

      }


      setHistory(
        data.records || []
      )


    } catch (error) {

      console.error(
        "History error:",
        error
      )


      setHistoryError(
        error.message
      )


    } finally {

      setIsLoadingHistory(
        false
      )

    }

  }


  // ----------------------------------------------
  // LOAD STUDENTS
  // ----------------------------------------------

  async function handleLoadStudents() {

    setIsLoadingStudents(
      true
    )

    setStudentsError(
      null
    )


    try {

      const response = await fetch(
        `${API_URL}/students`
      )


      const data = await response.json()


      if (!response.ok) {

        throw new Error(
          data.detail ||
          "Failed to load students."
        )

      }


      setStudents(
        data.students || []
      )


    } catch (error) {

      console.error(
        "Students error:",
        error
      )


      setStudentsError(
        error.message
      )


    } finally {

      setIsLoadingStudents(
        false
      )

    }

  }


  // ----------------------------------------------
  // ADD STUDENT
  // ----------------------------------------------

  async function handleAddStudent(
    event
  ) {

    event.preventDefault()


    setStudentError(
      null
    )

    setStudentMessage(
      null
    )


    if (!newStudentId.trim()) {

      setStudentError(
        "Please enter a student ID."
      )

      return

    }


    if (
      studentImages.length === 0
    ) {

      setStudentError(
        "Please select at least one reference image."
      )

      return

    }


    setIsAddingStudent(
      true
    )


    try {

      const formData = new FormData()


      formData.append(
        "student_id",
        newStudentId.trim()
      )


      studentImages.forEach(
        (image) => {

          formData.append(
            "images",
            image
          )

        }
      )


      const response = await fetch(
        `${API_URL}/students`,
        {
          method: "POST",
          body: formData
        }
      )


      const data = await response.json()


      if (!response.ok) {

        throw new Error(
          data.detail ||
          "Failed to add student."
        )

      }


      setStudentMessage(
        `${data.student_id} was added successfully.`
      )


      setNewStudentId(
        ""
      )


      setStudentImages(
        []
      )


      await handleLoadStudents()


    } catch (error) {

      setStudentError(
        error.message
      )


    } finally {

      setIsAddingStudent(
        false
      )

    }

  }


  // ----------------------------------------------
  // DELETE STUDENT
  // ----------------------------------------------

  async function handleDeleteStudent(
    studentId
  ) {

    const confirmed = window.confirm(
      `Are you sure you want to delete ${studentId}?`
    )


    if (!confirmed) {
      return
    }


    setStudentsError(
      null
    )


    try {

      const response = await fetch(
        `${API_URL}/students/${studentId}`,
        {
          method: "DELETE"
        }
      )


      const data = await response.json()


      if (!response.ok) {

        throw new Error(
          data.detail ||
          "Failed to delete student."
        )

      }


      setStudentMessage(
        `${studentId} was deleted successfully.`
      )


      await handleLoadStudents()


    } catch (error) {

      setStudentsError(
        error.message
      )

    }

  }


  // ----------------------------------------------
  // LOGOUT
  // ----------------------------------------------

  function handleLogout() {

    setUser(
      null
    )

  }


  // ----------------------------------------------
  // LOGIN CHECK
  // ----------------------------------------------

  if (!user) {

    return (

      <Login
        onLogin={setUser}
      />

    )

  }


  // ----------------------------------------------
  // MAIN APPLICATION
  // ----------------------------------------------

  return (

    <div className="app">


      {/* HEADER */}

      <header className="header">

        <div>

          <h1>
            ClassSense
          </h1>

          <p>
            AI-Powered Classroom Attendance System
          </p>

        </div>


        <div className="header-right">

          <div className="logged-user">

            <strong>
              {user.username}
            </strong>

            <span>
              {user.role}
            </span>

          </div>


          <div className="status">

            <span></span>

            AI System Ready

          </div>


          <button
            className="logout-button"
            onClick={handleLogout}
          >

            Logout

          </button>

        </div>

      </header>


      <main className="main-container">


        {/* HERO */}

        <section className="hero-section">

          <h2>

            Smart Attendance.

            <br />

            Powered by AI.

          </h2>


          <p>

            Upload one or multiple classroom images and let
            ClassSense automatically detect and recognize
            enrolled students.

          </p>

        </section>


        {/* UPLOAD */}

        <section className="upload-section">

          <label
            className="upload-box"
            htmlFor="image-upload"
          >

            <div className="upload-icon">
              ↑
            </div>


            <h3>
              Upload Classroom Images
            </h3>


            <p>

              Select one or multiple classroom images
              for AI-powered attendance analysis.

            </p>


            <span className="browse-button">

              Browse Images

            </span>


            <input
              id="image-upload"
              type="file"
              accept="image/*"
              multiple
              onChange={handleImageChange}
            />

          </label>


          {selectedImages.length > 0 && (

            <div className="selected-file">

              <strong>
                Selected:
              </strong>

              {" "}

              {selectedImages.length}

              {" "}

              image(s)

            </div>

          )}


          <button
            className="analyze-button"
            disabled={
              selectedImages.length === 0 ||
              isAnalyzing
            }
            onClick={handleAnalyze}
          >

            {isAnalyzing
              ? "Analyzing Classroom..."
              : "Analyze Classroom"
            }

          </button>


          {error && (

            <div className="error-message">

              {error}

            </div>

          )}

        </section>


        {/* IMAGE PREVIEWS */}

        {previewUrls.length > 0 && (

          <section className="preview-section">

            <h2>
              Selected Classroom Images
            </h2>


            <div className="preview-grid">

              {previewUrls.map(
                (url, index) => (

                  <div
                    className="preview-card"
                    key={url}
                  >

                    <img
                      src={url}
                      alt={`Selected classroom ${index + 1}`}
                      className="preview-image"
                    />

                    <p>

                      {selectedImages[index]?.name}

                    </p>

                  </div>

                )
              )}

            </div>

          </section>

        )}


        {/* ATTENDANCE RESULTS */}

        {result && (

          <section className="results-section">

            <h2>
              Attendance Results
            </h2>


            <div className="stats-grid">


              <div className="stat-card">

                <span>
                  Total Enrolled
                </span>

                <strong>
                  {result.total_enrolled ?? 0}
                </strong>

              </div>


              <div className="stat-card">

                <span>
                  Present
                </span>

                <strong>
                  {result.recognized_students?.length ?? 0}
                </strong>

              </div>


              <div className="stat-card">

                <span>
                  Absent
                </span>

                <strong>
                  {result.absent_students?.length ?? 0}
                </strong>

              </div>


              <div className="stat-card">

                <span>
                  Unknown Faces
                </span>

                <strong>
                  {result.unknown_faces ?? 0}
                </strong>

              </div>

            </div>


            <button
              className="analyze-button"
              onClick={handleDownloadReport}
              disabled={isDownloadingReport}
            >

              {isDownloadingReport
                ? "Preparing PDF Report..."
                : "Download PDF Report"
              }

            </button>


            {/* COMPLETE ATTENDANCE TABLE */}

            <div className="attendance-table-section">

              <h3>
                Complete Attendance
              </h3>


              <div className="table-wrapper">

                <table className="attendance-table">

                  <thead>

                    <tr>

                      <th>
                        Student ID
                      </th>

                      <th>
                        Attendance Status
                      </th>

                    </tr>

                  </thead>


                  <tbody>

                    {result.recognized_students?.map(
                      (student) => (

                        <tr key={`present-${student}`}>

                          <td>
                            {student}
                          </td>

                          <td>

                            <span className="present-status">

                              Present

                            </span>

                          </td>

                        </tr>

                      )
                    )}


                    {result.absent_students?.map(
                      (student) => (

                        <tr key={`absent-${student}`}>

                          <td>
                            {student}
                          </td>

                          <td>

                            <span className="absent-status">

                              Absent

                            </span>

                          </td>

                        </tr>

                      )
                    )}

                  </tbody>

                </table>

              </div>

            </div>


            {/* AI PROCESSED IMAGES */}

            {result.processed_images?.length > 0 && (

              <section className="processed-images-section">

                <h3>
                  AI Recognition Results
                </h3>


                <div className="processed-images-grid">

                  {result.processed_images.map(
                    (imageResult, index) => (

                      <div
                        className="processed-image-card"
                        key={`${imageResult.image_name}-${index}`}
                      >

                        <h4>
                          {imageResult.image_name}
                        </h4>


                        <img
                          src={
                            `${API_URL}${imageResult.result_image}`
                          }
                          alt={
                            `Recognition result for ${imageResult.image_name}`
                          }
                          className="result-image"
                        />


                        <div className="image-result-details">

                          <p>

                            <strong>
                              Faces Detected:
                            </strong>

                            {" "}

                            {imageResult.faces_detected}

                          </p>


                          <p>

                            <strong>
                              Recognized:
                            </strong>

                            {" "}

                            {
                              imageResult
                                .recognized_students
                                ?.length ?? 0
                            }

                          </p>


                          <p>

                            <strong>
                              Unknown Faces:
                            </strong>

                            {" "}

                            {imageResult.unknown_faces}

                          </p>

                        </div>

                      </div>

                    )
                  )}

                </div>

              </section>

            )}

          </section>

        )}


        {/* STUDENT MANAGEMENT */}

        <section className="students-section">

          <div className="students-header">

            <div>

              <h2>
                Student Management
              </h2>

              <p>

                View and manage students enrolled
                in the recognition system.

              </p>

            </div>


            <button
              className="secondary-button"
              onClick={handleLoadStudents}
              disabled={isLoadingStudents}
            >

              {isLoadingStudents
                ? "Loading..."
                : "Load Students"
              }

            </button>

          </div>


          {/* ADD STUDENT */}

          <form
            className="add-student-form"
            onSubmit={handleAddStudent}
          >

            <h3>
              Add New Student
            </h3>


            <input
              type="text"
              placeholder="Student ID (example: BU003)"
              value={newStudentId}
              onChange={(event) =>
                setNewStudentId(
                  event.target.value
                )
              }
            />


            <label className="student-image-input">

              Select Reference Images

              <input
                type="file"
                accept="image/*"
                multiple
                onChange={(event) =>
                  setStudentImages(
                    Array.from(
                      event.target.files
                    )
                  )
                }
              />

            </label>


            {studentImages.length > 0 && (

              <p className="file-count">

                {studentImages.length} image(s) selected

              </p>

            )}


            <button
              className="analyze-button"
              disabled={isAddingStudent}
              type="submit"
            >

              {isAddingStudent
                ? "Adding Student..."
                : "Add Student"
              }

            </button>

          </form>


          {studentMessage && (

            <div className="success-message">

              {studentMessage}

            </div>

          )}


          {studentError && (

            <div className="error-message">

              {studentError}

            </div>

          )}


          {studentsError && (

            <div className="error-message">

              {studentsError}

            </div>

          )}


          {students.length > 0 && (

            <div className="students-grid">

              {students.map(
                (student) => (

                  <div
                    className="student-card"
                    key={student}
                  >

                    <div className="student-avatar">

                      {student.charAt(0)}

                    </div>


                    <div className="student-info">

                      <strong>
                        {student}
                      </strong>

                      <p>
                        Enrolled Student
                      </p>

                    </div>


                    <button
                      className="delete-button"
                      onClick={() =>
                        handleDeleteStudent(
                          student
                        )
                      }
                    >

                      Delete

                    </button>

                  </div>

                )
              )}

            </div>

          )}


          {!isLoadingStudents &&
            students.length === 0 &&
            !studentsError && (

              <p className="no-students">

                Click "Load Students" to view
                enrolled students.

              </p>

            )}

        </section>


        {/* ATTENDANCE HISTORY */}

        <section className="history-section">

          <div className="history-header">

            <div>

              <h2>
                Attendance History
              </h2>

              <p>

                View previously saved attendance
                sessions.

              </p>

            </div>

          </div>


          <div className="history-controls">

            <input
              type="date"
              value={historyDate}
              onChange={(event) =>
                setHistoryDate(
                  event.target.value
                )
              }
            />


            <button
              className="history-button"
              onClick={handleLoadHistory}
              disabled={isLoadingHistory}
            >

              {isLoadingHistory
                ? "Loading..."
                : "Load History"
              }

            </button>


            {historyDate && (

              <button
                className="clear-button"
                onClick={() => {

                  setHistoryDate("")

                  setHistory([])

                }}
              >

                Clear Filter

              </button>

            )}

          </div>


          {historyError && (

            <div className="error-message">

              {historyError}

            </div>

          )}


          {history.length > 0 && (

            <div className="history-grid">

              {history.map(
                (record, index) => (

                  <div
                    className="history-card"
                    key={
                      record.id ||
                      `${record.timestamp}-${index}`
                    }
                  >

                    <h3>
                      Attendance Session
                    </h3>


                    <p className="history-time">

                      {new Date(
                        record.timestamp
                      ).toLocaleString()}

                    </p>


                    <p className="history-image">

                      Image:

                      {" "}

                      <strong>

                        {record.image_name}

                      </strong>

                    </p>


                    <div className="history-stats">


                      <div>

                        <span>
                          Total
                        </span>

                        <strong>

                          {record.total_enrolled}

                        </strong>

                      </div>


                      <div>

                        <span>
                          Present
                        </span>

                        <strong>

                          {
                            record
                              .present_students
                              ?.length ?? 0
                          }

                        </strong>

                      </div>


                      <div>

                        <span>
                          Absent
                        </span>

                        <strong>

                          {
                            record
                              .absent_students
                              ?.length ?? 0
                          }

                        </strong>

                      </div>


                      <div>

                        <span>
                          Unknown
                        </span>

                        <strong>

                          {record.unknown_faces}

                        </strong>

                      </div>

                    </div>

                  </div>

                )
              )}

            </div>

          )}


          {!isLoadingHistory &&
            history.length === 0 &&
            !historyError && (

              <p className="no-history">

                {historyDate
                  ? "No attendance records were found for this date."
                  : "Click Load History to view saved attendance records."
                }

              </p>

            )}

        </section>

      </main>

    </div>

  )

}


export default App
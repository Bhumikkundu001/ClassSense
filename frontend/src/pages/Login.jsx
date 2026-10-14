import { useState } from "react"

import "./Login.css"


const API_URL = "http://127.0.0.1:8000"


function Login({ onLogin }) {

  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")

  const [isLoading, setIsLoading] = (
    useState(false)
  )

  const [error, setError] = (
    useState(null)
  )


  async function handleLogin(event) {

    event.preventDefault()


    if (
      !username.trim() ||
      !password.trim()
    ) {

      setError(
        "Please enter your username and password."
      )

      return
    }


    setIsLoading(true)

    setError(null)


    try {

      const response = await fetch(
        `${API_URL}/auth/login`,
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json"
          },

          body: JSON.stringify({
            username: username.trim(),
            password: password
          })
        }
      )


      const data = await response.json()


      if (!response.ok) {

        throw new Error(
          data.detail ||
          "Login failed."
        )
      }


      // Send logged-in user data to App.jsx
      onLogin(data)


    } catch (error) {

      setError(
        error.message ||
        "Unable to connect to the server."
      )

    } finally {

      setIsLoading(false)

    }

  }


  return (

    <div className="login-page">

      <div className="login-card">

        <div className="login-header">

          <h1>
            ClassSense
          </h1>

          <p>
            AI-Powered Classroom Attendance
          </p>

        </div>


        <form
          className="login-form"
          onSubmit={handleLogin}
        >

          <label>
            Username
          </label>

          <input
            type="text"
            placeholder="Enter your username"
            value={username}
            onChange={
              (event) =>
                setUsername(
                  event.target.value
                )
            }
          />


          <label>
            Password
          </label>

          <input
            type="password"
            placeholder="Enter your password"
            value={password}
            onChange={
              (event) =>
                setPassword(
                  event.target.value
                )
            }
          />


          {error && (

            <div className="login-error">

              {error}

            </div>

          )}


          <button
            type="submit"
            disabled={isLoading}
          >

            {
              isLoading
                ? "Logging in..."
                : "Login"
            }

          </button>

        </form>


      </div>

    </div>

  )

}


export default Login
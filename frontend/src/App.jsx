import { useState, useEffect } from 'react'
import './App.css'

const API_URL = 'http://localhost:8000/'

function App() {
  const [message, setMessage] = useState('')

  useEffect(() => {
    fetch(API_URL)
      .then(response => response.json())
      .then(data => setMessage(data.message))
  }, [])

  return (
    <div>
      <header>
        <h1 className='text-blue-400 pb-2 font-m-plus font-light'>Welcome to Osusume!</h1>
        <h2 className='text-blue-300 pb-5 font-m-plus font-light text-3xl'>お勧めへようこそ!</h2>
        <text className='text-gray-600'>{message}</text>
      </header>
    </div>
  )
}

export default App

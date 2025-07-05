import { useState } from 'react'
import './App.css'

const API_URL = 'http://localhost:8000/'

function App() {
  const [query, setQuery]         = useState('')
  const [message, setMessage]     = useState('')
  const [isLoading, setIsLoading] = useState(false)
  
  const handleChange = (event) => {             // Called every time the user types in the text area to update the value of the query
    setQuery(event.target.value);
  };

  const handleSubmit = async (event) => {       // Called every time the user clicks on the "Submit" button
    event.preventDefault()                      // Prevents the page from reloading when submitting the form
    setIsLoading(true)                          // Updates loading state to disable the button and textarea
    console.log(query)                          // TODO : debug, to remove
    try{
      const response = await fetch(API_URL)     // Async call to the API
      const data = await response.json()
      setMessage(data.message)
    }  catch(error) {
      console.error('Error fetching API:', error)
      setMessage('Oops, something went wrong... Try again!')
    } finally {
      setIsLoading(false)                       // Updates loading state to enable the button and textarea again
      setQuery("")                              // Resets the textarea content
      console.log(message)                      // TODO : debug, to remove
    }
  };

  return (
    <div>
      <header>
        <h1 className='text-blue-400 pb-2 font-m-plus font-light'>Welcome to Osusume!</h1>
        <h2 className='text-blue-300 font-m-plus font-light text-3xl'>お勧めへようこそ!</h2>
      </header>
      
      <form onSubmit={handleSubmit}>
        <div className='m-5'>
        <textarea
          rows="5"
          value={query}
          onChange={handleChange}
          disabled={isLoading}
          className="w-4xl p-5 border resize-none border-gray-300 rounded-3xl shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-300 text-gray-600 "
          placeholder="What would you like to be recommended?"
          >
        </textarea>
      </div>

      <div>
        <button
          type="submit"
          className={`w-25 px-4 py-2 text-white rounded-3xl ${isLoading ? 'bg-gray-400 cursor-not-allowed' : 'bg-blue-500 hover:bg-blue-700'}`}
        >
          {isLoading ? 'Loading...' : 'Submit'}
        </button>
      </div>

      </form>

      <div className='p-4'>
        <p className='text-gray-600'>{message}</p> 
      </div>
     
    </div>
  )
}

export default App

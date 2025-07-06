
import './App.css'
import QueryForm from './components/QueryForm';


function App() {
  return (
    <div>
        
      <header>
        <h1 className='text-blue-400 pb-2 font-m-plus font-light'>Welcome to Osusume!</h1>
        <h2 className='text-blue-300 font-m-plus font-light text-3xl'>お勧めへようこそ!</h2>
      </header>

      <QueryForm />
      
    </div>
  )
}

export default App

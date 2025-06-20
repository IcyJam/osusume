import React, { useEffect, useState } from 'react';

const API_URL = 'http://localhost:8000/'

const App = () => {
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetch(API_URL)
      .then(response => response.json())
      .then(data => setMessage(data.message));
  }, []);

  return (
    <div>
      <header>
        <h1>Welcome to Osusume!</h1>
        <h2>Message from API: {message}</h2>
      </header>
    </div>
  );
};

export default App;

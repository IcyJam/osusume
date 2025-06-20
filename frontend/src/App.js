import React, { useEffect, useState } from 'react';

const BASE_URL = 'http://0.0.0.0:8000/'

const App = () => {
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetch(BASE_URL)
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

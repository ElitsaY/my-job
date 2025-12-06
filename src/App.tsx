import React from 'react';
import InternshipsTable from './components/InternshipsTable';
import { internshipData } from './data/internshipData';

const App: React.FC = () => {
  return (
    <div className="App">
      <InternshipsTable data={internshipData} />
    </div>
  );
};

export default App;
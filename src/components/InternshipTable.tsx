import React from 'react';
import { Internship } from '../data/internshipData';

interface InternshipsTableProps {
  data: readonly Internship[];
}


const InternshipsTable: React.FC<InternshipsTableProps> = ({ data }) => {
  if (data.length === 0) {
    return <p> No internship data available.</p>;
  }

  return (
    <div style={{ padding: '20px' }}>
      <h1>Available Internships (2026)</h1>
      <table 
        style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}
      >
        <thead>
          <tr style={{ borderBottom: '2px solid #ccc' }}>
            <th style={{ padding: '10px 0', width: '80%' }}>Job Title</th>
            <th style={{ padding: '10px 0', width: '20%' }}>Link</th>
          </tr>
        </thead>
        <tbody>
          {data.map((internship, index) => (
            <tr key={index} style={{ borderBottom: '1px solid #eee' }}>
              <td style={{ padding: '10px 0' }}>
                title=internship.title
              </td>
              <td style={{ padding: '10px 0' }}>
                <a 
                  href={internship.url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  style={{ color: '#007bff', textDecoration: 'none' }}
                >
                  Apply
                </a>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default InternshipsTable;
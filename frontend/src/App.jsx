import { useEffect, useState } from "react";
import "./index.css";

function App() {
  const [results, setResults] = useState([]);

  useEffect(() => {
    fetch("http://localhost:8000/api/results")
      .then((res) => res.json())
      .then((data) => {
        console.log("Fetched results:", data); // ✅ Debug
        setResults(data);
      })
      .catch((err) => console.error("Failed to fetch data:", err));
  }, []);

  return (
    <div>
      <h1>🧠 HackerNews Snapshot</h1>
      <div className="grid">
        {results.map((item, i) => (
          <div key={i} className="card">
            <h2>{item.title}</h2>
            <a href={item.url} target="_blank" rel="noopener noreferrer">
              {item.url}
            </a>
            {item.status === "success" ? (
              <img
                src={`http://localhost:8000/${item.screenshot}`}
                alt={item.title}
              />
            ) : (
              <div className="placeholder">
                Preview unavailable — site uses custom graphics
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;

import { useEffect, useState } from "react";
import "./index.css";

function App() {
  const [results, setResults] = useState([]);

  useEffect(() => {
    fetch("http://localhost:8000/api/results")
      .then((res) => res.json())
      .then((data) => {
        console.log("Fetched results:", data);
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
                src={`http://localhost:8000/screenshots/${item.screenshot
                  .split("/")
                  .pop()}`}
                alt={item.title}
                style={{
                  width: "100%",
                  borderRadius: "8px",
                  marginTop: "0.5rem",
                }}
              />
            ) : (
              <div className="placeholder">
                Preview unavailable — site uses custom graphics
              </div>
            )}
            <p style={{ marginTop: "0.5rem", color: "#ccc" }}>{item.summary}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;

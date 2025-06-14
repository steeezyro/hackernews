import { useEffect, useState } from "react";
import "./index.css";

function App() {
  const [results, setResults] = useState([]);

  useEffect(() => {
    fetch("http://localhost:8000/api/results")
      .then((res) => res.json())
      .then((data) => setResults(data))
      .catch((err) => console.error("Failed to fetch data:", err));
  }, []);

  const speak = (text) => {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1; // Adjust speed (0.1 to 10)
    utterance.pitch = 1; // Adjust pitch (0 to 2)
    speechSynthesis.speak(utterance);
  };

  return (
    <div>
      <h1>HackerNews Snapshot 📈</h1>
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
            <p>{item.summary}</p>
            <button
              onClick={() => speak(item.summary)}
              style={{ marginTop: "0.5rem" }}
            >
              🔊 Play Summary
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;

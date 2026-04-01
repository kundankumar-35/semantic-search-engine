import { useState } from 'react';

export default function App() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]); // This will now hold the Array(10)
  const [loading, setLoading] = useState(false);
  const [searchStats, setSearchStats] = useState(null);

  const handleSearch = async () => {
    if (!query.trim()) return;
    
    console.log("1. Search Started for:", query);
    setLoading(true);
    setResults([]); // Clear previous results
    
    try {
      const url = `http://127.0.0.1:8000/search?q=${encodeURIComponent(query)}`;
      console.log("2. Fetching from:", url);
      
      const response = await fetch(url);
      const data = await response.json();
      
      console.log("3. Raw Data received:", data);

      // KEY FIX: Extract the 'results' array from the backend object
      if (data && data.results) {
        setResults(data.results);
        setSearchStats({
          latency: data.latency_ms,
          total: data.total_hits,
          method: data.method
        });
      } else {
        console.warn("Data format unexpected or results empty");
        setResults([]);
      }

    } catch (error) {
      console.error("4. FETCH ERROR:", error);
      alert("Backend server is not responding. Check your Python terminal!");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gray-900 text-slate-100 p-4 md:p-8 font-sans">
      <div className="max-w-4xl mx-auto">
        {/* Header Section */}
        <header className="text-center mb-12">
          <h1 className="text-5xl font-black mb-4 bg-gradient-to-r from-blue-500 to-cyan-400 bg-clip-text text-transparent">
            Semantic Engine
          </h1>
          <p className="text-gray-400">Querying 50,000 vectors via FAISS & AI</p>
        </header>

        {/* Search Bar Container */}
        <div className="flex flex-col md:flex-row gap-3 mb-8">
          <input
            type="text"
            className="flex-1 p-4 rounded-xl bg-gray-800 border border-gray-700 focus:ring-2 focus:ring-blue-500 outline-none text-lg transition-all shadow-2xl"
            placeholder="Describe what you're looking for..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
          />
          <button 
            onClick={handleSearch}
            disabled={loading}
            className="bg-blue-600 hover:bg-blue-500 disabled:bg-gray-700 px-10 py-4 rounded-xl font-bold transition-all shadow-lg active:scale-95"
          >
            {loading ? (
              <span className="flex items-center gap-2">
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                Searching...
              </span>
            ) : "Search"}
          </button>
        </div>

        {/* Stats Bar */}
        {searchStats && !loading && (
          <div className="mb-6 flex gap-4 text-xs font-mono text-gray-500 uppercase tracking-widest justify-center">
            <span>Latency: {searchStats.latency}ms</span>
            <span>|</span>
            <span>Hits: {searchStats.total}</span>
            <span>|</span>
            <span>Method: {searchStats.method}</span>
          </div>
        )}

        {/* Results Area */}
<div className="space-y-6 mt-8">
  {results && results.length > 0 ? (
    results.map((item, index) => (
      <div 
        key={index} 
        className="p-6 bg-gray-800 rounded-xl border border-gray-700 shadow-lg hover:border-blue-500 transition-all group"
      >
        {/* Title and Score Row */}
        <div className="flex justify-between items-start mb-2">
          <h3 className="text-xl font-bold text-blue-400 group-hover:text-blue-300">
            {item.title}
          </h3>
          <span className="text-xs font-mono bg-blue-900/30 text-blue-400 px-2 py-1 rounded">
            Score: {item.score?.toFixed(4)}
          </span>
        </div>

        {/* Snippet / Description */}
        <p className="text-gray-300 leading-relaxed mb-4">
          {item.snippet}
        </p>

        {/* URL and Doc ID Footer */}
        <div className="flex justify-between items-center border-t border-gray-700 pt-4 text-xs">
          <a 
            href={item.url} 
            target="_blank" 
            rel="noopener noreferrer" 
            className="text-cyan-500 hover:underline flex items-center gap-1"
          >
            Read more on Wikipedia →
          </a>
          <span className="text-gray-500 font-mono">
            DOC_ID: {item.doc_id}
          </span>
        </div>
      </div>
    ))
  ) : (
    !loading && <p className="text-center text-gray-500">No results to display yet.</p>
  )}
</div>
      </div>
    </main>
  );
}
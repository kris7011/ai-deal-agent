import { useState } from "react";
import "./App.css";
import ProductCard from "./components/ProductCard";
import type { ProductResult, SearchRequirements } from "./types";
import { searchProductsApi } from "./api";

function App() {
  const [query, setQuery] = useState("");
  const [products, setProducts] = useState<ProductResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [allowLiveSearch, setAllowLiveSearch] = useState(false);
  const [usedCache, setUsedCache] = useState<boolean | null>(null);
  const [requirements, setRequirements] = useState<SearchRequirements | null>(null);

  const exampleQueries = [
    "robotstøvsuger med moppe og høj sugeevne",
    "laptop til programmering med 16GB RAM under 8000 kr",
    "vandtæt vinterjakke til herre under 1500 kr",
  ];

  async function searchProducts() {
    if (!query.trim()) {
      setError("Skriv hvad du leder efter først.");
      return;
    }

    setError(null);
    setLoading(true);
    setProducts([]);
    setUsedCache(null);
    setRequirements(null);

    try {
      const data = await searchProductsApi(query, allowLiveSearch);
      setProducts(data.products);
      setUsedCache(data.used_cache);
      setRequirements(data.requirements);
    } catch (error) {
      console.error(error);

      if (error instanceof Error) {
        setError(error.message);
      } else {
        setError("Der skete en fejl. Prøv venligst igen.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page">
      <h1>AI Deal Agent</h1>

      <div className="search-section">
        <div className="search-bar">
          <input
            type="text"
            placeholder="Søg efter produkter..."
            value={query}
            onChange={(event) => setQuery(event.target.value)}
          />

          <button onClick={searchProducts} disabled={loading}>
            {loading ? "Søger..." : "Søg"}
          </button>
        </div>

        <label className="live-search-toggle">
          <input
            type="checkbox"
            checked={allowLiveSearch}
            onChange={(event) => setAllowLiveSearch(event.target.checked)}
          />
          Tillad live-søgning hvis cache mangler
        </label>

        {error && <p className="error-message">{error}</p>}

        {usedCache !== null && (
          <p className="search-source">
            {usedCache
              ? "Resultater hentet fra cache. Ingen SerpAPI-søgning brugt."
              : "Ny live-søgning udført og gemt i cache."}
          </p>
        )}
      </div>

      {requirements && (
        <div className="requirements-summary">
          <p>
            <strong>Agenten forstod søgningen som:</strong>
          </p>
          <p>Produkt: {requirements.product_type}</p>
          <p>
            Makspris:{" "}
            {requirements.max_price
              ? `${requirements.max_price} kr.`
              : "Ikke angivet"}
          </p>
          <p>
            Krav:{" "}
            {requirements.required_features.length > 0
              ? requirements.required_features.join(", ")
              : "Ingen specifikke krav fundet"}
          </p>
        </div>
      )}

      {products.length === 0 && !loading && !error && (
        <div className="empty-state">
          <h2>Hvad leder du efter?</h2>
          <p>
            Skriv et produkt og dine krav. Agenten forsøger at finde relevante produkter,
            score dem og forklare hvorfor de matcher.
          </p>

          <div className="example-queries">
            {exampleQueries.map((example) => (
              <button
                key={example}
                type="button"
                onClick={() => setQuery(example)}
              >
                {example}
              </button>
            ))}
          </div>
        </div>
      )}

      {loading && <p>Loader...</p>}

      <div className="product-grid">
        {products.map((item) => (
          <ProductCard key={item.product.url} item={item} />
        ))}
      </div>
    </div>
  );
}

export default App;
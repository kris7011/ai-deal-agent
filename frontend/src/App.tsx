import { useState } from "react";
import "./App.css";
import SearchSection from "./components/SearchSection";
import RequirementsSummary from "./components/RequirementsSummary";
import EmptyState from "./components/EmptyState";
import ProductGrid from "./components/ProductGrid";
import type { ProductResult, SearchRequirements } from "./types";
import { saveSearchApi, searchProductsApi } from "./api";

function App() {
  const [query, setQuery] = useState("");
  const [products, setProducts] = useState<ProductResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [allowLiveSearch, setAllowLiveSearch] = useState(false);
  const [usedCache, setUsedCache] = useState<boolean | null>(null);
  const [requirements, setRequirements] = useState<SearchRequirements | null>(null);
  const [resultCount, setResultCount] = useState(0);
  const [saveMessage, setSaveMessage] = useState<string | null>(null);

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
    setResultCount(0);
    setSaveMessage(null);

    try {
      const data = await searchProductsApi(query, allowLiveSearch);
      setProducts(data.products);
      setUsedCache(data.used_cache);
      setRequirements(data.requirements);
      setResultCount(data.count);
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

  async function saveCurrentSearch() {
    if (!query.trim() || products.length === 0) {
      return;
    }

    const bestScore = products[0]?.score ?? 0;

    try {
      await saveSearchApi(query, resultCount, bestScore);
      setSaveMessage("Søgningen er gemt.");
    } catch (error) {
      console.error(error);

      if (error instanceof Error) {
        setSaveMessage(error.message);
      } else {
        setSaveMessage("Kunne ikke gemme søgningen.");
      }
    }
  }

  return (
    <div className="page">
      <h1>AI Deal Agent</h1>

      <SearchSection
        query={query}
        loading={loading}
        error={error}
        allowLiveSearch={allowLiveSearch}
        usedCache={usedCache}
        onQueryChange={setQuery}
        onAllowLiveSearchChange={setAllowLiveSearch}
        onSearch={searchProducts}
      />

      {requirements && <RequirementsSummary requirements={requirements} />}

      {products.length > 0 && (
        <div className="save-search-section">
          <button type="button" onClick={saveCurrentSearch}>
            Gem søgning
          </button>

          {saveMessage && <p>{saveMessage}</p>}
        </div>
      )}

      {products.length === 0 && !loading && !error && (
        <EmptyState
          exampleQueries={exampleQueries}
          onExampleClick={setQuery}
        />
      )}

      {loading && <p>Loader...</p>}

      <ProductGrid products={products} />
    </div>
  );
}

export default App;
import { useState } from "react";
import "./App.css";
import ProductCard from "./components/ProductCard";
import SearchSection from "./components/SearchSection";
import RequirementsSummary from "./components/RequirementsSummary";
import EmptyState from "./components/EmptyState";
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

      {products.length === 0 && !loading && !error && (
        <EmptyState
          exampleQueries={exampleQueries}
          onExampleClick={setQuery}
        />
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
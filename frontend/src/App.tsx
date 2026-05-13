import { useEffect, useState } from "react";
import "./App.css";
import SearchSection from "./components/SearchSection";
import RequirementsSummary from "./components/RequirementsSummary";
import EmptyState from "./components/EmptyState";
import ProductGrid from "./components/ProductGrid";
import SavedSearchesPanel from "./components/SavedSearchesPanel";
import {
  deleteSavedSearchApi,
  getSavedSearchesApi,
  saveSearchApi,
  searchProductsApi,
} from "./api";
import type { ProductResult, SavedSearch, SearchRequirements } from "./types";

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
  const [savedSearches, setSavedSearches] = useState<SavedSearch[]>([]);

  const exampleQueries = [
    "robotstøvsuger med moppe og høj sugeevne",
    "laptop til programmering med 16GB RAM under 8000 kr",
    "vandtæt vinterjakke til herre under 1500 kr",
  ];

  useEffect(() => {
    loadSavedSearches();
  }, []);

  async function searchProducts(searchQuery: string = query) {
    const queryToSearch = searchQuery.trim();

    if (!queryToSearch) {
      setError("Skriv hvad du leder efter først.");
      return;
    }

    setQuery(queryToSearch);
    setError(null);
    setLoading(true);
    setProducts([]);
    setUsedCache(null);
    setRequirements(null);
    setResultCount(0);
    setSaveMessage(null);

    try {
      const data = await searchProductsApi(queryToSearch, allowLiveSearch);
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
      await loadSavedSearches();
    } catch (error) {
      console.error(error);

      if (error instanceof Error) {
        setSaveMessage(error.message);
      } else {
        setSaveMessage("Kunne ikke gemme søgningen.");
      }
    }
  }

  async function loadSavedSearches() {
    try {
      const data = await getSavedSearchesApi();
      setSavedSearches(data.saved_searches);
    } catch (error) {
      console.error(error);
    }
  }

  async function deleteSavedSearch(savedSearchId: string) {
    try {
      await deleteSavedSearchApi(savedSearchId);
      await loadSavedSearches();
    } catch (error) {
      console.error(error);
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
        onSearch={() => searchProducts()}
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

      <SavedSearchesPanel
        savedSearches={savedSearches}
        onSavedSearchClick={setQuery}
        onRunSavedSearch={searchProducts}
        onDeleteSavedSearch={deleteSavedSearch}
      />

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
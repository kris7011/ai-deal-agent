type SearchSectionProps = {
    query: string;
    loading: boolean;
    error: string | null;
    allowLiveSearch: boolean;
    usedCache: boolean | null;
    onQueryChange: (value: string) => void;
    onAllowLiveSearchChange: (value: boolean) => void;
    onSearch: () => void;
};

function SearchSection({
    query,
    loading,
    error,
    allowLiveSearch,
    usedCache,
    onQueryChange,
    onAllowLiveSearchChange,
    onSearch,
}: SearchSectionProps) {
    return (
        <div className="search-section">
            <div className="search-bar">
                <input
                    type="text"
                    placeholder="Søg efter produkter..."
                    value={query}
                    onChange={(event) => onQueryChange(event.target.value)}
                    onKeyDown={(event) => {
                        if (event.key === "Enter") {
                            onSearch();
                        }
                    }}
                />

                <button onClick={onSearch} disabled={loading}>
                    {loading ? "Søger..." : "Søg"}
                </button>
            </div>

            <label className="live-search-toggle">
                <input
                    type="checkbox"
                    checked={allowLiveSearch}
                    onChange={(event) => onAllowLiveSearchChange(event.target.checked)}
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
    );
}

export default SearchSection;
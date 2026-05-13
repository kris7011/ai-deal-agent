import type { SavedSearch } from "../types";

type SavedSearchesPanelProps = {
    savedSearches: SavedSearch[];
    onSavedSearchClick: (query: string) => void;
    onRunSavedSearch: (query: string) => void;
    onDeleteSavedSearch: (id: string) => void;
};

function SavedSearchesPanel({
    savedSearches,
    onSavedSearchClick,
    onRunSavedSearch,
    onDeleteSavedSearch,
}: SavedSearchesPanelProps) {
    if (savedSearches.length === 0) {
        return null;
    }

    const sortedSavedSearches = [...savedSearches].sort(
        (a, b) =>
            new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    );

    return (
        <div className="saved-searches-panel">
            <h2>Gemte søgninger</h2>

            <div className="saved-searches-list">
                {sortedSavedSearches.map((savedSearch) => (
                    <div key={savedSearch.id} className="saved-search-card">
                        <h3>{savedSearch.query}</h3>

                        <p className="saved-search-date">
                            Gemt: {formatDate(savedSearch.created_at)}
                        </p>

                        <p>Produkt: {savedSearch.product_type}</p>

                        <p>
                            Makspris:{" "}
                            {savedSearch.max_price
                                ? `${savedSearch.max_price} kr.`
                                : "Ikke angivet"}
                        </p>

                        <p>
                            Krav:{" "}
                            {savedSearch.required_features.length > 0
                                ? savedSearch.required_features.join(", ")
                                : "Ingen specifikke krav"}
                        </p>

                        <p>Resultater: {savedSearch.result_count}</p>
                        <p>Bedste score: {savedSearch.best_score}/100</p>

                        <div className="saved-search-actions">
                            <button
                                type="button"
                                className="saved-search-use-button"
                                onClick={() => onSavedSearchClick(savedSearch.query)}
                            >
                                Brug søgning
                            </button>

                            <button
                                type="button"
                                className="saved-search-run-button"
                                onClick={() => onRunSavedSearch(savedSearch.query)}
                            >
                                Søg igen
                            </button>

                            <button
                                type="button"
                                className="saved-search-delete-button"
                                onClick={() => onDeleteSavedSearch(savedSearch.id)}
                            >
                                Slet
                            </button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

function formatDate(value: string) {
    return new Date(value).toLocaleString("da-DK", {
        dateStyle: "short",
        timeStyle: "short",
    });
}

export default SavedSearchesPanel;
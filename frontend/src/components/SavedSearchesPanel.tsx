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
    {
        {
            if (savedSearches.length === 0) {
                return null;
            }

            return (
                <div className="saved-searches-panel">
                    <h2>Gemte søgninger</h2>

                    <div className="saved-searches-list">
                        {savedSearches.map((savedSearch) => (
                            <div
                                key={savedSearch.id}
                                className="saved-search-card"
                            >
                                <h3>{savedSearch.query}</h3>

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
                                </div>

                                <button
                                    type="button"
                                    className="saved-search-delete-button"
                                    onClick={() => onDeleteSavedSearch(savedSearch.id)}
                                >
                                    Slet
                                </button>
                            </div>
                        ))}
                    </div>
                </div>
            );
        }
    }
}

export default SavedSearchesPanel;
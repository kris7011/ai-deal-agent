import type { SavedSearch } from "../types";

type SavedSearchesPanelProps = {
    savedSearches: SavedSearch[];
    onSavedSearchClick: (query: string) => void;
};

function SavedSearchesPanel({
    savedSearches,
    onSavedSearchClick,
}: SavedSearchesPanelProps) {
    if (savedSearches.length === 0) {
        return null;
    }

    return (
        <div className="saved-searches-panel">
            <h2>Gemte søgninger</h2>

            <div className="saved-searches-list">
                {savedSearches.map((savedSearch) => (
                    <div
                        key={`${savedSearch.query}-${savedSearch.created_at}`}
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

                        <button
                            type="button"
                            className="saved-search-use-button"
                            onClick={() => onSavedSearchClick(savedSearch.query)}
                        >
                            Brug søgning
                        </button>
                    </div>
                ))}
            </div>
        </div>
    );
}

export default SavedSearchesPanel;
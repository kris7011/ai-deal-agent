type EmptyStateProps = {
    exampleQueries: string[];
    onExampleClick: (query: string) => void;
};

function EmptyState({ exampleQueries, onExampleClick }: EmptyStateProps) {
    return (
        <div className="empty-state">
            <h2>Hvad leder du efter?</h2>

            <p>
                Skriv et produkt og dine krav. Agenten forsøger at finde relevante
                produkter, score dem og forklare hvorfor de matcher.
            </p>

            <div className="example-queries">
                {exampleQueries.map((example) => (
                    <button
                        key={example}
                        type="button"
                        onClick={() => onExampleClick(example)}
                    >
                        {example}
                    </button>
                ))}
            </div>
        </div>
    );
}

export default EmptyState;
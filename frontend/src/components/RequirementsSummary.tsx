import type { SearchRequirements } from "../types";

type RequirementsSummaryProps = {
    requirements: SearchRequirements;
};

function RequirementsSummary({ requirements }: RequirementsSummaryProps) {
    return (
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
    );
}

export default RequirementsSummary;
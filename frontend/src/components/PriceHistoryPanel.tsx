import { useEffect, useState } from "react";
import { getPriceHistoryApi } from "../api";
import { formatDate, formatDateTime, formatPrice } from "../format";
import type { PriceHistory, PriceObservation } from "../types";

type PriceHistoryPanelProps = {
    productId: number;
};

const originLabels: Record<PriceObservation["origin"], string> = {
    live: "Live",
    cache: "Cache",
    demo: "Demo",
};

const CHART_WIDTH = 240;
const CHART_HEIGHT = 60;

function PriceChart({ observations }: { observations: PriceObservation[] }) {
    if (observations.length < 2) {
        return null;
    }

    const prices = observations.map((observation) => observation.price);
    const lowest = Math.min(...prices);
    const range = Math.max(...prices) - lowest || 1;

    const points = observations
        .map((observation, index) => {
            const x = (index / (observations.length - 1)) * (CHART_WIDTH - 8) + 4;
            const y = CHART_HEIGHT - 4 - ((observation.price - lowest) / range) * (CHART_HEIGHT - 8);
            return `${x.toFixed(1)},${y.toFixed(1)}`;
        })
        .join(" ");

    return (
        <svg
            className="price-chart"
            viewBox={`0 0 ${CHART_WIDTH} ${CHART_HEIGHT}`}
            role="img"
            aria-label={`Pris fra ${formatPrice(prices[0])} til ${formatPrice(prices[prices.length - 1])}`}
        >
            <polyline points={points} fill="none" stroke="currentColor" strokeWidth="2" />
        </svg>
    );
}

function PriceHistoryPanel({ productId }: PriceHistoryPanelProps) {
    const [history, setHistory] = useState<PriceHistory | null>(null);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        let active = true;

        getPriceHistoryApi(productId)
            .then((data) => active && setHistory(data))
            .catch((caught: unknown) =>
                active && setError(caught instanceof Error ? caught.message : "Kunne ikke hente prishistorikken."),
            );

        return () => {
            active = false;
        };
    }, [productId]);

    if (error) {
        return <p className="error-message">{error}</p>;
    }

    if (!history) {
        return <p className="price-history-loading">Henter prishistorik...</p>;
    }

    if (history.observations.length === 0) {
        return <p className="price-history-empty">Ingen kendte priser endnu.</p>;
    }

    return (
        <div className="price-history-panel">
            <PriceChart observations={history.observations} />
            <table className="price-history-table">
                <caption>
                    Prishistorik siden {formatDate(history.observations[0].observed_at)}
                </caption>
                <thead>
                    <tr>
                        <th scope="col">Hentet fra kilden</th>
                        <th scope="col">Pris</th>
                        <th scope="col">Kilde</th>
                    </tr>
                </thead>
                <tbody>
                    {[...history.observations].reverse().map((observation) => (
                        <tr key={`${observation.observed_at}-${observation.price}`}>
                            <td>{formatDateTime(observation.observed_at)}</td>
                            <td>{formatPrice(observation.price)}</td>
                            <td>{originLabels[observation.origin]}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}

export default PriceHistoryPanel;

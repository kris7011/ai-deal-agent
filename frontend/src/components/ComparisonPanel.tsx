import { useState } from "react";
import { compareProductsApi } from "../api";
import { formatDateTime, formatPrice } from "../format";
import type { Comparison, ComparisonHighlight } from "../types";

/** Render with key={productIds.join(",")} so a new selection starts without the old table. */
type ComparisonPanelProps = {
    productIds: number[];
    onClear: () => void;
};

const highlightLabels: Record<ComparisonHighlight, string> = {
    cheapest_now: "Billigst nu",
    best_rated: "Bedst bedømt",
    lowest_price_seen: "Laveste pris set",
};

function priceOrDash(price: number | null) {
    return price === null ? "–" : formatPrice(price);
}

function formatChange(change: number | null) {
    if (change === null || change === 0) {
        return "Uændret";
    }

    return change < 0 ? `${formatPrice(-change)} billigere` : `${formatPrice(change)} dyrere`;
}

function ComparisonPanel({ productIds, onClear }: ComparisonPanelProps) {
    const [comparison, setComparison] = useState<Comparison | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);

    async function compare() {
        setLoading(true);
        setError(null);

        try {
            setComparison(await compareProductsApi(productIds));
        } catch (caught) {
            setError(caught instanceof Error ? caught.message : "Kunne ikke sammenligne produkterne.");
        } finally {
            setLoading(false);
        }
    }

    return (
        <section className="comparison-panel" aria-label="Sammenligning">
            <div className="comparison-actions">
                <span>{productIds.length} valgt til sammenligning (2-4)</span>
                <button type="button" disabled={productIds.length < 2 || loading} onClick={compare}>
                    {loading ? "Sammenligner..." : "Sammenlign valgte"}
                </button>
                <button type="button" className="comparison-clear" onClick={onClear}>
                    Ryd valg
                </button>
            </div>

            {error && <p className="error-message">{error}</p>}

            {comparison && (
                <div className="comparison-table-wrapper">
                    <table className="comparison-table">
                        <thead>
                            <tr>
                                <th scope="col">Produkt</th>
                                {comparison.items.map((item) => (
                                    <th scope="col" key={item.product.id}>
                                        {item.product.name}
                                        <div className="comparison-highlights">
                                            {item.highlights.map((highlight) => (
                                                <span key={highlight} className="product-badge">
                                                    {highlightLabels[highlight]}
                                                </span>
                                            ))}
                                        </div>
                                    </th>
                                ))}
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <th scope="row">Pris nu</th>
                                {comparison.items.map((item) => (
                                    <td key={item.product.id}>{priceOrDash(item.summary.latest_price)}</td>
                                ))}
                            </tr>
                            <tr>
                                <th scope="row">Siden forrige pris</th>
                                {comparison.items.map((item) => (
                                    <td key={item.product.id}>{formatChange(item.summary.price_change)}</td>
                                ))}
                            </tr>
                            <tr>
                                <th scope="row">Laveste / højeste set</th>
                                {comparison.items.map((item) => (
                                    <td key={item.product.id}>
                                        {priceOrDash(item.summary.lowest_price)} / {priceOrDash(item.summary.highest_price)}
                                    </td>
                                ))}
                            </tr>
                            <tr>
                                <th scope="row">Prismålinger</th>
                                {comparison.items.map((item) => (
                                    <td key={item.product.id}>{item.summary.observation_count}</td>
                                ))}
                            </tr>
                            <tr>
                                <th scope="row">Pris hentet</th>
                                {comparison.items.map((item) => (
                                    <td key={item.product.id}>
                                        {item.summary.freshness ? (
                                            <>
                                                {formatDateTime(item.summary.freshness.fetched_at)}
                                                <br />
                                                <span className={`freshness-badge freshness-${item.summary.freshness.status}`}>
                                                    {item.summary.freshness.origin_label} · {item.summary.freshness.status_label}
                                                </span>
                                            </>
                                        ) : (
                                            "–"
                                        )}
                                    </td>
                                ))}
                            </tr>
                            <tr>
                                <th scope="row">Bedømmelse</th>
                                {comparison.items.map((item) => (
                                    <td key={item.product.id}>{item.product.rating ?? "–"}</td>
                                ))}
                            </tr>
                            <tr>
                                <th scope="row">Butik</th>
                                {comparison.items.map((item) => (
                                    <td key={item.product.id}>{item.product.source}</td>
                                ))}
                            </tr>
                        </tbody>
                    </table>
                    {comparison.price_spread !== null && (
                        <p className="comparison-spread">
                            Forskel mellem dyreste og billigste: {formatPrice(comparison.price_spread)}
                        </p>
                    )}
                </div>
            )}
        </section>
    );
}

export default ComparisonPanel;

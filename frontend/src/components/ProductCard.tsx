import { useState } from "react";
import { formatDateTime, formatPrice } from "../format";
import type { PriceHistorySummary, ProductResult } from "../types";
import PriceHistoryPanel from "./PriceHistoryPanel";

type ProductCardProps = {
    item: ProductResult;
    isSelected?: boolean;
    canSelectMore?: boolean;
    onToggleCompare?: (productId: number) => void;
};

function PriceHistoryLine({ summary }: { summary: PriceHistorySummary }) {
    const change = summary.price_change;

    return (
        <div className="price-history-summary">
            {summary.freshness && (
                <p className="price-observed">
                    Pris hentet {formatDateTime(summary.freshness.fetched_at)}{" "}
                    <span className={`freshness-badge freshness-${summary.freshness.status}`}>
                        {summary.freshness.status_label}
                    </span>
                </p>
            )}
            {summary.observation_count > 1 && (
                <p>
                    {change !== null && change !== 0 && (
                        <span className={change < 0 ? "price-down" : "price-up"}>
                            {change < 0 ? `↓ ${formatPrice(-change)}` : `↑ ${formatPrice(change)}`} siden forrige pris.{" "}
                        </span>
                    )}
                    Laveste {formatPrice(summary.lowest_price ?? 0)}, højeste {formatPrice(summary.highest_price ?? 0)} i{" "}
                    {summary.observation_count} målinger.
                </p>
            )}
            {summary.is_lowest_seen && <span className="product-badge lowest-badge">Laveste pris set</span>}
        </div>
    );
}

function ProductCard({ item, isSelected = false, canSelectMore = true, onToggleCompare }: ProductCardProps) {
    const [showHistory, setShowHistory] = useState(false);
    const productId = item.product_id ?? null;

    return (
        <div className={isSelected ? "product-card product-card-selected" : "product-card"}>
            {item.product.image_url && (
                <img src={item.product.image_url} alt={item.product.name} />
            )}

            <h3>{item.product.name}</h3>

            <div className="product-badges">
                {item.badges.map((badge) => (
                    <span key={badge} className="product-badge">
                        {badge}
                    </span>
                ))}
            </div>

            <p className="product-price">{item.product.price} kr.</p>

            {item.price_history && <PriceHistoryLine summary={item.price_history} />}

            <p>Butik: {item.product.source}</p>

            <p className="product-score">Score: {item.score}/100</p>

            <div className="product-explanations">
                {item.explanations.map((explanation) => (
                    <p key={explanation}>{explanation}</p>
                ))}
            </div>

            {productId !== null && (
                <div className="product-history-actions">
                    <button
                        type="button"
                        className="history-toggle"
                        aria-expanded={showHistory}
                        onClick={() => setShowHistory((current) => !current)}
                    >
                        {showHistory ? "Skjul prishistorik" : "Vis prishistorik"}
                    </button>

                    {onToggleCompare && (
                        <label className="compare-toggle">
                            <input
                                type="checkbox"
                                checked={isSelected}
                                disabled={!isSelected && !canSelectMore}
                                onChange={() => onToggleCompare(productId)}
                            />
                            Sammenlign
                        </label>
                    )}
                </div>
            )}

            {showHistory && productId !== null && <PriceHistoryPanel productId={productId} />}

            <a
                className="product-link"
                href={item.product.url}
                target="_blank"
                rel="noreferrer"
            >
                {item.product.url.includes("google.com")
                    ? "Se via Google Shopping"
                    : "Se produkt hos forhandler"}
            </a>
        </div>
    );
}

export default ProductCard;

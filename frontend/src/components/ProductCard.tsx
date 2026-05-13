import type { ProductResult } from "../types";

type ProductCardProps = {
    item: ProductResult;
};

function ProductCard({ item }: ProductCardProps) {
    return (
        <div className="product-card">
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

            <p>Butik: {item.product.source}</p>

            <p className="product-score">Score: {item.score}/100</p>

            <div className="product-explanations">
                {item.explanations.map((explanation) => (
                    <p key={explanation}>{explanation}</p>
                ))}
            </div>

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
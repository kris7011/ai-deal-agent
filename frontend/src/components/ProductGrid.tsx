import ProductCard from "./ProductCard";
import type { ProductResult } from "../types";

type ProductGridProps = {
    products: ProductResult[];
    selectedIds?: number[];
    maxSelected?: number;
    onToggleCompare?: (productId: number) => void;
};

function ProductGrid({ products, selectedIds = [], maxSelected = 4, onToggleCompare }: ProductGridProps) {
    return (
        <div className="product-grid">
            {products.map((item, index) => (
                <ProductCard
                    // Several offers can share a Google Shopping URL, so the stored id comes first.
                    key={item.product_id ?? `${item.product.url}-${index}`}
                    item={item}
                    isSelected={item.product_id != null && selectedIds.includes(item.product_id)}
                    canSelectMore={selectedIds.length < maxSelected}
                    onToggleCompare={onToggleCompare}
                />
            ))}
        </div>
    );
}

export default ProductGrid;

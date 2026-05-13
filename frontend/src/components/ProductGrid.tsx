import ProductCard from "./ProductCard";
import type { ProductResult } from "../types";

type ProductGridProps = {
    products: ProductResult[];
};

function ProductGrid({ products }: ProductGridProps) {
    return (
        <div className="product-grid">
            {products.map((item) => (
                <ProductCard key={item.product.url} item={item} />
            ))}
        </div>
    );
}

export default ProductGrid;
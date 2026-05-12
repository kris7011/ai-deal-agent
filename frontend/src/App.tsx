import { useState } from "react";
import "./App.css";

type Product = {
  name: string;
  price: number;
  image_url: string | null;
  source: string;
  url: string;
};

type ProductResult = {
  product: Product;
  score: number;
  explanations: string[];
};

function App() {
  const [query, setQuery] = useState("");
  const [products, setProducts] = useState<ProductResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function searchProducts() {
    if (!query.trim()) {
      setError("Skriv hvad du leder efter først.");
      return;
    }

    setError(null);
    setLoading(true);
    setProducts([]);

    try {
      const response = await fetch("http://127.0.0.1:8000/api/search", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail ?? "Søgningen fejlede.");
      }

      setProducts(data.products);
    } catch (error) {
      console.error(error);

      if (error instanceof Error) {
        setError(error.message);
      } else {
        setError("Der skete en fejl. Prøv venligst igen.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page">
      <h1>AI Deal Agent</h1>

      <div className="search-bar">
        <input
          type="text"
          placeholder="Søg efter produkter..."
          value={query}
          onChange={(event) => setQuery(event.target.value)}
        />
        {error && <p className="error-message">{error}</p>}

        <button onClick={searchProducts} disabled={loading}>
          {loading ? "Søger..." : "Søg"}
        </button>
      </div>

      {loading && <p>Loader...</p>}

      <div className="product-grid">
        {products.map((item) => (
          <div key={item.product.url} className="product-card">
            {item.product.image_url && (
              <img src={item.product.image_url} alt={item.product.name} />
            )}

            <h3>{item.product.name}</h3>

            <p className="product-price">
              {item.product.price} kr.
            </p>
            <p>Butik: {item.product.source}</p>
            <p className="product-score">
              Score: {item.score}/100
            </p>

            <div className="product-explanations">
              {item.explanations.map((explanation) => (
                <p key={explanation}>
                  {explanation}
                </p>
              ))}
            </div>

            <a
              className="product-link"
              href={item.product.url}
              target="_blank"
              rel="noreferrer"
            >
              Se produkt
            </a>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;
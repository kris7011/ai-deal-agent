import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { productResult } from "../test/fakeApi";
import ProductCard from "./ProductCard";

describe("ProductCard", () => {
  it("shows price, shop, score, badges and explanations", () => {
    render(
      <ProductCard
        item={productResult("Roborock S8", 92, {
          badges: ["Stærkt match", "Under budget"],
          explanations: ["✓ Under budget (4799 kr.)", "? Ikke tydeligt om produktet matcher: høj sugeevne"],
        })}
      />,
    );

    expect(screen.getByRole("heading", { name: "Roborock S8" })).toBeInTheDocument();
    expect(screen.getByRole("img", { name: "Roborock S8" })).toBeInTheDocument();
    expect(screen.getByText("4799 kr.")).toBeInTheDocument();
    expect(screen.getByText("Butik: Test Shop")).toBeInTheDocument();
    expect(screen.getByText("Score: 92/100")).toBeInTheDocument();
    expect(screen.getByText("Under budget")).toHaveClass("product-badge");
    expect(screen.getByText("? Ikke tydeligt om produktet matcher: høj sugeevne")).toBeInTheDocument();
  });

  it("labels Google Shopping links differently from retailer links and opens them safely", () => {
    const { rerender } = render(<ProductCard item={productResult("Roborock S8", 92)} />);

    const googleLink = screen.getByRole("link", { name: "Se via Google Shopping" });
    expect(googleLink).toHaveAttribute("target", "_blank");
    expect(googleLink).toHaveAttribute("rel", "noreferrer");

    const retailerItem = productResult("Roborock S8", 92);
    retailerItem.product.url = "https://www.elgiganten.dk/product/roborock-s8";
    rerender(<ProductCard item={retailerItem} />);

    expect(screen.getByRole("link", { name: "Se produkt hos forhandler" })).toHaveAttribute(
      "href",
      "https://www.elgiganten.dk/product/roborock-s8",
    );
  });

  it("omits the image when the product has none", () => {
    const item = productResult("Uden billede", 40);
    item.product.image_url = null;

    render(<ProductCard item={item} />);

    expect(screen.queryByRole("img")).not.toBeInTheDocument();
  });
});

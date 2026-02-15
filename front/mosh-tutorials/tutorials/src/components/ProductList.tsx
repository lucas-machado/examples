import { useState, useEffect } from "react";

interface ProductListProps {
  category: string;
}

export function ProductList({ category }: ProductListProps) {
  const [products, setProducts] = useState<string[]>([]);

  useEffect(() => {
    console.log("Fetching products in category: ", category);
    setProducts(["Clothing", "Housing"]);
  }, [category]);

  return (
    <>
      <p>Product List</p>
    </>
  );
}

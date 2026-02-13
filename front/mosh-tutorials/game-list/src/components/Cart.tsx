interface CartProps {
  cartItems: string[];
  onClearRequested: () => void;
}

export default function Cart({ cartItems, onClearRequested }: CartProps) {
  return (
    <>
      <h2>Cart</h2>
      <ul>
        {cartItems.map((product) => (
          <li key={product}>{product}</li>
        ))}
      </ul>
      <button onClick={onClearRequested}>Clear</button>
    </>
  );
}

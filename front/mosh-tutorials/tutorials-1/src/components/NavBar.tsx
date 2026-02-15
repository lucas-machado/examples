interface NavBarProps {
  cartItemsCount: number;
}

export default function NavBar({ cartItemsCount }: NavBarProps) {
  return <div>Navbar: {cartItemsCount}</div>;
}

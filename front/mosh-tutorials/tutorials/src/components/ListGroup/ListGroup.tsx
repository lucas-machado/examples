import { useState } from "react";
import "./ListGroup.css";

interface ListGroupProps {
  items: string[];
  heading: string;
  onSelectItem: (item: string) => void;
}

export default function ListGroup({
  items,
  heading,
  onSelectItem,
}: ListGroupProps) {
  const [selectedIndex, setSelectedIndex] = useState(-1);

  return (
    <>
      <h1>{heading}</h1>
      <ul className="list-group" style={{ backgroundColor: "yellow" }}>
        {items.length === 0 && <p>No items found</p>}
        {items.map((item, index) => (
          <li
            className={
              selectedIndex === index
                ? "list-group-item active"
                : "list-group-item"
            }
            key={item}
            onClick={() => {
              setSelectedIndex(index);
              onSelectItem(item);
            }}
          >
            {item}
          </li>
        ))}
      </ul>
    </>
  );
}

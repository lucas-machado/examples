import { useState } from "react";

interface ExpandableTextProps {
  children: string;
  maxChars?: number;
}

export function ExpandableText({
  children,
  maxChars = 10,
}: ExpandableTextProps) {
  if (children.length < maxChars) return <p>{children}</p>;

  const [reduced, setReduced] = useState(false);

  if (!children) return null;

  const text = !reduced ? children : children?.slice(0, maxChars) + "...";

  const handleClick = () => {
    setReduced(!reduced);
  };

  return (
    <>
      <p>
        {text}
        <button onClick={handleClick}>{reduced ? "More" : "Less"}</button>
      </p>
    </>
  );
}

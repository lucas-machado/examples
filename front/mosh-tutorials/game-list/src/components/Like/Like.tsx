import { AiFillHeart, AiOutlineHeart } from "react-icons/ai";
import { useState } from "react";

interface LikeProps {
  onClick: () => void;
}

export default function Like({ onClick }: LikeProps) {
  const [liked, setLiked] = useState(false);

  return (
    <>
      {liked ? (
        <AiFillHeart
          color="#ff6b81"
          size={20}
          onClick={() => {
            setLiked(false);
            onClick();
          }}
        />
      ) : (
        <AiOutlineHeart
          color="#ff6b81"
          size={20}
          onClick={() => {
            setLiked(true);
            onClick();
          }}
        />
      )}
    </>
  );
}

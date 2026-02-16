import type { Game } from "../hooks/useGames";
import { Card, Image } from "@chakra-ui/react";

interface GameCardProps {
  game: Game;
}

export function GameCard({ game }: GameCardProps) {
  return (
    <Card.Root margin="10px">
      <Image src={game.background_image} />
      <Card.Body>
        <Card.Title fontSize="2xl">{game.name}</Card.Title>
      </Card.Body>
    </Card.Root>
  );
}

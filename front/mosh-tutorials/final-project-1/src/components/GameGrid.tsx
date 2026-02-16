import { useGames, type Game } from "../hooks/useGames";
import { Text } from "@chakra-ui/react";

export function GameGrid() {
  const { games, error } = useGames();
  return (
    <>
      {error && <Text>{error}</Text>}
      <ul>
        {(games ?? []).map((game) => (
          <li key={game.id}>{game.name}</li>
        ))}
      </ul>
    </>
  );
}

import { useGames, type Game } from "../hooks/useGames";
import { SimpleGrid, Text } from "@chakra-ui/react";
import { GameCard } from "./GameCard";

export function GameGrid() {
  const { games, error } = useGames();
  return (
    <>
      {error && <Text>{error}</Text>}
      <SimpleGrid columns={{ sm: 1, md: 3 }} padding="10px">
        {(games ?? []).map((game) => (
          <GameCard key={game.id} game={game} />
        ))}
      </SimpleGrid>
    </>
  );
}

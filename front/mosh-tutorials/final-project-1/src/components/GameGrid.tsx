import { useState, useEffect } from "react";
import apiClient from "../services/api-client";
import { AxiosError } from "axios";
import { Text } from "@chakra-ui/react";

interface Game {
  id: number;
  name: string;
}

interface FetchGamesResponse {
  count: number;
  results: Game[];
}

export function GameGrid() {
  const [games, setGames] = useState<Game[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    const request = apiClient.get<FetchGamesResponse>("/games");

    const requestGames = async () => {
      try {
        const response = await request;
        setGames(response.data.results ?? []);
      } catch (err) {
        setError((err as AxiosError).message);
      }
    };

    requestGames();
  }, []);

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

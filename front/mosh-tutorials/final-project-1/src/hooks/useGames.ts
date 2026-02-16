import { useState, useEffect } from "react";
import apiClient from "../services/api-client";
import { AxiosError, CanceledError } from "axios";

export interface Game {
  id: number;
  name: string;
}

interface FetchGamesResponse {
  count: number;
  results: Game[];
}

export function useGames() {
  const [games, setGames] = useState<Game[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    const controller = new AbortController();
    const request = apiClient.get<FetchGamesResponse>("/games", {
      signal: controller.signal,
    });

    const requestGames = async () => {
      try {
        const response = await request;
        setGames(response.data.results ?? []);
      } catch (err) {
        if (err instanceof CanceledError) return;
        setError((err as AxiosError).message);
      }
    };

    requestGames();

    return () => controller.abort();
  }, []);

  return { games, error };
}

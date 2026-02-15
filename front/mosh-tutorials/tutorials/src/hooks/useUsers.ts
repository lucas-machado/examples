import { useState, useEffect } from "react";
import userService, { type User } from "../services/user-service";
import { CanceledError, AxiosError } from "axios";

export default function useUsers() {
  const [users, setUsers] = useState<User[]>([]);
  const [error, setError] = useState("");
  const [isLoading, setLoading] = useState(false);

  useEffect(() => {
    const { request, cancel } = userService.getAll<User>();

    const fetchUsers = async () => {
      try {
        setLoading(true);
        const response = await request;
        setUsers(response.data);
        setLoading(false);
      } catch (err) {
        if (err instanceof CanceledError) return;
        setError((err as AxiosError).message);
        setLoading(false);
      }
    };

    fetchUsers();

    return cancel;
  }, []);

  return { users, error, isLoading, setUsers, setError };
}

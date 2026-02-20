import { AxiosError, CanceledError } from "axios";
import api from "../client/api";
import { useState, useEffect } from "react";

interface MomentBase {
  title: string;
  url: string;
}

export interface CreateMoment extends MomentBase {
  file: File;
}

export interface Moment extends MomentBase {
  id: number;
}

export function useMoments() {
  const [moments, setMoments] = useState<Moment[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    const controller = new AbortController();

    const fetchMoments = async () => {
      try {
        const request = api.get<Moment[]>("/moments", {
          signal: controller.signal,
        });

        const result = await request;
        setMoments(result.data);
      } catch (err) {
        if (err instanceof CanceledError) return;
        setError((err as AxiosError).message);
      }
    };

    fetchMoments();

    return () => controller.abort();
  }, []);

  const addMoment = async (moment: CreateMoment) => {
    const newMoment: Moment = {
      id: Date.now() * -1,
      title: moment.title,
      url: moment.url,
    };
    try {
      setMoments((curr) => [...curr, newMoment]);
      const formData = new FormData();
      formData.append("title", moment.title);
      formData.append("file", moment.file);
      const response = await api.post<Moment>("/moments", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setMoments((curr) =>
        curr.map((m) => {
          if (m.id === newMoment.id) {
            URL.revokeObjectURL(newMoment.url);
            return response.data;
          } else {
            return m;
          }
        }),
      );
    } catch (err) {
      setError((err as AxiosError).message);
      setMoments((curr) => curr.filter((moment) => moment.id !== newMoment.id));
    }
  };

  const deleteMoment = async (moment: Moment) => {
    try {
      setMoments((curr) => curr.filter((m) => m.id !== moment.id));
      await api.delete("/moments/" + moment.id);
    } catch (err) {
      setError((err as AxiosError).message);
      setMoments((curr) => [...curr, moment]);
    }
  };

  const updateMoment = async (moment: Moment) => {
    const original = moments.find((m) => m.id === moment.id);
    if (!original) return;

    try {
      setMoments((curr) =>
        curr.map((m) => (m.id === moment.id ? { ...moment } : m)),
      );
      await api.put("/moments/" + moment.id, moment);
    } catch (err) {
      setError((err as AxiosError).message);
      setMoments((curr) =>
        curr.map((m) => (m.id === moment.id ? original : m)),
      );
    }
  };

  return { moments, error, addMoment, deleteMoment, updateMoment };
}

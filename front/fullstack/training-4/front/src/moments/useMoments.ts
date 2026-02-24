import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { CACHE_KEY_MOMENTS } from "../constants";
import axiosInstance from "../core/axiosInstance";
import axios from "axios";

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

export function useGetMoments() {
  return useQuery<Moment[], Error>({
    queryKey: CACHE_KEY_MOMENTS,
    queryFn: async () => {
      const res = await axiosInstance.get<Moment[]>("/moments");
      return res.data;
    },
  });
}

export function useAddMoment() {
  const queryClient = useQueryClient();
  return useMutation<Moment, Error, CreateMoment, { optimisticMoment: Moment }>(
    {
      mutationFn: async (moment: CreateMoment) => {
        const formData = new FormData();
        formData.append("title", moment.title);
        formData.append("file", moment.file);
        const res = await axiosInstance.post<Moment>("/moments", formData, {
          headers: { "Content-Type": "multipart/form-data" },
        });
        return res.data;
      },
      onMutate: (newMoment: CreateMoment) => {
        const optimisticMoment: Moment = {
          id: Date.now() * -1,
          title: newMoment.title,
          url: newMoment.url,
        };

        queryClient.setQueryData<Moment[]>(CACHE_KEY_MOMENTS, (moments) => [
          optimisticMoment,
          ...(moments || []),
        ]);

        return { optimisticMoment };
      },
      onSuccess: (savedMoment, _newMoment, context) => {
        queryClient.setQueryData<Moment[]>(CACHE_KEY_MOMENTS, (moments) =>
          moments?.map((m) => {
            if (m === context.optimisticMoment) {
              URL.revokeObjectURL(m.url);
              return savedMoment;
            } else {
              return m;
            }
          }),
        );
      },
      onError: (error, _newMoment, context) => {
        queryClient.setQueryData<Moment[]>(CACHE_KEY_MOMENTS, (moments) =>
          moments?.filter((m) => m !== context?.optimisticMoment),
        );
      },
    },
  );
}

export function useDeleteMoment() {
  const queryClient = useQueryClient();
  return useMutation<
    void,
    Error,
    number,
    { optimisticMoment: Moment | undefined }
  >({
    mutationFn: async (id: number) => {
      await axiosInstance.delete("/moments/" + id);
    },
    onMutate: (id: number) => {
      const optimisticMoment = queryClient
        .getQueryData<Moment[]>(CACHE_KEY_MOMENTS)
        ?.find((m) => m.id === id);

      queryClient.setQueryData<Moment[]>(CACHE_KEY_MOMENTS, (moments) =>
        moments?.filter((m) => m.id !== id),
      );

      return { optimisticMoment };
    },
    onError: (_data, _id, context) => {
      const moment = context?.optimisticMoment;
      if (!moment) return;

      queryClient.setQueryData<Moment[]>(CACHE_KEY_MOMENTS, (moments) => [
        moment,
        ...(moments || []),
      ]);
    },
  });
}

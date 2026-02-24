import { MomentGrid } from "./moments/MomentGrid";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import {
  useGetMoments,
  useAddMoment,
  type Moment,
  useDeleteMoment,
} from "./moments/useMoments";

const createMomentSchema = z.object({
  title: z.string().min(6, { message: "min title is 6" }),
  files: z
    .instanceof(FileList)
    .refine((list) => list.length == 1, "select a singles image"),
});

type CreateMomentInputs = z.infer<typeof createMomentSchema>;

const MomentsPage = () => {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<CreateMomentInputs>({
    resolver: zodResolver(createMomentSchema),
  });
  const { data: moments, error, isLoading } = useGetMoments();
  const addMoment = useAddMoment();
  const deleteMoment = useDeleteMoment();

  const onSubmit = (formData: CreateMomentInputs) => {
    if (!formData.files || !formData.files[0]) return;
    const url = URL.createObjectURL(formData.files[0]);
    addMoment.mutate({
      title: formData.title,
      url: url,
      file: formData.files[0],
    });
  };

  const onDeleteMoment = (moment: Moment) => {
    deleteMoment.mutate(moment.id);
  };

  return (
    <>
      {error && <p>{error.message}</p>}
      <MomentGrid moments={moments || []} deleteMoment={onDeleteMoment} />

      <form className="px-3 py-2" onSubmit={handleSubmit(onSubmit)}>
        <label>
          Title: <input className="border" type="text" {...register("title")} />
        </label>
        {errors.title && <p>{errors.title.message}</p>}

        <label>
          URL: <input className="border" type="file" {...register("files")} />
        </label>
        {errors.files && <p>{errors.files.message}</p>}

        <button
          disabled={isLoading}
          type="submit"
          className="border px-4"
          style={{ marginLeft: "10px" }}
        >
          Add
        </button>
      </form>
    </>
  );
};

export default MomentsPage;

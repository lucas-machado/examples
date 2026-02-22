import "./App.css";
import { MomentGrid } from "./components/MomentGrid";
import { useMoments } from "./hooks/useMoments";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";

const momentSchema = z.object({
  title: z.string().min(6, { message: "min title is 6" }),
  files: z
    .instanceof(FileList)
    .refine((list) => list.length == 1, "select a singles image"),
});

type FormData = z.infer<typeof momentSchema>;

function App() {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormData>({ resolver: zodResolver(momentSchema) });

  const { moments, error, addMoment, deleteMoment } = useMoments();

  const onSubmit = (formData: FormData) => {
    if (!formData.files || !formData.files[0]) return;
    const url = URL.createObjectURL(formData.files[0]);
    addMoment({ title: formData.title, url: url, file: formData.files[0] });
  };

  return (
    <>
      {error && <p>{error}</p>}
      <MomentGrid moments={moments} deleteMoment={deleteMoment} />

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
          type="submit"
          className="border px-4"
          style={{ marginLeft: "10px" }}
        >
          Add
        </button>
      </form>
    </>
  );
}

export default App;

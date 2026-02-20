import "./App.css";
import { MomentGrid } from "./components/MomentGrid";
import { useMoments, type CreateMoment } from "./hooks/useMoments";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";

const momentSchema = z.object({
  title: z.string().min(6, { message: "min title is 6" }),
  url: z.url(),
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
    addMoment(formData);
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
          URL: <input className="border" type="text" {...register("url")} />
        </label>
        {errors.url && <p>{errors.url.message}</p>}

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

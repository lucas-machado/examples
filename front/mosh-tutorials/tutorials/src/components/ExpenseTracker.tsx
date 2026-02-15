import { useForm, type FieldValues } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { useState, type ChangeEvent } from "react";

const categories = ["Groceries", "Utilities", "Entertainment"] as const;

const schema = z.object({
  description: z
    .string()
    .min(10, { message: "Description must be at least 10 characters" }),
  amount: z.number().min(1, { message: "Amount must be at least 1" }),
  category: z.enum(categories),
});

type FormData = z.infer<typeof schema>;

export function ExpenseTracker() {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormData>({ resolver: zodResolver(schema) });

  const [items, setItems] = useState<FormData[]>([]);

  const onSubmit = (item: FieldValues) => {
    console.log(item);

    setItems([
      ...items,
      {
        description: item.description,
        amount: item.amount,
        category: item.category,
      },
    ]);
  };

  const [categoryFilter, setCategoryFilter] = useState("All categories");

  const handleCategorySelect = (event: ChangeEvent<HTMLSelectElement>) => {
    setCategoryFilter(event.target.value);
  };

  const handleDelete = (description: string) => {
    setItems(items.filter((item) => item.description !== description));
  };

  return (
    <>
      <form onSubmit={handleSubmit(onSubmit)}>
        <div className="mb-3">
          <label htmlFor="description" className="form-label">
            Description
          </label>
          <input
            id="description"
            type="string"
            className="form-control"
            {...register("description")}
          />
          {errors.description && (
            <p className="danger">{errors.description.message}</p>
          )}
        </div>

        <div className="mb-3">
          <label htmlFor="amount" className="form-label">
            Amount
          </label>
          <input
            id="amount"
            type="number"
            className="form-control"
            {...register("amount", { valueAsNumber: true })}
          />
          {errors.amount && <p className="danger">{errors.amount.message}</p>}
        </div>

        <div className="mb-3">
          <label htmlFor="category" className="form-label">
            Category
          </label>
          <select
            id="category"
            className="form-select"
            {...register("category")}
          >
            <option value=""></option>
            <option value="Groceries">Groceries</option>
            <option value="Utilities">Utilities</option>
            <option value="Entertainment">Entertainment</option>
          </select>
          {errors.category && (
            <p className="danger">{errors.category.message}</p>
          )}
        </div>

        <button className="btn btn-primary">Submit</button>
      </form>

      <div style={{ paddingTop: "10px" }}>
        <select className="form-select" onChange={handleCategorySelect}>
          <option value="All categories">All categories</option>
          <option value="Groceries">Groceries</option>
          <option value="Utilities">Utilities</option>
          <option value="Entertainment">Entertainment</option>
        </select>
      </div>

      <table className="table table-bordered mt-5">
        <thead>
          <tr>
            <th>Description</th>
            <th>Amount</th>
            <th>Category</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {items
            .filter((item) => item.category !== categoryFilter)
            .map((item) => (
              <tr key={item.description}>
                <td>{item.description}</td>
                <td>{item.amount}</td>
                <td>{item.category}</td>
                <td>
                  <button
                    onClick={() => handleDelete(item.description)}
                    className="btn btn-danger"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
        </tbody>
      </table>
    </>
  );
}

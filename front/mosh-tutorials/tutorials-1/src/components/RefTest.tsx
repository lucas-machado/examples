import { useRef, type FormEvent } from "react";

export function RefTest() {
  const nameRef = useRef<HTMLInputElement>(null);

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();

    if (nameRef.current) console.log(nameRef.current.value);
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="mb-3">
        <label htmlFor="name" className="form-label">
          Name
        </label>
        <input id="name" ref={nameRef} className="form-control"></input>
        <button className="btn btn-primary">Submit</button>
      </div>
    </form>
  );
}

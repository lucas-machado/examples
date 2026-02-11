import Like from "./components/Like";

export default function App() {
  return (
    <div>
      <Like onClick={() => console.log("clicked")} />
    </div>
  );
}

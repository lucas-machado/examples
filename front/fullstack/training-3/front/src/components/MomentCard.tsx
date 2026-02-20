interface MomentCardProps {
  title: string;
  url: string;
  onDelete: () => void;
}

export function MomentCard({ title, url, onDelete }: MomentCardProps) {
  return (
    <div>
      <p>{title}</p>
      <p>{url}</p>
      <button className="border px-3" onClick={() => onDelete()}>
        x
      </button>
    </div>
  );
}

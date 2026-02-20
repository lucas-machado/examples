import styles from "./MomentCard.module.css";

interface MomentCardProps {
  title: string;
  url: string;
  onDelete: () => void;
}

export function MomentCard({ title, url, onDelete }: MomentCardProps) {
  return (
    <div className={styles.card}>
      <p>{title}</p>
      <img src={url} />
      <button className={styles.overlay} onClick={() => onDelete()}>
        x
      </button>
    </div>
  );
}

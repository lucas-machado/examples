import { type Moment } from "../hooks/useMoments";
import { MomentCard } from "./MomentCard";

export interface MomentGridProps {
  moments: Moment[];
  deleteMoment: (moment: Moment) => void;
}

export function MomentGrid({ moments, deleteMoment }: MomentGridProps) {
  return (
    <>
      <div className="grid grid-cols-3 gap-4">
        {moments.map((moment) => (
          <MomentCard
            title={moment.title}
            url={moment.url}
            onDelete={() => deleteMoment(moment)}
          />
        ))}
      </div>
    </>
  );
}

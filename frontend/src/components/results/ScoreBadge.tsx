interface ScoreBadgeProps {
  score: number;
}

export function ScoreBadge({ score }: ScoreBadgeProps) {
  const percent = Math.round(score * 100);
  return (
    <span className="rounded-md bg-brand-50 px-2 py-0.5 text-xs font-semibold text-brand-700">
      {percent}% match
    </span>
  );
}

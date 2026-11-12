// Javob matni: [1], [2] havolalari bosiladigan tugmaga aylanadi -> o'ng paneldagi dalilni ochadi.
export function AnswerText({ text, onCite }: { text: string; onCite: (evidenceId: string) => void }) {
  const parts = text.split(/(\[\d+\])/g);
  return (
    <div className="whitespace-pre-line text-[15px] leading-relaxed text-ink">
      {parts.map((part, index) => {
        const match = part.match(/^\[(\d+)\]$/);
        if (!match) return <span key={index}>{part}</span>;
        return (
          <button
            key={index}
            onClick={() => onCite(match[1])}
            className="mx-0.5 inline-flex h-5 min-w-5 items-center justify-center rounded bg-primary-soft px-1 align-text-top text-xs font-semibold text-primary hover:bg-primary hover:text-white"
            aria-label={`Show source ${match[1]}`}
          >
            {match[1]}
          </button>
        );
      })}
    </div>
  );
}

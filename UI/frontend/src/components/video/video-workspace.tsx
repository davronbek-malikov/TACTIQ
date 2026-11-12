import { Play, Video } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { cn, formatTimestamp } from "@/lib/format";

// V2 (video intelligence) uchun tayyor komponentlar. Hozircha ma'lumot yo'q — soxta voqealar ko'rsatilmaydi.

export interface TimelineEvent {
  id: string;
  timestamp_seconds: number;
  label: string;
  kind: "event" | "observation" | "annotation";
}

export interface VideoClip {
  id: string;
  title: string;
  start_seconds: number;
  end_seconds: number;
}

export function VideoTimeline({
  duration,
  events,
  position = 0,
  onSeek,
}: {
  duration: number;
  events: TimelineEvent[];
  position?: number;
  onSeek?: (seconds: number) => void;
}) {
  return (
    <div>
      <div className="relative h-8 rounded-md bg-subtle" role="slider" aria-label="Match timeline" aria-valuemin={0} aria-valuemax={duration} aria-valuenow={position}>
        <div className="absolute inset-y-0 left-0 rounded-l-md bg-primary-soft" style={{ width: duration ? `${(position / duration) * 100}%` : 0 }} />
        {events.map((event) => (
          <button
            key={event.id}
            title={`${formatTimestamp(event.timestamp_seconds)} · ${event.label}`}
            onClick={() => onSeek?.(event.timestamp_seconds)}
            className={cn("absolute top-1 h-6 w-1 rounded", event.kind === "observation" ? "bg-primary" : "bg-muted")}
            style={{ left: `${(event.timestamp_seconds / Math.max(duration, 1)) * 100}%` }}
          />
        ))}
      </div>
      <div className="mt-1 flex justify-between text-xs text-muted">
        <span>0:00</span>
        <span>{formatTimestamp(duration)}</span>
      </div>
    </div>
  );
}

export function VideoWorkspace({ events = [], clips = [] }: { events?: TimelineEvent[]; clips?: VideoClip[] }) {
  return (
    <div className="grid gap-4 lg:grid-cols-3">
      <div className="lg:col-span-2">
        <div className="flex aspect-video flex-col items-center justify-center rounded-xl border border-dashed border-line bg-subtle text-center">
          <Video className="mb-2 size-7 text-muted" aria-hidden />
          <p className="text-sm font-medium">No video loaded</p>
          <p className="max-w-sm text-xs text-muted">Video ingestion, player detection and tracking arrive in V2.</p>
        </div>
        <div className="mt-3 flex items-center gap-3">
          <button disabled className="grid size-9 place-items-center rounded-full bg-primary text-white opacity-40" aria-label="Play">
            <Play className="size-4" />
          </button>
          <div className="flex-1"><VideoTimeline duration={90 * 60} events={events} /></div>
        </div>
      </div>
      <div className="rounded-xl border border-line p-4">
        <div className="mb-2 flex items-center justify-between">
          <h3 className="text-sm font-semibold">Clips & observations</h3>
          <Badge>Planned · V2</Badge>
        </div>
        {clips.length === 0 ? (
          <p className="text-sm text-muted">
            AI observations will reference a match, a timestamp and a clip — e.g. clicking 32:14 opens the video at that moment.
          </p>
        ) : (
          <ul className="space-y-2">
            {clips.map((clip) => (
              <li key={clip.id} className="rounded-lg bg-subtle px-3 py-2 text-sm">
                {clip.title} <span className="text-muted">{formatTimestamp(clip.start_seconds)}–{formatTimestamp(clip.end_seconds)}</span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

import { BunnyAvatar } from "./BunnyAvatar";
import { PageDecor } from "./PageDecor";

export function AppLoading({ label }: { label: string }) {
  return (
    <main className="page-shell loading-page">
      <PageDecor />
      <div className="loading-card" aria-live="polite">
        <BunnyAvatar profile />
        <div className="typing-dots large" aria-hidden="true"><i /><i /><i /></div>
        <p>{label}</p>
      </div>
    </main>
  );
}

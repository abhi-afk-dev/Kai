export default function ChatEmptyState() {
  return (
    <div className="flex jet flex-col items-center justify-center text-center px-4 sm:px-6 py-8 select-none">
      <h2 className="text-lg sm:text-xl font-semibold text-[var(--app-text)] mb-1.5">
        Death
      </h2>
      <p className="text-[13px] sm:text-sm font-mono text-[var(--app-text-muted)] uppercase tracking-wide mb-3">
        What's on your mind ?
      </p>
    </div>
  );
}

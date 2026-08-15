import Link from "next/link";

export default function Home() {
  return (
    <div className="flex flex-1 flex-col items-center justify-center px-6">
      <div className="w-full max-w-lg text-center">
        <div className="mb-2 text-sm font-semibold tracking-wide text-emerald-600">
          ROUNDVEST
        </div>
        <h1 className="mb-4 text-4xl font-bold tracking-tight text-zinc-900">
          Invest your spare change, automatically.
        </h1>
        <p className="mb-8 text-lg text-zinc-600">
          Link a bank, and every purchase rounds up to the nearest dollar.
          The round-up goes straight into a real fractional-share order —
          Acorns-style investing, built end to end.
        </p>
        <div className="flex justify-center gap-4">
          <Link
            href="/register"
            className="rounded-full bg-emerald-600 px-6 py-3 font-medium text-white transition hover:bg-emerald-700"
          >
            Get started
          </Link>
          <Link
            href="/login"
            className="rounded-full border border-zinc-300 px-6 py-3 font-medium text-zinc-700 transition hover:bg-zinc-100"
          >
            Log in
          </Link>
        </div>
      </div>
    </div>
  );
}

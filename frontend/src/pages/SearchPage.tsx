import { PageWrapper } from "../components/layout/PageWrapper";

export function SearchPage() {
  return (
    <PageWrapper>
      <section className="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
        <h1 className="text-2xl font-bold text-slate-900">Search</h1>
        <p className="mt-2 text-slate-600">
          Multilingual query interface will be implemented in Phase 2.
        </p>
      </section>
    </PageWrapper>
  );
}

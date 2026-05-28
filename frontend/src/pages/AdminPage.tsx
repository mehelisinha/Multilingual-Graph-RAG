import { PageWrapper } from "../components/layout/PageWrapper";

export function AdminPage() {
  return (
    <PageWrapper>
      <section className="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
        <h1 className="text-2xl font-bold">Admin</h1>
        <p className="mt-2 text-slate-600">Ingestion metrics dashboard coming in Phase 4.</p>
      </section>
    </PageWrapper>
  );
}

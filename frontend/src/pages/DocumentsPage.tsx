import { PageWrapper } from "../components/layout/PageWrapper";
import { DocumentList } from "../components/upload/DocumentList";

export function DocumentsPage() {
  return (
    <PageWrapper>
      <section className="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
        <h1 className="text-2xl font-bold mb-6">Documents</h1>
        <DocumentList />
      </section>
    </PageWrapper>
  );
}

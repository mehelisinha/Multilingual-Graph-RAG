import React, { useEffect, useState } from "react";
import { listDocuments, deleteDocument } from "../../api/documents";
import { DocumentRecord } from "../../types/document.types";
import { FileText, Trash2, RefreshCw } from "lucide-react";
import toast from "react-hot-toast";

export const DocumentList: React.FC = () => {
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchDocuments = async () => {
    setIsLoading(true);
    try {
      const data = await listDocuments();
      setDocuments(data);
    } catch {
      toast.error("Failed to load documents");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  const handleDelete = async (id: string) => {
    if (!window.confirm("Are you sure you want to delete this document?")) return;
    try {
      await deleteDocument(id);
      toast.success("Document deleted");
      setDocuments((docs) => docs.filter((d) => d.id !== id));
    } catch {
      toast.error("Failed to delete document");
    }
  };

  if (isLoading) {
    return <div className="p-8 text-center text-gray-500">Loading documents...</div>;
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
      <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center bg-gray-50 dark:bg-gray-800/50">
        <h3 className="font-semibold text-gray-900 dark:text-white">Ingested Documents</h3>
        <button
          onClick={fetchDocuments}
          className="p-2 text-gray-500 hover:text-blue-600 dark:text-gray-400 dark:hover:text-blue-400 transition-colors"
          title="Refresh list"
        >
          <RefreshCw className="w-5 h-5" />
        </button>
      </div>

      {documents.length === 0 ? (
        <div className="p-8 text-center text-gray-500 dark:text-gray-400">
          No documents found. Upload one to get started.
        </div>
      ) : (
        <ul className="divide-y divide-gray-200 dark:divide-gray-700">
          {documents.map((doc) => (
            <li
              key={doc.id}
              className="p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors flex items-center justify-between"
            >
              <div className="flex items-center space-x-4">
                <div className="p-2 bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded-lg">
                  <FileText className="w-6 h-6" />
                </div>
                <div>
                  <h4 className="font-medium text-gray-900 dark:text-white">
                    {doc.title || doc.filename}
                  </h4>
                  <div className="text-sm text-gray-500 dark:text-gray-400 flex space-x-4 mt-1">
                    <span>{doc.language?.toUpperCase() || "Unknown"}</span>
                    <span>{(doc.size_bytes / 1024).toFixed(1)} KB</span>
                    <span>{doc.chunk_count} chunks</span>
                    <span
                      className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                        doc.status === "COMPLETED"
                          ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                          : doc.status === "FAILED"
                            ? "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400"
                            : "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400"
                      }`}
                    >
                      {doc.status}
                    </span>
                  </div>
                </div>
              </div>

              <button
                onClick={() => handleDelete(doc.id)}
                className="p-2 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
                title="Delete document"
              >
                <Trash2 className="w-5 h-5" />
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

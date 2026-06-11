import React from "react";
import { UploadZone } from "../components/upload/UploadZone";
import { JobStatus } from "../components/upload/JobStatus";
import { DocumentList } from "../components/upload/DocumentList";
import { useIngest } from "../hooks/useIngest";
import { Database } from "lucide-react";
import { PageWrapper } from "../components/layout/PageWrapper";

export const AdminPage: React.FC = () => {
  const { upload, isUploading, activeJob } = useIngest();

  return (
    <PageWrapper>
      <div className="max-w-6xl mx-auto py-8 px-4 sm:px-6 lg:px-8 h-full overflow-y-auto">
        <div className="flex items-center space-x-3 mb-8">
          <div className="p-3 bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded-xl">
            <Database className="w-8 h-8" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white tracking-tight">
              Data Management
            </h1>
            <p className="text-gray-500 dark:text-gray-400 mt-1">
              Upload and manage knowledge base documents
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-1 space-y-6">
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 shadow-sm">
              <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">
                Upload New Document
              </h2>
              <UploadZone onUpload={upload} isUploading={isUploading} />
              <JobStatus job={activeJob} />
            </div>
          </div>

          <div className="lg:col-span-2">
            <DocumentList />
          </div>
        </div>
      </div>
    </PageWrapper>
  );
};

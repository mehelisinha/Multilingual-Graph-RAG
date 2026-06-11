import React from "react";
import { IngestionJob } from "../../types/document.types";
import { CheckCircle, XCircle, Loader2 } from "lucide-react";

interface JobStatusProps {
  job: IngestionJob | null;
}

export const JobStatus: React.FC<JobStatusProps> = ({ job }) => {
  if (!job) return null;

  return (
    <div className="mt-6 bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Processing Status</h3>
        <span className="text-sm font-medium text-gray-500 dark:text-gray-400">
          {job.progress}%
        </span>
      </div>

      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5 mb-6 overflow-hidden">
        <div
          className={`h-2.5 rounded-full transition-all duration-500 ${
            job.status === "FAILED" ? "bg-red-500" : "bg-blue-600"
          }`}
          style={{ width: `${job.progress}%` }}
        ></div>
      </div>

      <div className="flex items-center space-x-3 text-sm">
        {job.status === "COMPLETED" ? (
          <CheckCircle className="w-5 h-5 text-green-500" />
        ) : job.status === "FAILED" ? (
          <XCircle className="w-5 h-5 text-red-500" />
        ) : (
          <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />
        )}

        <span
          className={`font-medium ${
            job.status === "FAILED" ? "text-red-500" : "text-gray-700 dark:text-gray-300"
          }`}
        >
          {job.status === "FAILED" ? job.error_message : job.current_stage.replace(/_/g, " ")}
        </span>
      </div>
    </div>
  );
};

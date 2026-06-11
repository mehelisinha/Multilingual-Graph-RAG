import React, { useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { UploadCloud } from "lucide-react";

interface UploadZoneProps {
  onUpload: (file: File) => void;
  isUploading: boolean;
}

export const UploadZone: React.FC<UploadZoneProps> = ({ onUpload, isUploading }) => {
  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      if (acceptedFiles.length > 0) {
        onUpload(acceptedFiles[0]);
      }
    },
    [onUpload],
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "text/html": [".html", ".htm"],
      "text/xml": [".xml"],
    },
    disabled: isUploading,
    multiple: false,
  });

  return (
    <div
      {...getRootProps()}
      className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-colors duration-200 flex flex-col items-center justify-center
        ${
          isDragActive
            ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20"
            : "border-gray-300 dark:border-gray-700 hover:border-blue-400 hover:bg-gray-50 dark:hover:bg-gray-800/50"
        }
        ${isUploading ? "opacity-50 cursor-not-allowed" : ""}
      `}
    >
      <input {...getInputProps()} />
      <UploadCloud className="w-16 h-16 text-gray-400 mb-4" />
      {isUploading ? (
        <p className="text-lg font-medium text-gray-700 dark:text-gray-300">
          Uploading document...
        </p>
      ) : isDragActive ? (
        <p className="text-lg font-medium text-blue-600 dark:text-blue-400">
          Drop the file here ...
        </p>
      ) : (
        <>
          <p className="text-lg font-medium text-gray-700 dark:text-gray-300 mb-2">
            Drag & drop a document here, or click to select
          </p>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Supports PDF, HTML, XML (Max 50MB)
          </p>
        </>
      )}
    </div>
  );
};

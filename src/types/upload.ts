export interface UploadedFile {
  id: string;
  original_filename: string;
  stored_filename: string;
  file_size: number;
  file_hash: string;
  mime_type: string;
  language: string;
  uploaded_at: string;
  review_id?: string | null;
}

export interface BatchTaskStatus {
  id: string;
  task_type: string;
  status: "PENDING" | "RUNNING" | "COMPLETED" | "FAILED";
  filename?: string;
  total_files: number;
  processed_files: number;
  failed_files: number;
  progress_percentage: number;
  started_at?: string;
  completed_at?: string;
  error_message?: string;
  output_path?: string;
  processing_time?: number;
}

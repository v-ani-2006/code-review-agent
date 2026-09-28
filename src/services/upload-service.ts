import { apiClient } from "./api-client";
import { BatchTaskStatus, UploadedFile } from "@/types/upload";

export const uploadService = {
  async uploadSingleFile(file: File, language = "python"): Promise<UploadedFile> {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("language", language);

    const response = await apiClient.post<UploadedFile>("/upload/single", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return response.data;
  },

  async uploadArchive(file: File): Promise<{ task_id: string; message: string; total_files?: number }> {
    const formData = new FormData();
    formData.append("file", file);

    const response = await apiClient.post("/upload/archive", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return response.data;
  },

  async getBatchStatus(taskId: string): Promise<BatchTaskStatus> {
    const response = await apiClient.get<BatchTaskStatus>(`/batch/status/${taskId}`);
    return response.data;
  },

  async getUploadedFiles(page = 1, pageSize = 20): Promise<{ items: UploadedFile[]; total: number }> {
    const response = await apiClient.get(`/upload/files?page=${page}&page_size=${pageSize}`);
    return response.data;
  },
};

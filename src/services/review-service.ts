import { apiClient } from "./api-client";
import { AIReviewResponse, ReviewReport } from "@/types/review";

export const reviewService = {
  // Fast AST + Complexity static review
  async analyzeText(code: string, filename = "main.py", language = "python"): Promise<ReviewReport> {
    const response = await apiClient.post<ReviewReport>("/review/text", {
      code,
      filename,
      language,
    });
    return response.data;
  },

  // Deep Gemini 2.5 Flash review
  async aiReview(code: string, language = "python", detailLevel = "comprehensive"): Promise<AIReviewResponse> {
    const response = await apiClient.post<AIReviewResponse>("/ai/review", {
      code,
      language,
      detail_level: detailLevel,
    });
    return response.data;
  },

  // Explain code complexity and execution flow
  async explainCode(code: string, language = "python"): Promise<{ explanation: string; time_complexity: string; space_complexity: string }> {
    const response = await apiClient.post("/ai/explain", {
      code,
      language,
    });
    return response.data;
  },

  // Automated performance optimizations
  async optimizeCode(code: string, language = "python"): Promise<{ optimized_code: string; optimization_notes: string; expected_gain: string }> {
    const response = await apiClient.post("/ai/optimize", {
      code,
      language,
    });
    return response.data;
  },

  // Automated CVE & bug fix
  async fixBugs(code: string, language = "python", issueDescription = ""): Promise<{ fixed_code: string; explanation: string; diff: string }> {
    const response = await apiClient.post("/ai/bugfix", {
      code,
      language,
      issue_description: issueDescription,
    });
    return response.data;
  },

  // Generate docstrings and API docs
  async generateDocs(code: string, language = "python", docFormat = "google"): Promise<{ documented_code: string; markdown_docs: string }> {
    const response = await apiClient.post("/ai/documentation", {
      code,
      language,
      doc_format: docFormat,
    });
    return response.data;
  },

  // Generate Pytest unit tests
  async generateTests(code: string, language = "python", framework = "pytest"): Promise<{ test_code: string; test_cases_count: number }> {
    const response = await apiClient.post("/ai/tests", {
      code,
      language,
      framework,
    });
    return response.data;
  },

  // Generator endpoints
  async generateReadme(code: string): Promise<{ readme_markdown: string }> {
    const response = await apiClient.post("/generators/readme", { code });
    return response.data;
  },

  async generateArchitecture(code: string): Promise<{ architecture_markdown: string; mermaid_diagram: string }> {
    const response = await apiClient.post("/generators/architecture", { code });
    return response.data;
  },

  async generateChangelog(code: string): Promise<{ changelog_markdown: string }> {
    const response = await apiClient.post("/generators/changelog", { code });
    return response.data;
  },
};

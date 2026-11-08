export interface AuthUser {
  id: string;
  email: string;
  name: string;
}

export interface EmailCodeChallenge {
  userId: string;
  email: string;
  expiresAt: number;
}

export interface DocumentInfo {
  filename: string;
  chunksCount?: number;
}

export interface Citation {
  sentence: string;
  page: number;
  filename?: string | null;
}

export interface AnswerResponse {
  answer: string;
  citations: Citation[];
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  text: string;
  citations?: Citation[];
  sourceFilenames?: string[];
}

export interface ChatThread {
  notebookId: string;
  messages: ChatMessage[];
  updatedAt: string;
}

export interface QueryError {
  message: string;
  query: string;
}

export interface SavedNote {
  id: string;
  notebookId: string;
  title: string;
  text: string;
  citations: Citation[];
  createdAt: string;
  updatedAt: string;
}

export interface Notebook {
  id: string;
  title: string;
  sourceFilenames: string[];
  createdAt: string;
  updatedAt: string;
}

export interface UploadTask {
  id: string;
  filename: string;
  status: "waiting" | "processing" | "done" | "error";
  message?: string;
}

export interface HealthResponse {
  status: string;
  config: {
    groq_api_key_loaded: boolean;
    chroma_host_loaded: boolean;
  };
}

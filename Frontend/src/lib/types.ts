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

export interface HealthResponse {
  status: string;
  config: {
    groq_api_key_loaded: boolean;
    chroma_host_loaded: boolean;
  };
}

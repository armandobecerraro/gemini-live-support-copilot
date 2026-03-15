export interface IssueRequest {
  description: string;
  logs?: string;
  image_base64?: string;
  session_id?: string;
}

export interface Hypothesis {
  description: string;
  confidence: number;
  evidence: string[];
}

export interface SuggestedAction {
  id: string;
  title: string;
  description: string;
  requires_confirmation: boolean;
  is_destructive: boolean;
}

export interface AgentResponse {
  session_id: string;
  correlation_id: string;
  what_i_understood: string;
  what_i_see?: string;
  root_cause_summary?: string;
  recommendations: string[];
  next_action?: string;
  hypotheses: Hypothesis[];
  confidence: number;
  needs_more_info: boolean;
  suggested_actions: SuggestedAction[];
}

export type SessionStatus = 'idle' | 'loading' | 'active' | 'error';

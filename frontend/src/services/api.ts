import axios from 'axios';
import { IssueRequest, AgentResponse } from '@/types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';
const API_KEY = process.env.NEXT_PUBLIC_BACKEND_API_KEY || '';

const client = axios.create({
  baseURL: API_URL,
  timeout: 30000,
  headers: { 
    'Content-Type': 'application/json',
    ...(API_KEY ? { 'X-API-Key': API_KEY } : {})
  },
});

export const analyzeIssue = async (request: IssueRequest): Promise<AgentResponse> => {
  const { data } = await client.post<AgentResponse>('/agent/issue', request);
  return data;
};

export const confirmAction = async (
  sessionId: string,
  actionId: string,
  approved: boolean
): Promise<{ action_id: string; status: string }> => {
  const { data } = await client.post('/agent/confirm-action', { session_id: sessionId, action_id: actionId, approved });
  return data;
};

export const getSessionReport = async (sessionId: string) => {
  const { data } = await client.get(`/session/${sessionId}/report`);
  return data;
};

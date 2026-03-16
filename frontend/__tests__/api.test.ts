import * as api from '../src/services/api';
import axios from 'axios';

const mockPost = jest.fn();
const mockGet = jest.fn();

jest.mock('axios', () => ({
  create: jest.fn(() => ({
    post: (...args: any[]) => mockPost(...args),
    get: (...args: any[]) => mockGet(...args),
  })),
}));

describe('API Service', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  it('analyzeIssue calls the correct endpoint', async () => {
    const mockRequest = { description: 'test' };
    const mockResponse = { session_id: '123' };
    mockPost.mockResolvedValue({ data: mockResponse });

    const result = await api.analyzeIssue(mockRequest as any);

    expect(mockPost).toHaveBeenCalledWith('/agent/issue', mockRequest);
    expect(result).toEqual(mockResponse);
  });

  it('confirmAction calls the correct endpoint', async () => {
    mockPost.mockResolvedValue({ data: { action_id: 'a1', status: 'approved' } });

    const result = await api.confirmAction('s1', 'a1', true);

    expect(mockPost).toHaveBeenCalledWith('/agent/confirm-action', {
      session_id: 's1',
      action_id: 'a1',
      approved: true,
    });
    expect(result.status).toBe('approved');
  });

  it('getSessionReport calls the correct endpoint', async () => {
    mockGet.mockResolvedValue({ data: { report: 'md' } });

    const result = await api.getSessionReport('s1');

    expect(mockGet).toHaveBeenCalledWith('/session/s1/report');
    expect(result.report).toBe('md');
  });
});

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import Page from '@/app/page';
import * as api from '@/services/api';

jest.mock('@/services/api');
const mockedApi = api as jest.Mocked<typeof api>;

// Mock SpeechRecognition globally for integration tests
const mockStart = jest.fn();
const mockStop = jest.fn();
(window as any).webkitSpeechRecognition = jest.fn().mockImplementation(() => ({
  start: mockStart,
  stop: mockStop,
  continuous: false,
  interimResults: false,
  lang: '',
  onresult: null,
}));

// Mock window.alert
window.alert = jest.fn();

describe('Frontend Integration', () => {
  it('submits an incident and displays the response', async () => {
    const mockResponse = {
      session_id: 'test-session',
      correlation_id: 'test-correlation',
      what_i_understood: 'I understood there is a 500 error.',
      what_i_see: 'I see a screen with errors.',
      recommendations: ['Check DB', 'Scale connections'],
      hypotheses: [
        { description: 'Database is down', confidence: 0.9, evidence: ['Log 500 error'] }
      ],
      suggested_actions: [
        { id: '1', title: 'Restart Database', description: 'Restarts the pg service', requires_confirmation: true, is_destructive: true }
      ],
      root_cause_summary: 'Database connection failure',
      confidence: 0.9,
      needs_more_info: false
    };

    mockedApi.analyzeIssue.mockResolvedValueOnce(mockResponse);

    render(<Page />);

    // Fill the description
    const textarea = screen.getByPlaceholderText(/Briefly describe the anomaly.../i);
    fireEvent.change(textarea, { target: { value: 'My database is failing' } });

    // Click analyze
    const analyzeButton = screen.getByRole('button', { name: /Analyze Incident/i });
    fireEvent.click(analyzeButton);

    // Should show loading state
    expect(screen.getByText(/ENGINEERING ANALYSIS.../i)).toBeInTheDocument();

    // Wait for response
    await waitFor(() => {
      expect(screen.getAllByText(/Database connection failure/i)[0]).toBeInTheDocument();
    });

    expect(screen.getByText(/I understood there is a 500 error./i)).toBeInTheDocument();
    expect(screen.getByText(/Database is down/i)).toBeInTheDocument();
    expect(screen.getByText(/Restart Database/i)).toBeInTheDocument();

    // Test action confirmation
    mockedApi.confirmAction.mockResolvedValueOnce({ action_id: '1', status: 'approved' });
    const executeButton = screen.getByRole('button', { name: /Execute Protocol/i });
    fireEvent.click(executeButton);
    await waitFor(() => {
      expect(mockedApi.confirmAction).toHaveBeenCalledWith('test-session', '1', true);
    });

    // Test action rejection
    mockedApi.confirmAction.mockResolvedValueOnce({ action_id: '1', status: 'rejected' });
    const ignoreButton = screen.getByRole('button', { name: /Ignore/i });
    fireEvent.click(ignoreButton);
    await waitFor(() => {
      expect(mockedApi.confirmAction).toHaveBeenCalledWith('test-session', '1', false);
    });
  });

  it('handles API error during analysis', async () => {
    mockedApi.analyzeIssue.mockRejectedValueOnce({
      response: { data: { error: 'Service Unavailable' } }
    });

    render(<Page />);
    const textarea = screen.getByPlaceholderText(/Briefly describe the anomaly.../i);
    fireEvent.change(textarea, { target: { value: 'Trigger error' } });
    const analyzeButton = screen.getByRole('button', { name: /Analyze Incident/i });
    fireEvent.click(analyzeButton);

    await waitFor(() => {
      expect(screen.getByText(/Service Unavailable/i)).toBeInTheDocument();
    });
  });

  it('handles action confirmation error', async () => {
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
    const mockResponse = {
      session_id: 's1',
      suggested_actions: [{ id: '1', title: 'Action Title', description: 'Action Desc', is_destructive: false }],
      hypotheses: [],
      recommendations: [],
      what_i_understood: 'Understood',
      confidence: 0.5,
      needs_more_info: false
    };
    mockedApi.analyzeIssue.mockResolvedValueOnce(mockResponse as any);
    mockedApi.confirmAction.mockRejectedValueOnce(new Error('Failed'));

    render(<Page />);
    const textarea = screen.getByPlaceholderText(/Briefly describe the anomaly.../i);
    fireEvent.change(textarea, { target: { value: 'Something' } });
    fireEvent.click(screen.getByRole('button', { name: /Analyze Incident/i }));
    
    await waitFor(() => screen.getByText(/Action Title/i));
    
    fireEvent.click(screen.getByRole('button', { name: /Execute Protocol/i }));
    await waitFor(() => {
      expect(consoleSpy).toHaveBeenCalledWith('Failed to confirm action', expect.anything());
    });
    consoleSpy.mockRestore();
  });

  it('resets the workspace when clicking the reset button', async () => {
    render(<Page />);

    const textarea = screen.getByPlaceholderText(/Briefly describe the anomaly.../i) as HTMLTextAreaElement;
    fireEvent.change(textarea, { target: { value: 'Something to clear' } });
    expect(textarea.value).toBe('Something to clear');

    const resetButton = screen.getByTitle(/Reset Workspace/i);
    fireEvent.click(resetButton);

    expect(textarea.value).toBe('');
  });

  it('toggles recording state', async () => {
    render(<Page />);
    const startButton = screen.getByRole('button', { name: /Start Analysis/i });
    fireEvent.click(startButton);
    
    expect(screen.getByRole('button', { name: /Stop Recording/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Stop Recording/i })).toHaveClass('animate-pulse');
    
    fireEvent.click(screen.getByRole('button', { name: /Stop Recording/i }));
    expect(screen.getByRole('button', { name: /Start Analysis/i })).toBeInTheDocument();
  });
});

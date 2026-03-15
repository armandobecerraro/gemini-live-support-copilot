import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import Page from '@/app/page';
import * as api from '@/services/api';

jest.mock('@/services/api');
const mockedApi = api as jest.Mocked<typeof api>;

describe('Frontend Integration', () => {
  it('submits an incident and displays the response', async () => {
    const mockResponse = {
      session_id: 'test-session',
      what_i_understood: 'I understood there is a 500 error.',
      what_i_see: 'I see a screen with errors.',
      hypotheses: [
        { description: 'Database is down', confidence: 0.9 }
      ],
      suggested_actions: [
        { id: '1', title: 'Restart Database', description: 'Restarts the pg service', is_destructive: true }
      ],
      root_cause_summary: 'Database connection failure',
      needs_more_info: false,
      correlation_id: 'test-correlation-id',
      recommendations: ['Check database connection pool'],
      confidence: 0.9
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
});

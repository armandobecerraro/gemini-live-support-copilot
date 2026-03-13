import { render, screen } from '@testing-library/react';
import Page from '@/app/page';

describe('Home Page', () => {
  it('renders the main heading', () => {
    render(<Page />);
    // Use getAllByText for both parts and check the first occurrences
    const supportSightParts = screen.getAllByText(/SupportSight/i);
    const liveParts = screen.getAllByText(/Live/i);
    
    expect(supportSightParts[0]).toBeInTheDocument();
    expect(liveParts[0]).toBeInTheDocument();
  });

  it('contains the start recording button', () => {
    render(<Page />);
    const button = screen.getByRole('button', { name: /Start Recording/i });
    expect(button).toBeInTheDocument();
  });
});

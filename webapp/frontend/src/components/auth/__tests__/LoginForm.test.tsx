import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import LoginForm from '../LoginForm';
import { AuthProvider } from '../../../contexts/AuthContext';

// Mock fetch globally
const mockFetch = jest.fn();
global.fetch = mockFetch;

describe('LoginForm', () => {
  beforeEach(() => {
    mockFetch.mockClear();
  });

  it('renders login form with username and password fields', () => {
    render(
      <AuthProvider>
        <LoginForm />
      </AuthProvider>
    );

    expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
  });

  it('shows validation errors for empty fields', async () => {
    render(
      <AuthProvider>
        <LoginForm />
      </AuthProvider>
    );

    const loginButton = screen.getByRole('button', { name: /login/i });
    fireEvent.click(loginButton);

    expect(await screen.findByText(/username is required/i)).toBeInTheDocument();
    expect(await screen.findByText(/password is required/i)).toBeInTheDocument();
  });

  it('handles successful login', async () => {
    const mockResponse = {
      access_token: 'fake-token',
      token_type: 'bearer'
    };

    mockFetch.mockImplementationOnce(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockResponse)
      })
    );

    render(
      <AuthProvider>
        <LoginForm />
      </AuthProvider>
    );

    await userEvent.type(screen.getByLabelText(/username/i), 'testuser');
    await userEvent.type(screen.getByLabelText(/password/i), 'password123');
    
    fireEvent.click(screen.getByRole('button', { name: /login/i }));

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/auth/login'),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({
            username: 'testuser',
            password: 'password123'
          })
        })
      );
    });
  });

  it('handles login failure', async () => {
    mockFetch.mockImplementationOnce(() =>
      Promise.resolve({
        ok: false,
        status: 401
      })
    );

    render(
      <AuthProvider>
        <LoginForm />
      </AuthProvider>
    );

    await userEvent.type(screen.getByLabelText(/username/i), 'wronguser');
    await userEvent.type(screen.getByLabelText(/password/i), 'wrongpass');
    
    fireEvent.click(screen.getByRole('button', { name: /login/i }));

    expect(await screen.findByText(/invalid username or password/i)).toBeInTheDocument();
  });
}); 
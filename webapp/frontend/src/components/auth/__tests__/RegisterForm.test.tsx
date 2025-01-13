import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import RegisterForm from '../RegisterForm';
import { AuthProvider } from '../../../contexts/AuthContext';

// Mock fetch globally
const mockFetch = jest.fn();
global.fetch = mockFetch;

describe('RegisterForm', () => {
  beforeEach(() => {
    mockFetch.mockClear();
  });

  it('renders registration form with all required fields', () => {
    render(
      <AuthProvider>
        <RegisterForm />
      </AuthProvider>
    );

    // Required fields
    expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/display name/i)).toBeInTheDocument();

    // Optional profile fields
    expect(screen.getByLabelText(/bio/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/avatar url/i)).toBeInTheDocument();
  });

  it('shows validation errors for empty required fields', async () => {
    render(
      <AuthProvider>
        <RegisterForm />
      </AuthProvider>
    );

    fireEvent.click(screen.getByRole('button', { name: /register/i }));

    expect(await screen.findByText(/username is required/i)).toBeInTheDocument();
    expect(await screen.findByText(/email is required/i)).toBeInTheDocument();
    expect(await screen.findByText(/password is required/i)).toBeInTheDocument();
    expect(await screen.findByText(/display name is required/i)).toBeInTheDocument();
  });

  it('validates email format', async () => {
    render(
      <AuthProvider>
        <RegisterForm />
      </AuthProvider>
    );

    await userEvent.type(screen.getByLabelText(/email/i), 'invalid-email');
    fireEvent.click(screen.getByRole('button', { name: /register/i }));

    expect(await screen.findByText(/invalid email format/i)).toBeInTheDocument();
  });

  it('validates password requirements', async () => {
    render(
      <AuthProvider>
        <RegisterForm />
      </AuthProvider>
    );

    await userEvent.type(screen.getByLabelText(/password/i), 'short');
    fireEvent.click(screen.getByRole('button', { name: /register/i }));

    expect(await screen.findByText(/password must be at least 8 characters/i)).toBeInTheDocument();
  });

  it('handles successful registration with profile data', async () => {
    const mockResponse = {
      id: 'test-id',
      username: 'testuser',
      email: 'test@example.com',
      display_name: 'Test User',
      bio: 'Test bio',
      avatar_url: 'https://example.com/avatar.jpg',
      is_online: true
    };

    mockFetch.mockImplementationOnce(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockResponse)
      })
    );

    render(
      <AuthProvider>
        <RegisterForm />
      </AuthProvider>
    );

    // Fill in required fields
    await userEvent.type(screen.getByLabelText(/username/i), 'testuser');
    await userEvent.type(screen.getByLabelText(/email/i), 'test@example.com');
    await userEvent.type(screen.getByLabelText(/password/i), 'password123');
    await userEvent.type(screen.getByLabelText(/display name/i), 'Test User');

    // Fill in optional profile fields
    await userEvent.type(screen.getByLabelText(/bio/i), 'Test bio');
    await userEvent.type(screen.getByLabelText(/avatar url/i), 'https://example.com/avatar.jpg');

    fireEvent.click(screen.getByRole('button', { name: /register/i }));

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/auth/register'),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({
            username: 'testuser',
            email: 'test@example.com',
            password: 'password123',
            display_name: 'Test User',
            bio: 'Test bio',
            avatar_url: 'https://example.com/avatar.jpg'
          })
        })
      );
    });
  });

  it('handles registration failure for duplicate username', async () => {
    mockFetch.mockImplementationOnce(() =>
      Promise.resolve({
        ok: false,
        status: 400,
        json: () => Promise.resolve({ detail: 'Username already exists' })
      })
    );

    render(
      <AuthProvider>
        <RegisterForm />
      </AuthProvider>
    );

    await userEvent.type(screen.getByLabelText(/username/i), 'existinguser');
    await userEvent.type(screen.getByLabelText(/email/i), 'test@example.com');
    await userEvent.type(screen.getByLabelText(/password/i), 'password123');
    await userEvent.type(screen.getByLabelText(/display name/i), 'Test User');

    fireEvent.click(screen.getByRole('button', { name: /register/i }));

    expect(await screen.findByText(/username already exists/i)).toBeInTheDocument();
  });
}); 
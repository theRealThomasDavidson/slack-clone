import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AuthProvider } from '../../../contexts/AuthContext';
import ProfileSettings from '../ProfileSettings';

// Mock fetch globally
const mockFetch = jest.fn();
global.fetch = mockFetch;

describe('Profile Operations', () => {
  const mockUser = {
    id: 'test-user-id',
    username: 'testuser',
    email: 'test@example.com',
    display_name: 'Test User',
    bio: 'Original bio',
    avatar_url: 'https://example.com/avatar.jpg',
    is_online: true
  };

  beforeEach(() => {
    mockFetch.mockClear();
    // Mock initial user data fetch
    mockFetch.mockImplementationOnce(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockUser)
      })
    );
  });

  it('loads and displays current profile information', async () => {
    render(
      <AuthProvider>
        <ProfileSettings />
      </AuthProvider>
    );

    expect(await screen.findByDisplayValue('Test User')).toBeInTheDocument();
    expect(await screen.findByDisplayValue('Original bio')).toBeInTheDocument();
    expect(await screen.findByDisplayValue('https://example.com/avatar.jpg')).toBeInTheDocument();
  });

  it('updates display name and bio', async () => {
    const updatedUser = {
      ...mockUser,
      display_name: 'Updated Name',
      bio: 'Updated bio'
    };

    mockFetch.mockImplementationOnce(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(updatedUser)
      })
    );

    render(
      <AuthProvider>
        <ProfileSettings />
      </AuthProvider>
    );

    // Wait for form to load with current data
    const displayNameInput = await screen.findByLabelText(/display name/i);
    const bioInput = await screen.findByLabelText(/bio/i);

    // Update fields
    await userEvent.clear(displayNameInput);
    await userEvent.clear(bioInput);
    await userEvent.type(displayNameInput, 'Updated Name');
    await userEvent.type(bioInput, 'Updated bio');

    // Submit form
    fireEvent.click(screen.getByRole('button', { name: /save changes/i }));

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/users/profile'),
        expect.objectContaining({
          method: 'PUT',
          body: JSON.stringify({
            display_name: 'Updated Name',
            bio: 'Updated bio',
            avatar_url: 'https://example.com/avatar.jpg'
          })
        })
      );
    });

    // Success message should be shown
    expect(await screen.findByText(/profile updated successfully/i)).toBeInTheDocument();
  });

  it('validates avatar URL format', async () => {
    render(
      <AuthProvider>
        <ProfileSettings />
      </AuthProvider>
    );

    const avatarInput = await screen.findByLabelText(/avatar url/i);
    await userEvent.clear(avatarInput);
    await userEvent.type(avatarInput, 'invalid-url');

    fireEvent.click(screen.getByRole('button', { name: /save changes/i }));

    expect(await screen.findByText(/please enter a valid url/i)).toBeInTheDocument();
  });

  it('handles profile update failure', async () => {
    mockFetch
      .mockImplementationOnce(() => Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockUser)
      }))
      .mockImplementationOnce(() => Promise.resolve({
        ok: false,
        status: 500,
        json: () => Promise.resolve({ detail: 'Internal server error' })
      }));

    render(
      <AuthProvider>
        <ProfileSettings />
      </AuthProvider>
    );

    const displayNameInput = await screen.findByLabelText(/display name/i);
    await userEvent.clear(displayNameInput);
    await userEvent.type(displayNameInput, 'Failed Update');

    fireEvent.click(screen.getByRole('button', { name: /save changes/i }));

    expect(await screen.findByText(/failed to update profile/i)).toBeInTheDocument();
  });

  it('shows loading state during update', async () => {
    mockFetch
      .mockImplementationOnce(() => Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockUser)
      }))
      .mockImplementationOnce(() => new Promise(resolve => setTimeout(() => resolve({
        ok: true,
        json: () => Promise.resolve(mockUser)
      }), 1000)));

    render(
      <AuthProvider>
        <ProfileSettings />
      </AuthProvider>
    );

    const displayNameInput = await screen.findByLabelText(/display name/i);
    await userEvent.clear(displayNameInput);
    await userEvent.type(displayNameInput, 'New Name');

    fireEvent.click(screen.getByRole('button', { name: /save changes/i }));

    // Save button should show loading state
    expect(screen.getByRole('button', { name: /saving/i })).toBeInTheDocument();
  });
}); 
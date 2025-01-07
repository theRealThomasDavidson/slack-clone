import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AuthProvider } from '../../../contexts/AuthContext';
import { WebSocketProvider } from '../../../contexts/WebSocketContext';
import ChannelList from '../ChannelList';
import MessageList from '../MessageList';
import MessageInput from '../MessageInput';

// Mock fetch globally
const mockFetch = jest.fn();
global.fetch = mockFetch;

describe('Channel Operations', () => {
  beforeEach(() => {
    mockFetch.mockClear();
  });

  it('creates a new channel', async () => {
    const mockResponse = {
      id: 'test-channel-id',
      name: 'test-channel',
      description: 'Test Channel Description',
      owner_id: 'test-user-id',
      members: ['test-user-id']
    };

    mockFetch.mockImplementationOnce(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockResponse)
      })
    );

    render(
      <AuthProvider>
        <ChannelList onChannelSelect={() => {}} />
      </AuthProvider>
    );

    // Click create channel button
    fireEvent.click(screen.getByRole('button', { name: /create channel/i }));

    // Fill in channel details
    await userEvent.type(screen.getByLabelText(/channel name/i), 'test-channel');
    await userEvent.type(screen.getByLabelText(/description/i), 'Test Channel Description');

    // Submit form
    fireEvent.click(screen.getByRole('button', { name: /create/i }));

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/channels'),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({
            name: 'test-channel',
            description: 'Test Channel Description'
          })
        })
      );
    });

    // New channel should appear in the list
    expect(await screen.findByText('test-channel')).toBeInTheDocument();
  });

  it('sends and receives messages in a channel', async () => {
    const channelId = 'test-channel-id';
    const mockMessage = {
      id: 'msg-1',
      content: 'Hello channel!',
      channel_id: channelId,
      username: 'testuser',
      user_id: 'test-user-id',
      timestamp: new Date().toISOString()
    };

    mockFetch.mockImplementationOnce(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve([mockMessage])
      })
    );

    render(
      <AuthProvider>
        <WebSocketProvider>
          <MessageList channelId={channelId} />
          <MessageInput channelId={channelId} />
        </WebSocketProvider>
      </AuthProvider>
    );

    // Type and send a message
    await userEvent.type(screen.getByPlaceholderText(/type a message/i), 'Hello channel!');
    fireEvent.click(screen.getByRole('button', { name: /send/i }));

    // Message should appear in the list
    expect(await screen.findByText('Hello channel!')).toBeInTheDocument();
  });

  it('shows error when channel name already exists', async () => {
    mockFetch.mockImplementationOnce(() =>
      Promise.resolve({
        ok: false,
        status: 400,
        json: () => Promise.resolve({ detail: 'Channel name already exists' })
      })
    );

    render(
      <AuthProvider>
        <ChannelList onChannelSelect={() => {}} />
      </AuthProvider>
    );

    fireEvent.click(screen.getByRole('button', { name: /create channel/i }));
    await userEvent.type(screen.getByLabelText(/channel name/i), 'existing-channel');
    fireEvent.click(screen.getByRole('button', { name: /create/i }));

    expect(await screen.findByText(/channel name already exists/i)).toBeInTheDocument();
  });

  it('joins an existing channel', async () => {
    const mockChannel = {
      id: 'test-channel-id',
      name: 'test-channel',
      description: 'Test Channel',
      owner_id: 'other-user-id',
      members: ['other-user-id']
    };

    mockFetch
      .mockImplementationOnce(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve([mockChannel])
        })
      )
      .mockImplementationOnce(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve({
            ...mockChannel,
            members: [...mockChannel.members, 'test-user-id']
          })
        })
      );

    render(
      <AuthProvider>
        <ChannelList onChannelSelect={() => {}} />
      </AuthProvider>
    );

    // Find and click join button for the channel
    const joinButton = await screen.findByRole('button', { name: /join/i });
    fireEvent.click(joinButton);

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/channels/test-channel/join'),
        expect.objectContaining({
          method: 'POST'
        })
      );
    });

    // Join button should be replaced with a "Joined" indicator
    expect(screen.queryByRole('button', { name: /join/i })).not.toBeInTheDocument();
    expect(screen.getByText(/joined/i)).toBeInTheDocument();
  });

  it('leaves a channel successfully', async () => {
    const mockChannel = {
      id: 'test-channel-id',
      name: 'test-channel',
      description: 'Test Channel',
      owner_id: 'other-user-id',
      members: ['other-user-id', 'test-user-id']
    };

    mockFetch
      .mockImplementationOnce(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve([mockChannel])
        })
      )
      .mockImplementationOnce(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve({
            ...mockChannel,
            members: ['other-user-id']
          })
        })
      );

    render(
      <AuthProvider>
        <ChannelList onChannelSelect={() => {}} />
      </AuthProvider>
    );

    // Find and click leave button for the channel
    const leaveButton = await screen.findByRole('button', { name: /leave/i });
    fireEvent.click(leaveButton);

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/channels/test-channel/leave'),
        expect.objectContaining({
          method: 'POST'
        })
      );
    });

    // Leave button should be replaced with a "Join" button
    expect(screen.queryByRole('button', { name: /leave/i })).not.toBeInTheDocument();
    expect(screen.getByRole('button', { name: /join/i })).toBeInTheDocument();
  });

  it('deletes a channel when user is owner', async () => {
    const mockChannel = {
      id: 'test-channel-id',
      name: 'test-channel',
      description: 'Test Channel',
      owner_id: 'test-user-id',
      members: ['test-user-id']
    };

    mockFetch
      .mockImplementationOnce(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve([mockChannel])
        })
      )
      .mockImplementationOnce(() =>
        Promise.resolve({
          ok: true,
          status: 204
        })
      );

    render(
      <AuthProvider>
        <ChannelList onChannelSelect={() => {}} />
      </AuthProvider>
    );

    // Find and click delete button for the channel
    const deleteButton = await screen.findByRole('button', { name: /delete/i });
    fireEvent.click(deleteButton);

    // Confirm deletion in the modal
    const confirmButton = await screen.findByRole('button', { name: /confirm/i });
    fireEvent.click(confirmButton);

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/channels/test-channel'),
        expect.objectContaining({
          method: 'DELETE'
        })
      );
    });

    // Channel should be removed from the list
    expect(screen.queryByText('test-channel')).not.toBeInTheDocument();
  });

  it('handles channel update', async () => {
    const mockChannel = {
      id: 'test-channel-id',
      name: 'test-channel',
      description: 'Test Channel',
      owner_id: 'test-user-id',
      members: ['test-user-id']
    };

    const updatedChannel = {
      ...mockChannel,
      name: 'updated-channel',
      description: 'Updated Description'
    };

    mockFetch
      .mockImplementationOnce(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve([mockChannel])
        })
      )
      .mockImplementationOnce(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve(updatedChannel)
        })
      );

    render(
      <AuthProvider>
        <ChannelList onChannelSelect={() => {}} />
      </AuthProvider>
    );

    // Find and click edit button for the channel
    const editButton = await screen.findByRole('button', { name: /edit/i });
    fireEvent.click(editButton);

    // Update channel details
    const nameInput = screen.getByLabelText(/channel name/i);
    const descriptionInput = screen.getByLabelText(/description/i);
    
    await userEvent.clear(nameInput);
    await userEvent.clear(descriptionInput);
    await userEvent.type(nameInput, 'updated-channel');
    await userEvent.type(descriptionInput, 'Updated Description');

    // Submit form
    fireEvent.click(screen.getByRole('button', { name: /save/i }));

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/channels/test-channel'),
        expect.objectContaining({
          method: 'PUT',
          body: JSON.stringify({
            name: 'updated-channel',
            description: 'Updated Description'
          })
        })
      );
    });

    // Updated channel details should appear in the list
    expect(await screen.findByText('updated-channel')).toBeInTheDocument();
    expect(await screen.findByText('Updated Description')).toBeInTheDocument();
  });

  it('handles network error when fetching channels', async () => {
    mockFetch.mockImplementationOnce(() =>
      Promise.reject(new Error('Network error'))
    );

    render(
      <AuthProvider>
        <ChannelList onChannelSelect={() => {}} />
      </AuthProvider>
    );

    expect(await screen.findByText(/error loading channels/i)).toBeInTheDocument();
    expect(await screen.findByRole('button', { name: /retry/i })).toBeInTheDocument();
  });

  it('handles unauthorized access to channel operations', async () => {
    mockFetch.mockImplementationOnce(() =>
      Promise.resolve({
        ok: false,
        status: 403,
        json: () => Promise.resolve({ detail: 'Not authorized to perform this action' })
      })
    );

    render(
      <AuthProvider>
        <ChannelList onChannelSelect={() => {}} />
      </AuthProvider>
    );

    // Try to create a channel
    fireEvent.click(screen.getByRole('button', { name: /create channel/i }));
    await userEvent.type(screen.getByLabelText(/channel name/i), 'new-channel');
    fireEvent.click(screen.getByRole('button', { name: /create/i }));

    expect(await screen.findByText(/not authorized to perform this action/i)).toBeInTheDocument();
  });
}); 
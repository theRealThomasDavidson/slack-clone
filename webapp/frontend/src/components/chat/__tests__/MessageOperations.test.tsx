import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AuthProvider } from '../../../contexts/AuthContext';
import { WebSocketProvider } from '../../../contexts/WebSocketContext';
import MessageList from '../MessageList';
import MessageInput from '../MessageInput';

// Mock fetch globally
const mockFetch = jest.fn();
global.fetch = mockFetch;

describe('Message Operations', () => {
  const channelId = 'test-channel-id';
  const userId = 'test-user-id';

  beforeEach(() => {
    mockFetch.mockClear();
  });

  it('loads message history when entering a channel', async () => {
    const mockMessages = [
      {
        id: 'msg-1',
        content: 'First message',
        channel_id: channelId,
        user_id: userId,
        username: 'testuser',
        timestamp: new Date().toISOString()
      },
      {
        id: 'msg-2',
        content: 'Second message',
        channel_id: channelId,
        user_id: 'other-user',
        username: 'otheruser',
        timestamp: new Date().toISOString()
      }
    ];

    mockFetch.mockImplementationOnce(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockMessages)
      })
    );

    render(
      <AuthProvider>
        <WebSocketProvider>
          <MessageList channelId={channelId} />
        </WebSocketProvider>
      </AuthProvider>
    );

    // Messages should be displayed
    expect(await screen.findByText('First message')).toBeInTheDocument();
    expect(await screen.findByText('Second message')).toBeInTheDocument();
  });

  it('sends a message with emoji', async () => {
    const mockMessage = {
      id: 'msg-1',
      content: 'Hello! 😊',
      channel_id: channelId,
      user_id: userId,
      username: 'testuser',
      timestamp: new Date().toISOString()
    };

    mockFetch.mockImplementationOnce(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockMessage)
      })
    );

    render(
      <AuthProvider>
        <WebSocketProvider>
          <MessageInput channelId={channelId} />
          <MessageList channelId={channelId} />
        </WebSocketProvider>
      </AuthProvider>
    );

    // Type message with emoji
    await userEvent.type(screen.getByPlaceholderText(/type a message/i), 'Hello! 😊');
    fireEvent.click(screen.getByRole('button', { name: /send/i }));

    // Message should appear with emoji
    expect(await screen.findByText('Hello! 😊')).toBeInTheDocument();
  });

  it('edits own message', async () => {
    const originalMessage = {
      id: 'msg-1',
      content: 'Original text',
      channel_id: channelId,
      user_id: userId,
      username: 'testuser',
      timestamp: new Date().toISOString()
    };

    const editedMessage = {
      ...originalMessage,
      content: 'Edited text'
    };

    mockFetch
      .mockImplementationOnce(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve([originalMessage])
        })
      )
      .mockImplementationOnce(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve(editedMessage)
        })
      );

    render(
      <AuthProvider>
        <WebSocketProvider>
          <MessageList channelId={channelId} />
        </WebSocketProvider>
      </AuthProvider>
    );

    // Find and click edit button on message
    const editButton = await screen.findByRole('button', { name: /edit/i });
    fireEvent.click(editButton);

    // Edit message
    const editInput = screen.getByDisplayValue('Original text');
    await userEvent.clear(editInput);
    await userEvent.type(editInput, 'Edited text');
    fireEvent.click(screen.getByRole('button', { name: /save/i }));

    // Verify edited message
    expect(await screen.findByText('Edited text')).toBeInTheDocument();
    expect(screen.queryByText('Original text')).not.toBeInTheDocument();
  });

  it('deletes own message', async () => {
    const mockMessage = {
      id: 'msg-1',
      content: 'Message to delete',
      channel_id: channelId,
      user_id: userId,
      username: 'testuser',
      timestamp: new Date().toISOString()
    };

    mockFetch
      .mockImplementationOnce(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve([mockMessage])
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
        <WebSocketProvider>
          <MessageList channelId={channelId} />
        </WebSocketProvider>
      </AuthProvider>
    );

    // Find and click delete button
    const deleteButton = await screen.findByRole('button', { name: /delete/i });
    fireEvent.click(deleteButton);

    // Confirm deletion
    const confirmButton = await screen.findByRole('button', { name: /confirm/i });
    fireEvent.click(confirmButton);

    // Message should be removed
    expect(screen.queryByText('Message to delete')).not.toBeInTheDocument();
  });

  it('handles message send failure', async () => {
    mockFetch.mockImplementationOnce(() =>
      Promise.resolve({
        ok: false,
        status: 500,
        json: () => Promise.resolve({ detail: 'Internal server error' })
      })
    );

    render(
      <AuthProvider>
        <WebSocketProvider>
          <MessageInput channelId={channelId} />
        </WebSocketProvider>
      </AuthProvider>
    );

    await userEvent.type(screen.getByPlaceholderText(/type a message/i), 'Failed message');
    fireEvent.click(screen.getByRole('button', { name: /send/i }));

    // Error message should be shown
    expect(await screen.findByText(/failed to send message/i)).toBeInTheDocument();
    expect(await screen.findByRole('button', { name: /retry/i })).toBeInTheDocument();
  });

  it('shows typing indicator when other users are typing', async () => {
    render(
      <AuthProvider>
        <WebSocketProvider>
          <MessageList channelId={channelId} />
        </WebSocketProvider>
      </AuthProvider>
    );

    // Simulate WebSocket message for typing indicator
    const ws = new WebSocket('ws://localhost');
    ws.onopen = () => {
      ws.send(JSON.stringify({
        type: 'typing',
        data: {
          channel_id: channelId,
          username: 'otheruser'
        }
      }));
    };

    // Typing indicator should appear
    expect(await screen.findByText(/otheruser is typing/i)).toBeInTheDocument();

    // Typing indicator should disappear after delay
    await waitFor(() => {
      expect(screen.queryByText(/otheruser is typing/i)).not.toBeInTheDocument();
    }, { timeout: 3000 });
  });

  it('handles message with markdown formatting', async () => {
    const mockMessage = {
      id: 'msg-1',
      content: '**Bold** and *italic* text with `code`',
      channel_id: channelId,
      user_id: userId,
      username: 'testuser',
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
        </WebSocketProvider>
      </AuthProvider>
    );

    // Message should be rendered with markdown formatting
    const message = await screen.findByTestId('message-content');
    expect(message).toContainHTML('<strong>Bold</strong>');
    expect(message).toContainHTML('<em>italic</em>');
    expect(message).toContainHTML('<code>code</code>');
  });
}); 
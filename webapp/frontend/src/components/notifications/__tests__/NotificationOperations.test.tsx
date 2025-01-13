import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AuthProvider } from '../../../contexts/AuthContext';
import { WebSocketProvider } from '../../../contexts/WebSocketContext';
import NotificationList from '../NotificationList';
import NotificationBadge from '../NotificationBadge';

// Mock fetch globally
const mockFetch = jest.fn();
global.fetch = mockFetch;

describe('Notification Operations', () => {
  const userId = 'test-user-id';
  const mockNotifications = [
    {
      id: 'notif-1',
      type: 'mention',
      content: '@testuser mentioned you in Test Channel',
      channel_id: 'channel-1',
      message_id: 'msg-1',
      created_at: new Date().toISOString(),
      read: false
    },
    {
      id: 'notif-2',
      type: 'channel_invite',
      content: 'You were invited to join New Channel',
      channel_id: 'channel-2',
      created_at: new Date().toISOString(),
      read: false
    }
  ];

  beforeEach(() => {
    mockFetch.mockClear();
    mockFetch.mockImplementationOnce(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockNotifications)
      })
    );
  });

  it('displays unread notifications count', async () => {
    render(
      <AuthProvider>
        <WebSocketProvider>
          <NotificationBadge />
        </WebSocketProvider>
      </AuthProvider>
    );

    expect(await screen.findByText('2')).toBeInTheDocument();
  });

  it('shows notification list with different types', async () => {
    render(
      <AuthProvider>
        <WebSocketProvider>
          <NotificationList />
        </WebSocketProvider>
      </AuthProvider>
    );

    expect(await screen.findByText(/@testuser mentioned you/i)).toBeInTheDocument();
    expect(await screen.findByText(/invited to join/i)).toBeInTheDocument();
  });

  it('marks notification as read when clicked', async () => {
    mockFetch
      .mockImplementationOnce(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockNotifications)
        })
      )
      .mockImplementationOnce(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ ...mockNotifications[0], read: true })
        })
      );

    render(
      <AuthProvider>
        <WebSocketProvider>
          <NotificationList />
        </WebSocketProvider>
      </AuthProvider>
    );

    const notification = await screen.findByText(/@testuser mentioned you/i);
    fireEvent.click(notification);

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/notifications/notif-1/read'),
        expect.objectContaining({
          method: 'POST'
        })
      );
    });

    // Notification should appear as read
    expect(notification).toHaveClass('read');
  });

  it('receives real-time notification for new message mention', async () => {
    render(
      <AuthProvider>
        <WebSocketProvider>
          <NotificationList />
        </WebSocketProvider>
      </AuthProvider>
    );

    // Simulate WebSocket message for new mention
    const ws = new WebSocket('ws://localhost');
    ws.onopen = () => {
      ws.send(JSON.stringify({
        type: 'notification',
        data: {
          id: 'notif-3',
          type: 'mention',
          content: '@otheruser mentioned you in Test Channel',
          channel_id: 'channel-1',
          message_id: 'msg-2',
          created_at: new Date().toISOString(),
          read: false
        }
      }));
    };

    // New notification should appear
    expect(await screen.findByText(/@otheruser mentioned you/i)).toBeInTheDocument();
  });

  it('clears all notifications', async () => {
    mockFetch
      .mockImplementationOnce(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockNotifications)
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
          <NotificationList />
        </WebSocketProvider>
      </AuthProvider>
    );

    // Click clear all button
    fireEvent.click(screen.getByRole('button', { name: /clear all/i }));

    // Confirm clear action
    const confirmButton = await screen.findByRole('button', { name: /confirm/i });
    fireEvent.click(confirmButton);

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/notifications/clear'),
        expect.objectContaining({
          method: 'POST'
        })
      );
    });

    // No notifications should be shown
    expect(screen.queryByText(/@testuser mentioned you/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/invited to join/i)).not.toBeInTheDocument();
  });

  it('shows notification preferences settings', async () => {
    const mockPreferences = {
      mentions: true,
      channel_invites: true,
      direct_messages: false
    };

    mockFetch
      .mockImplementationOnce(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockNotifications)
        })
      )
      .mockImplementationOnce(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockPreferences)
        })
      );

    render(
      <AuthProvider>
        <WebSocketProvider>
          <NotificationList />
        </WebSocketProvider>
      </AuthProvider>
    );

    // Open preferences
    fireEvent.click(screen.getByRole('button', { name: /preferences/i }));

    // Check preference toggles
    expect(screen.getByRole('switch', { name: /mentions/i })).toBeChecked();
    expect(screen.getByRole('switch', { name: /channel invites/i })).toBeChecked();
    expect(screen.getByRole('switch', { name: /direct messages/i })).not.toBeChecked();
  });

  it('updates notification preferences', async () => {
    mockFetch
      .mockImplementationOnce(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockNotifications)
        })
      )
      .mockImplementationOnce(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve({
            mentions: true,
            channel_invites: false,
            direct_messages: true
          })
        })
      );

    render(
      <AuthProvider>
        <WebSocketProvider>
          <NotificationList />
        </WebSocketProvider>
      </AuthProvider>
    );

    // Open preferences
    fireEvent.click(screen.getByRole('button', { name: /preferences/i }));

    // Toggle preferences
    fireEvent.click(screen.getByRole('switch', { name: /channel invites/i }));
    fireEvent.click(screen.getByRole('switch', { name: /direct messages/i }));

    // Save preferences
    fireEvent.click(screen.getByRole('button', { name: /save preferences/i }));

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/notifications/preferences'),
        expect.objectContaining({
          method: 'PUT',
          body: JSON.stringify({
            mentions: true,
            channel_invites: false,
            direct_messages: true
          })
        })
      );
    });

    // Success message should be shown
    expect(await screen.findByText(/preferences updated/i)).toBeInTheDocument();
  });
}); 
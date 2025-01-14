import '@testing-library/jest-dom';

// Mock WebSocket
class MockWebSocket {
  onmessage: ((event: MessageEvent) => void) | null = null;
  onclose: ((event: CloseEvent) => void) | null = null;
  onopen: ((event: Event) => void) | null = null;
  onerror: ((event: Event) => void) | null = null;
  readyState: number = WebSocket.CONNECTING;
  url: string = '';

  constructor(url: string) {
    this.url = url;
    setTimeout(() => {
      this.readyState = WebSocket.OPEN;
      if (this.onopen) {
        this.onopen(new Event('open'));
      }
    }, 0);
  }

  send(data: string): void {
    // Mock sending data
    if (this.onmessage) {
      const messageEvent = new MessageEvent('message', {
        data: data
      });
      setTimeout(() => this.onmessage?.(messageEvent), 0);
    }
  }

  close(): void {
    this.readyState = WebSocket.CLOSED;
    if (this.onclose) {
      const closeEvent = new CloseEvent('close');
      this.onclose(closeEvent);
    }
  }
}

// Replace the global WebSocket with our mock
global.WebSocket = MockWebSocket as any; 
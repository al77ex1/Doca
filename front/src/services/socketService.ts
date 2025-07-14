import { io, Socket } from 'socket.io-client';

class SocketService {
  private socket: Socket | null = null;
  private listeners: Map<string, Function[]> = new Map();

  connect(url: string = 'http://localhost:8000'): void {
    if (this.socket) {
      this.socket.disconnect();
    }

    this.socket = io(url);

    this.socket.on('connect', () => {
      console.log('Connected to WebSocket server');
    });

    this.socket.on('disconnect', () => {
      console.log('Disconnected from WebSocket server');
    });

    // Set up listeners for indexing events
    this.socket.on('indexing_started', (data) => {
      this.notifyListeners('indexing_started', data);
    });

    this.socket.on('indexing_progress', (data) => {
      this.notifyListeners('indexing_progress', data);
    });

    this.socket.on('indexing_completed', (data) => {
      this.notifyListeners('indexing_completed', data);
    });
    
    // Add listeners for error and status events
    this.socket.on('indexing_error', (data) => {
      console.error('Indexing error:', data);
      this.notifyListeners('indexing_error', data);
    });
    
    this.socket.on('indexing_status', (data) => {
      console.log('Indexing status:', data);
      this.notifyListeners('indexing_status', data);
    });
  }

  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }

  startIndexing(params: any): void {
    if (!this.socket) {
      console.error('Socket not connected');
      return;
    }
    this.socket.emit('start_indexing', params);
  }

  addListener(event: string, callback: Function): void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event)?.push(callback);
  }

  removeListener(event: string, callback: Function): void {
    if (!this.listeners.has(event)) return;
    
    const eventListeners = this.listeners.get(event);
    if (eventListeners) {
      const index = eventListeners.indexOf(callback);
      if (index !== -1) {
        eventListeners.splice(index, 1);
      }
    }
  }

  private notifyListeners(event: string, data: any): void {
    const callbacks = this.listeners.get(event);
    if (callbacks) {
      callbacks.forEach(callback => callback(data));
    }
  }
}

// Create singleton instance
const socketService = new SocketService();
export default socketService;

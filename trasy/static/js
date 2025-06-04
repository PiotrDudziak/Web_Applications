class NotificationManager {
  constructor() {
    this.eventSource = null;
    this.notificationContainer = null;
    this.MAX_NOTIFICATIONS = 5;
    this.NOTIFICATION_TIMEOUT = 5000; // 5 sekund dla toastów
    this.connectionAttempts = 0;
    this.MAX_CONNECTION_ATTEMPTS = 3;

    this.createNotificationContainer();

    // Opóźnienie początkowej próby połączenia
    setTimeout(() => {
      this.initializeEventSource();
    }, 2000);
  }

  initializeEventSource() {
    try {
      this.eventSource = new EventSource('/sse/notifications/');

      // Obsługa zdarzeń newBoard
      this.eventSource.addEventListener('newBoard', (event) => {
        const data = JSON.parse(event.data);
        const message = `Użytkownik ${data.creator_username} utworzył nową planszę: ${data.board_name}`;
        this.showNotification(message, 'newBoard', data.board_id);
      });

      // Obsługa zdarzeń newPath
      this.eventSource.addEventListener('newPath', (event) => {
        const data = JSON.parse(event.data);
        const message = `Użytkownik ${data.user_username} zapisał ścieżkę na planszy: ${data.board_name}`;
        this.showNotification(message, 'newPath', data.board_id);
      });

      // Obsługa błędów
      this.eventSource.onerror = () => {
        this.connectionAttempts++;

        // Pokaż błąd tylko po kilku nieudanych próbach
        if (this.connectionAttempts >= this.MAX_CONNECTION_ATTEMPTS) {
          console.error('Błąd połączenia SSE');
          this.showNotification('Utracono połączenie z serwerem powiadomień. Próba ponownego połączenia...', 'error');
        }

        // Ponowna próba połączenia po 2 sekundach
        setTimeout(() => {
          if (this.eventSource) {
            this.eventSource.close();
            this.initializeEventSource();
          }
        }, 2000);
      };

      // Powiadomienie o nawiązaniu połączenia
      this.eventSource.onopen = () => {
        console.log('Połączono z serwerem powiadomień');
        // Resetuj licznik prób przy udanym połączeniu
        this.connectionAttempts = 0;
      };

    } catch (error) {
      console.error('Błąd podczas inicjalizacji EventSource:', error);
    }
  }

  /**
   * Tworzy kontener na powiadomienia
   */
  createNotificationContainer() {
    // Sprawdź, czy kontener już istnieje
    if (document.getElementById('notification-container')) {
      this.notificationContainer = document.getElementById('notification-container');
      return;
    }

    // Utwórz nowy kontener
    this.notificationContainer = document.createElement('div');
    this.notificationContainer.id = 'notification-container';

    // Style dla kontenera
    Object.assign(this.notificationContainer.style, {
      position: 'fixed',
      top: '20px',
      right: '20px',
      zIndex: '1000',
      display: 'flex',
      flexDirection: 'column',
      gap: '10px'
    });

    document.body.appendChild(this.notificationContainer);
  }

showNotification(message, type, boardId) {
  if (!this.notificationContainer) return;

  // Utwórz element powiadomienia
  const notification = document.createElement('div');
  Object.assign(notification.style, {
    padding: '15px',
    backgroundColor: type === 'error' ? '#f44336' : '#4CAF50',
    color: 'white',
    borderRadius: '5px',
    boxShadow: '0 2px 5px rgba(0,0,0,0.2)',
    minWidth: '250px',
    maxWidth: '350px',
    opacity: '0',
    transition: 'opacity 0.3s'
  });

  // Dodaj tekst powiadomienia
  notification.textContent = message;

  // Dodaj interakcję tylko dla powiadomień typu newBoard
  if (boardId !== undefined && type === 'newBoard') {
    notification.style.cursor = 'pointer';
    notification.onclick = () => {
      window.location.href = `/board_view/${boardId}/`;
    };
  }

  // Pozostała część funkcji bez zmian
  this.notificationContainer.appendChild(notification);

  while (this.notificationContainer.children.length > this.MAX_NOTIFICATIONS) {
    this.notificationContainer.removeChild(this.notificationContainer.children[0]);
  }

  setTimeout(() => {
    notification.style.opacity = '1';
  }, 10);

  setTimeout(() => {
    notification.style.opacity = '0';
    setTimeout(() => {
      if (notification.parentNode === this.notificationContainer) {
        this.notificationContainer.removeChild(notification);
      }
    }, 300);
  }, this.NOTIFICATION_TIMEOUT);
}
}

// Inicjalizacja managera powiadomień po załadowaniu strony
document.addEventListener('DOMContentLoaded', () => {
  new NotificationManager();
});

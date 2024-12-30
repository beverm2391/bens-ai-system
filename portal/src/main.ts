import { app, BrowserWindow } from 'electron';
import { fileURLToPath } from 'url';
import path from 'path';

interface WindowConfig {
  width: number;
  height: number;
  webPreferences: {
    nodeIntegration: boolean;
    contextIsolation: boolean;
    preload: string;
  }
}

const createWindow = (): void => {
  const config: WindowConfig = {
    width: 800,
    height: 600,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    }
  };

  const mainWindow = new BrowserWindow(config);
  mainWindow.loadFile('../index.html');
};

app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
}); 
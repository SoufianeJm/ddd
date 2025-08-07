const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
    // Add any API methods you want to expose to the renderer
    getVersion: () => process.versions.electron,
    platform: process.platform
});

// Prevent new window creation
window.addEventListener('DOMContentLoaded', () => {
    // Override window.open to prevent popup windows
    window.open = () => {
        console.log('Window.open blocked for security');
        return null;
    };
});

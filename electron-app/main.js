const { app, BrowserWindow, dialog } = require('electron');
const { spawn } = require('child_process');
const path = require('path');
const axios = require('axios').default;

let mainWindow = null;
let djangoProcess = null;
let splashWindow = null;

const isDev = !app.isPackaged;
const DJANGO_HOST = '127.0.0.1';
const DJANGO_PORT = 8000;
const DJANGO_URL = `http://${DJANGO_HOST}:${DJANGO_PORT}`;

function createSplashWindow() {
  splashWindow = new BrowserWindow({
    width: 400,
    height: 300,
    frame: false,
    alwaysOnTop: true,
    transparent: true,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true
    }
  });

  const splashHTML = `
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {
                margin: 0;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                color: white;
            }
            .container {
                text-align: center;
                padding: 20px;
            }
            .spinner {
                border: 3px solid rgba(255,255,255,0.3);
                border-radius: 50%;
                border-top: 3px solid white;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 20px auto;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            h2 { margin: 10px 0; }
            p { margin: 5px 0; opacity: 0.8; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Facturation Desktop</h2>
            <div class="spinner"></div>
            <p>Starting application...</p>
        </div>
    </body>
    </html>
  `;

  splashWindow.loadURL(`data:text/html;charset=utf-8,${encodeURIComponent(splashHTML)}`);
}

function createMainWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    show: false,
    backgroundColor: '#ffffff', // Set a background color to prevent flashing
    icon: path.join(__dirname, 'assets', 'icon.png'),
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
      webSecurity: true
    },
    titleBarStyle: 'default',
    autoHideMenuBar: true
  });

  // Hide menu bar
  mainWindow.setMenuBarVisibility(false);

  let contentReady = false;

  // Only show window when everything is truly ready
  const showWindowWhenReady = () => {
    if (!contentReady) {
      contentReady = true;
      console.log('Content is fully ready, showing window');
      
      // Close splash and show main window
      if (splashWindow) {
        splashWindow.close();
        splashWindow = null;
      }
      
      mainWindow.show();
      mainWindow.focus();
    }
  };

  mainWindow.webContents.on('did-fail-load', () => {
    console.log('Failed to load Django app');
    showErrorDialog('Failed to connect to the application server. Please try restarting the application.');
  });

  // Wait for page to be fully loaded AND rendered
  mainWindow.webContents.on('did-finish-load', () => {
    console.log('Page finished loading, waiting for render...');
    
    // Wait a moment for rendering to complete
    setTimeout(() => {
      if (mainWindow && !mainWindow.isDestroyed()) {
        showWindowWhenReady();
      }
    }, 1000); // Increased delay to ensure everything is rendered
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Load the URL
  mainWindow.loadURL(DJANGO_URL);

  return mainWindow;
}

function findDjangoExecutable() {
  // Try to find Python executable in common locations
  const { execSync } = require('child_process');
  
  // Common Python executable names and paths
  const pythonCandidates = [
    'python',
    'python3', 
    'python3.10',
    'python3.11',
    'python3.12',
    'C:\\Python310\\python.exe',
    'C:\\Python311\\python.exe',
    'C:\\Python312\\python.exe',
    'C:\\Program Files\\Python310\\python.exe',
    'C:\\Program Files\\Python311\\python.exe',
    'C:\\Program Files\\Python312\\python.exe'
  ];
  
  for (const candidate of pythonCandidates) {
    try {
      execSync(`"${candidate}" --version`, { stdio: 'pipe', timeout: 3000 });
      console.log(`Found Python executable: ${candidate}`);
      return candidate;
    } catch (error) {
      // Continue to next candidate
    }
  }
  
  // Fallback to 'python' if nothing else works
  console.warn('No Python executable found in common locations, falling back to "python"');
  return 'python';
}

async function startDjangoServer() {
  return new Promise((resolve, reject) => {
    const djangoExePath = findDjangoExecutable();

    console.log('Starting Django server...');
    
    // Spawn Django process with environment settings
    let serverScript, workingDir;
    
    if (isDev) {
      // Development mode - use parent directory
      serverScript = path.join(__dirname, '..', 'django-backend', 'django_launcher.py');
      workingDir = path.join(__dirname, '..', 'django-backend');
    } else {
      // Production mode - files are in the resources directory
      serverScript = path.join(process.resourcesPath, 'django-backend', 'django_launcher.py');
      workingDir = path.join(process.resourcesPath, 'django-backend');
    }
    
    djangoProcess = spawn(djangoExePath, [serverScript], {
      cwd: workingDir, // Set working directory appropriately
      env: {
        ...process.env,
        DJANGO_SETTINGS_MODULE: 'slr_project.settings',
        PORT: DJANGO_PORT.toString()
      },
      stdio: ['pipe', 'pipe', 'pipe']
    });

    let serverStarted = false;

    djangoProcess.stdout.on('data', (data) => {
      const output = data.toString();
      console.log('Django stdout:', output);
      
      if (output.includes('Starting development server') || 
          output.includes('Quit the server with CONTROL-C') ||
          output.includes('Django version')) {
        if (!serverStarted) {
          serverStarted = true;
          console.log('Django server is starting...');
          // Wait a bit more to ensure server is ready
          setTimeout(resolve, 2000);
        }
      }
    });

    djangoProcess.stderr.on('data', (data) => {
      const error = data.toString();
      console.error('Django stderr:', error);
    });

    djangoProcess.on('error', (error) => {
      console.error('Failed to start Django process:', error);
      reject(error);
    });

    djangoProcess.on('exit', (code, signal) => {
      console.log(`Django process exited with code ${code} and signal ${signal}`);
      if (!serverStarted) {
        reject(new Error(`Django process exited with code ${code}`));
      }
    });

    // Fallback timeout
    setTimeout(() => {
      if (!serverStarted) {
        console.log('Django server timeout, proceeding anyway...');
        resolve();
      }
    }, 10000);
  });
}

async function waitForDjangoServer(maxAttempts = 30) {
  console.log('Waiting for Django server to be ready...');
  
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      const response = await axios.get(DJANGO_URL, { 
        timeout: 3000,
        validateStatus: () => true // Accept any status code
      });
      
      if (response.status === 200) {
        console.log(`Django server is fully ready (status ${response.status})`);
        // Extra delay to ensure static files are fully loaded
        await new Promise(resolve => setTimeout(resolve, 1500));
        return true;
      } else {
        console.log(`Django server responded with status ${response.status}, waiting...`);
      }
    } catch (error) {
      console.log(`Attempt ${attempt}/${maxAttempts}: Django server not ready yet...`);
    }
    
    await new Promise(resolve => setTimeout(resolve, 1000));
  }
  
  throw new Error('Django server failed to start within timeout period');
}

function showErrorDialog(message) {
  dialog.showMessageBox(null, {
    type: 'error',
    title: 'Application Error',
    message: 'Facturation Desktop Error',
    detail: message,
    buttons: ['OK']
  });
}

async function initializeApp() {
  try {
    createSplashWindow();
    
    console.log('Initializing Facturation Desktop...');
    
    // Start Django server
    await startDjangoServer();
    
    // Wait for server to be ready
    await waitForDjangoServer();
    
    // Create main window (it will handle showing itself when ready)
    createMainWindow();
    
  } catch (error) {
    console.error('Failed to initialize application:', error);
    
    if (splashWindow) {
      splashWindow.close();
      splashWindow = null;
    }
    
    showErrorDialog(`Failed to start the application: ${error.message}`);
    app.quit();
  }
}

// Prevent visual flickering
app.commandLine.appendSwitch('--disable-backgrounding-occluded-windows');
app.commandLine.appendSwitch('--disable-renderer-backgrounding');

app.whenReady().then(initializeApp);

app.on('window-all-closed', () => {
  // Terminate Django process
  if (djangoProcess) {
    console.log('Terminating Django process...');
    djangoProcess.kill('SIGTERM');
    
    // Force kill if still running after 5 seconds
    setTimeout(() => {
      if (djangoProcess && !djangoProcess.killed) {
        console.log('Force killing Django process...');
        djangoProcess.kill('SIGKILL');
      }
    }, 5000);
  }
  
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    initializeApp();
  }
});

app.on('before-quit', () => {
  if (djangoProcess) {
    djangoProcess.kill('SIGTERM');
  }
});

// Handle certificate errors for development
app.on('certificate-error', (event, webContents, url, error, certificate, callback) => {
  if (url.startsWith(DJANGO_URL)) {
    event.preventDefault();
    callback(true);
  } else {
    callback(false);
  }
});

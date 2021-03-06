const {app, BrowserWindow} = require('electron')

let win

function createWindow() {
  win = new BrowserWindow({width: 500, height: 650, icon:'assets/icon.png'})
  win.loadFile('index.html')
  win.setPosition(1100, 200)
  // win.webContents.openDevTools()
  win.on('closed', () => {
    win = null
  })
}

app.on('ready', createWindow)

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('activate', () => {
  if (win === null) {
    createWindow()
  }
})

// In this file you can include the rest of your app's specific main process
// code. You can also put them in separate files and require them here.



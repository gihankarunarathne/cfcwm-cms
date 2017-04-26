let express = require('express')
let app = express()
let serveIndex = require('serve-index')
let path = require('path')

const HOST = ""
const PORT = 8080

serveIndexOpts = {
	view: 'details'
}

app.use(serveIndex(path.join(__dirname, '../data'), serveIndexOpts));
app.use(express.static(path.join(__dirname, '../data')))

// app.get('/cfcwm', function (req, res) {
//   res.send('Welcome to CFCWM!')
// })

app.listen(PORT, function () {
  console.log('File Server: listening on port ', PORT)
})
import { CssBaseline, ThemeProvider, createTheme } from '@mui/material'
import { Container, AppBar, Toolbar, Typography, Box } from '@mui/material'
import './App.css'
import Indexer from './components/Indexer'

// Create a theme instance
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ flexGrow: 1 }}>
        <AppBar position="static">
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              Doca - Document Indexer
            </Typography>
          </Toolbar>
        </AppBar>
        <Container maxWidth="lg" sx={{ mt: 4 }}>
          <Indexer />
        </Container>
      </Box>
    </ThemeProvider>
  )
}

export default App

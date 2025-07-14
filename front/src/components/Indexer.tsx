import { useState, useEffect } from 'react';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';
import Paper from '@mui/material/Paper';
import LinearProgress from '@mui/material/LinearProgress';
import FormControlLabel from '@mui/material/FormControlLabel';
import Checkbox from '@mui/material/Checkbox';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Alert from '@mui/material/Alert';
import Snackbar from '@mui/material/Snackbar';
import Stack from '@mui/material/Stack';
import socketService from '../services/socketService';

interface IndexingProgress {
  current: number;
  total: number;
  percentage: number;
  file_path: string;
  chunks_indexed: number;
}

interface IndexingCompleted {
  total_files: number;
  total_chunks: number;
}

const Indexer = () => {
  const [directory, setDirectory] = useState<string>('/path/to/documents');
  const [recursive, setRecursive] = useState<boolean>(true);
  const [isIndexing, setIsIndexing] = useState<boolean>(false);
  const [progress, setProgress] = useState<IndexingProgress | null>(null);
  const [completed, setCompleted] = useState<IndexingCompleted | null>(null);
  const [showSuccess, setShowSuccess] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Connect to WebSocket server
    socketService.connect();

    // Set up event listeners
    socketService.addListener('indexing_started', handleIndexingStarted);
    socketService.addListener('indexing_progress', handleIndexingProgress);
    socketService.addListener('indexing_completed', handleIndexingCompleted);
    socketService.addListener('indexing_error', handleIndexingError);
    socketService.addListener('indexing_status', handleIndexingStatus);

    // Cleanup on unmount
    return () => {
      socketService.removeListener('indexing_started', handleIndexingStarted);
      socketService.removeListener('indexing_progress', handleIndexingProgress);
      socketService.removeListener('indexing_completed', handleIndexingCompleted);
      socketService.removeListener('indexing_error', handleIndexingError);
      socketService.removeListener('indexing_status', handleIndexingStatus);
      socketService.disconnect();
    };
  }, []);

  const handleIndexingStarted = (data: any) => {
    console.log('Indexing started:', data);
    setIsIndexing(true);
    setProgress(null);
    setCompleted(null);
    setError(null);
  };

  const handleIndexingProgress = (data: IndexingProgress) => {
    setProgress(data);
  };

  const handleIndexingCompleted = (data: IndexingCompleted) => {
    setIsIndexing(false);
    setCompleted(data);
    setShowSuccess(true);
  };
  
  const handleIndexingError = (data: any) => {
    console.error('Indexing error:', data);
    setIsIndexing(false);
    setError(data.error || 'An error occurred during indexing');
  };
  
  const handleIndexingStatus = (data: any) => {
    console.log('Indexing status:', data);
    // You can update UI based on different status messages if needed
    if (data.status === 'initializing' || data.status === 'starting' || data.status === 'checking') {
      setIsIndexing(true);
    }
  };

  const startIndexing = () => {
    if (!directory) {
      setError('Please enter a directory path');
      return;
    }

    socketService.startIndexing({
      directory,
      recursive
    });
  };

  const handleCloseSnackbar = () => {
    setShowSuccess(false);
  };

  return (
    <Box sx={{ maxWidth: 800, mx: 'auto', p: 3 }}>
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          Document Indexer
        </Typography>
        
        <Stack spacing={2} sx={{ mb: 3 }}>
          <TextField
            fullWidth
            label="Directory Path"
            value={directory}
            onChange={(e) => setDirectory(e.target.value)}
            disabled={isIndexing}
            helperText="Enter the path to the directory containing documents to index"
          />
          
          <FormControlLabel
            control={
              <Checkbox
                checked={recursive}
                onChange={(e) => setRecursive(e.target.checked)}
                disabled={isIndexing}
              />
            }
            label="Recursively search subdirectories"
          />
        </Stack>
        
        <Button
          variant="contained"
          color="primary"
          onClick={startIndexing}
          disabled={isIndexing}
          sx={{ mb: 2 }}
        >
          {isIndexing ? 'Indexing...' : 'Start Indexing'}
        </Button>
        
        {error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
        )}
      </Paper>

      {isIndexing && progress && (
        <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Indexing Progress
          </Typography>
          
          <Box sx={{ mb: 2 }}>
            <LinearProgress 
              variant="determinate" 
              value={progress.percentage} 
              sx={{ height: 10, borderRadius: 5 }}
            />
            <Typography variant="body2" sx={{ mt: 1 }}>
              {progress.percentage.toFixed(1)}% Complete
            </Typography>
          </Box>
          
          <Typography variant="body2">
            Processing file {progress.current} of {progress.total}
          </Typography>
          
          <Typography variant="body2" sx={{ wordBreak: 'break-all' }}>
            Current file: {progress.file_path}
          </Typography>
          
          <Typography variant="body2">
            Chunks indexed from current file: {progress.chunks_indexed}
          </Typography>
        </Paper>
      )}

      {completed && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" color="primary" gutterBottom>
              Indexing Completed
            </Typography>
            <Typography variant="body1">
              Total files processed: {completed.total_files}
            </Typography>
            <Typography variant="body1">
              Total chunks indexed: {completed.total_chunks}
            </Typography>
          </CardContent>
        </Card>
      )}

      <Snackbar
        open={showSuccess}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
      >
        <Alert onClose={handleCloseSnackbar} severity="success">
          Indexing completed successfully!
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default Indexer;

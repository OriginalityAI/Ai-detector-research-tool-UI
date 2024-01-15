export const RATE_LABELS = [
  'F1 score',
  'Precision',
  'Recall (True Positive Rate)',
  'Specificity (True Negative Rate)',
  'False Positive Rate',
  'Accuracy'
] as const;

export const PENDING_MSG = {
  running: 'Task is running, polling again in 30 seconds...',
  completed: 'Task completed, handling file download...',
  oddResponse: 'Unrecognized response status, stopped polling'
}
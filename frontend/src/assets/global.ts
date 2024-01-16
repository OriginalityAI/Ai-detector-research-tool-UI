export const RATE_LABELS = [
  'F1 score',
  'Precision',
  'Recall (True Positive Rate)',
  'Specificity (True Negative Rate)',
  'False Positive Rate',
  'Accuracy'
] as const;

export const PENDING_MSG = {
  running: 'Your detectors are being evaluated, this may take a few minutes',
  completed: 'Task completed, handling file...',
  failed: 'Your analysis has failed due to an error, check logs',
  oddResponse: 'Unrecognized response status, stopped polling'
}
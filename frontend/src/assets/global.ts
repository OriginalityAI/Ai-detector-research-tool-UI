export const RATE_LABELS = [
  'F1 score',
  'Precision',
  'Recall',
  'Specificity',
  'False Positive Rate',
  'Accuracy'
] as const;

export const PENDING_MSG = {
  running: 'Your detectors are being evaluated, this may take a few minutes',
  completed: 'Task completed, handling file...',
  testing: 'Performing a quick test before initiating full analysis',
  oddResponse: 'Unrecognized response status, stopped polling'
}

export const BAD_RESULT_MSG = {
  analysisFailed: 'Analysis of your csv has failed, download the error log for more details',
  testFailed: 'Our test of your csv has failed, download the error log for more details',
  pollFailed: 'Your analysis has failed due to an error, download the error logs for more details',
  loglessError: 'Your analysis has failed due to an error, though no error log was found',
  noResults: 'No results found',
  unknown: 'An unknown error occured',
  zipFailure: 'There was a problem unzipping your file.'
}

export const TEST_RESULT_MSG = {
  pass: 'Check your output zip to verify that each detector is responding correctly.'
}
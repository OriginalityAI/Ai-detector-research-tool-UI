export const poll = async (taskId: string) => {
  try {
    // Make a GET request to the server
    const response = await fetch(`/results/${taskId}`);
    const data = await response.json();

    // Check the status of the response
    if (data.status === 'running') {
      // If the task is still running, poll again after 30 seconds
      console.log('Task is running, polling again in 30 seconds...');
      setTimeout(() => poll(taskId), 30000);
    } else if (response.ok && response.status === 200 && data.status !== 'running') {
      // If the server returned a file response, handle the file download
      console.log('Task completed, handling file download...');
      // Assuming the server sets the 'Content-Disposition' header,
      // the browser will handle the file download automatically.
    } else if (data.error) {
      // If there was an error, log it and stop polling
      console.error(`Error from server: ${data.error}`);
    } else {
      // If no recognized response status is received, stop polling
      console.error('Unrecognized response status, stopping polling.');
    }
  } catch (error) {
    // If there's a network or server error, log the error and retry after 30 seconds
    console.error('Network/Server Error: An error occurred while polling:', error);
    console.log('Retrying in 30 seconds...');
    setTimeout(() => poll(taskId), 30000);
  }
}
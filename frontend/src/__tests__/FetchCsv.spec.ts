// import {describe, expect, it} from 'vitest';

// const successfulCsv = `text,dataset,label
// "Greetings, World! This is a sample text designed to demonstrate the capabilities of artificial intelligence.",gpt-4,ai-generated
// "Hello World, this is some example human generated text",human,human-generated`

// const failCsv = `text,datase,labe
// "Greetings, World! This is a sample text designed to demonstrate the capabilities of artificial intelligence.",gpt-4,ai-generated
// "Hello World, this is some example human generated text",human,human-generated`


// const formdata = new FormData();
// formdata.append("csvFile", new Blob([successfulCsv]), "Mixtral 8X7B Dataset.csv");
// formdata.append("api_keys", "{\n  \"ORIGINALITY_API_KEY\": [false, \"qg8lypxa5340cbj76k91f2srhdwotnze\"]}");

// const requestOptions = {
//   method: 'POST',
//   body: formdata,
//   redirect: 'follow'
// };

// describe('FetchCsv', () => {
//   it('should fetch a CSV file', async () => {
//     const res = await fetch("http://127.0.0.1:8000/analyze/", requestOptions)
//     console.log(res.blob())
//   });
// });

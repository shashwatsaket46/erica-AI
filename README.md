Hello, this is Erica

<img width="1629" height="867" alt="image" src="https://github.com/user-attachments/assets/0934bccf-ae2a-4677-8ba6-1f192020b88e" />


How to RUN:

This project is a full stack project, so we have a backend and ui component.
Once downloaded, in the root folder, open bash for unix / cmd, powershell for windows.
After that paste this command -> docker compose up --build -d
Once it has been build, <img width="1844" height="207" alt="image" src="https://github.com/user-attachments/assets/aea5b6ae-fbb5-42d5-95b1-ea7336163cbb" />

the above screen will show.
Then go to http://localhost:5173/ 
This will open a UI where you can chat and ask questions, and in accordance with the text, it will send the request to /ask api in the backend which will fetch the data.

The database that I am using for knowledge graph is neo4j which can be accessed using the link: http://localhost:7474/browser/ username - neo4j, password =password

The results and answers required as per part of this project is in the folder resultAndAnswers.

Now, coming to the folder structure. The UI part and code is ther in erica-ui, the backend code is there in ericaApi which have the main.py which hosts several API that I have discussed below. The folder cortex have all the required backend codes that is being redirected from ericaAPI main.py file.


<img width="677" height="627" alt="image" src="https://github.com/user-attachments/assets/2f2152fe-5357-47bc-ae04-1a48beefa507" />




I am using Ollama Qwen 2.5:3B model running on my localhost, so this is also required to run the project.

The graph build in neo4j looks as follows: 

<img width="1854" height="869" alt="image" src="https://github.com/user-attachments/assets/bfb8523d-f867-4b48-8514-481efd0318fa" />




  Now I will explain each API that I am hosting, just go to this api link: http://localhost:8000/docs#

  This will open swagger-ui page like this:
  <img width="1653" height="864" alt="image" src="https://github.com/user-attachments/assets/06ad9ff9-08a7-441e-80af-aba6290789ea" />


  APIs:

  1.  /
      Method Get
      Description: This checks if the Erica is running propely.
      <img width="1791" height="867" alt="image" src="https://github.com/user-attachments/assets/0f1bd5cd-7f3e-4a9f-9355-478e7ccb3859" />

  2.  /check-llm
      Method Get
      Description: This is a get API which will hit the Ollama and checks if the LLM model is running. Here successful response will show the models and its description.
      <img width="1541" height="859" alt="image" src="https://github.com/user-attachments/assets/66e9c5f8-4221-45f4-8036-1fb68628f4f0" />

  3.  /ingest
      Method Post
      Description: This is an API to accept any website, link, youtube videos, crawling website link and load in our local data/raw folder.
      <img width="1784" height="864" alt="image" src="https://github.com/user-attachments/assets/9f26d187-de9d-470a-a048-4b3c22c9ff6f" />

      <img width="897" height="538" alt="image" src="https://github.com/user-attachments/assets/4fb5e452-5e28-41d0-a6fc-e648aea12947" />


  4.  /ingest/chunk
      Method Post
      Description: This will create chunks of the raw text generated.
      <img width="1685" height="981" alt="image" src="https://github.com/user-attachments/assets/9eb50938-aa31-4c04-8092-f21265a9f1ea" />

  5.  /embed
      Method Post
      Description: This will create the embeddings for each chunks properly and store in our data folder.
      <img width="1570" height="956" alt="image" src="https://github.com/user-attachments/assets/dcc0a16f-7b14-4ea3-88b3-2b945e159268" />

  6.  /graph/build
      Method Post
      Description: This build build graph nodes for the embedded chunks.
      <img width="1856" height="970" alt="image" src="https://github.com/user-attachments/assets/e4e7357e-0d90-4dd9-93fe-6c6e14b8ba7d" />

  7.  /semantic/extract
      Method Post
      Description: This will extract semantic values for the graphs and divide into concepts, pre=reqs, definitions, examples for each graph nodes.
      <img width="1691" height="974" alt="image" src="https://github.com/user-attachments/assets/6e169dbd-a97a-4149-9088-a0d3f37c998a" />

  8.  /kg/build
      Method Post
      Description: This will create the knowledge graph and store it in the neo4j database.
      <img width="1646" height="974" alt="image" src="https://github.com/user-attachments/assets/9026a73d-9b76-45e6-99cf-f648435b8d42" />

  9.  /kg/cluster
      Method Post
      Description: This will create knowledge graph cluster and display the results for this.
      <img width="1668" height="506" alt="image" src="https://github.com/user-attachments/assets/b6412d46-a563-46b2-8ae8-b75cc11130a0" />

  10. /ask
      Method Post
      Description: This is the ask API where we can ask questions and our Erica would reply.
      <img width="1763" height="982" alt="image" src="https://github.com/user-attachments/assets/64965336-9a3e-4cd8-83d3-ee559092f6af" />

  11. /kg/subgraph
      Method Post
      Description: This will create a subgraph for any concepts.
      <img width="1439" height="857" alt="image" src="https://github.com/user-attachments/assets/a96c4884-91fc-4a03-b01c-8ff09ad46df8" />

  12. /pipeline/run
      Method Post
      Description: This is a pipeline which runs properly for single file or website, and will run for every API given above.
      <img width="1551" height="677" alt="image" src="https://github.com/user-attachments/assets/1e70a216-ae44-4e25-82ad-ab0f4a7ba9b4" />

  13. /bulk/run
      Method Post
      Description: This can be used for small amount of multimodal files, although for bigger files, the pipeline required high computation resources.
      <img width="1607" height="972" alt="image" src="https://github.com/user-attachments/assets/c321a7c3-07f1-423c-9888-f6ad6d28f53a" />

  14. /job/submit
      Method Post
      Description: This can used to run multimodal multiple files and will schedule a job for each method and for each API. This will provide a job_id which can be checked in next API.
      <img width="1588" height="971" alt="image" src="https://github.com/user-attachments/assets/731bba3d-72f2-4b35-b80d-3650d8b3ce7a" />

      <img width="1646" height="963" alt="image" src="https://github.com/user-attachments/assets/440c2313-9f18-4d55-b151-a290187bcfe7" />

  15. /job/status
      Method Get
      Description: This can check the status of the job created in the API 14.
      <img width="1674" height="980" alt="image" src="https://github.com/user-attachments/assets/232b7f9c-09e6-45d5-8e44-1b81b580ee12" />

  16. /job/result
      Description: This will show the result obtained after the job completion
      <img width="983" height="827" alt="image" src="https://github.com/user-attachments/assets/fc7d3f50-39be-4577-aaab-fda99d2faffd" />



| #  | Endpoint        | Method | Description |
|----|-----------------|--------|-------------|
| 1  | `/` | GET | Checks if Erica is running properly. |
| 2  | `/check-llm` | GET | Hits Ollama and checks if the LLM model is running; returns list of models and descriptions. |
| 3  | `/ingest` | POST | Accepts any website, link, YouTube video, or crawled URL and stores raw text in `data/raw`. |
| 4  | `/ingest/chunk` | POST | Creates text chunks from the raw ingested data. |
| 5  | `/embed` | POST | Generates embeddings for each chunk and stores them. |
| 6  | `/graph/build` | POST | Builds graph nodes for the embedded chunks. |
| 7  | `/semantic/extract` | POST | Extracts semantic info (concepts, prerequisites, definitions, examples) for each graph node. |
| 8  | `/kg/build` | POST | Creates the Knowledge Graph and stores it in Neo4j. |
| 9  | `/kg/cluster` | POST | Clusters the Knowledge Graph and shows the results. |
| 10 | `/ask` | POST | Main API to ask questions; Erica responds using LLM + KG. |
| 11 | `/kg/subgraph` | POST | Creates a subgraph for any concept. |
| 12 | `/pipeline/run` | POST | Runs the complete pipeline for a single file or website. |
| 13 | `/bulk/run` | POST | Runs pipeline for smaller multimodal file batches. |
| 14 | `/job/submit` | POST | Submits async multimodal jobs; returns job_id for tracking. |
| 15 | `/job/status` | GET | Checks the status of a job created by `/job/submit`. |
| 16 | `/job/result` | GET | Shows the final result after job completion. |
| 17 | `/kg/summary` | POST | Creates summaries using the knowledge graph. |





 






     






  







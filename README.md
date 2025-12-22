Hello, this is Erica

<img width="1915" height="1027" alt="image" src="https://github.com/user-attachments/assets/40462e14-9730-4781-845e-3266ce8e0af7" />

How to RUN:

This project is a full stack project, so we have a backend and ui component.
Once downloaded, in the root folder, open bash for unix / cmd, powershell for windows.
After that paste this command -> docker compose up --build -d
Once it has been build, <img width="1444" height="164" alt="image" src="https://github.com/user-attachments/assets/6cd5cf3f-e1d1-420f-86af-edf576eb2ac7" />
the above screen will show.
Then go to http://localhost:5173/ 
This will open a UI where you can chat and ask questions, and in accordance with the text, it will send the request to /ask api in the backend which will fetch the data.

The database that I am using for knowledge graph is neo4j which can be accessed using the link: http://localhost:7474/browser/ username - neo4j, password =password

The results and answers required as per part of this project is in the folder resultAndAnswers.

Now, coming to the folder structure. The UI part and code is ther in erica-ui, the backend code is there in ericaApi which have the main.py which hosts several API that I have discussed below. The folder cortex have all the required backend codes that is being redirected from ericaAPI main.py file.


<img width="544" height="505" alt="image" src="https://github.com/user-attachments/assets/7d7df8b7-1ecf-4dd6-8e72-7b8d5b7e051b" />



I am using Ollama Qwen 2.5:3B model running on my localhost, so this is also required to run the project.

The graph build in neo4j looks as follows: 

<img width="1919" height="901" alt="image" src="https://github.com/user-attachments/assets/c3902a8c-6075-41e5-9255-d5fbf7c30825" />



  Now I will explain each API that I am hosting, just go to this api link: http://localhost:8000/docs#

  This will open swagger-ui page like this:
  <img width="1850" height="973" alt="image" src="https://github.com/user-attachments/assets/841a2d66-9adb-4047-9fc6-044cb969259c" />

  APIs:

  1.  /
      Method Get
      Description: This checks if the Erica is running propely.
      <img width="1471" height="712" alt="image" src="https://github.com/user-attachments/assets/7780333e-f0be-440c-8fb3-651a5ffb5ce0" />
  2.  /check-llm
      Method Get
      Description: This is a get API which will hit the Ollama and checks if the LLM model is running. Here successful response will show the models and its description.
      <img width="1731" height="973" alt="image" src="https://github.com/user-attachments/assets/1b71f0d7-91d9-4459-b2f4-f14b84d882a2" />
  3.  /ingest
      Method Post
      Description: This is an API to accept any website, link, youtube videos, crawling website link and load in our local data/raw folder.
      <img width="1615" height="787" alt="image" src="https://github.com/user-attachments/assets/7392efbe-657e-457a-ab25-5793736399d3" />
      <img width="1615" height="968" alt="image" src="https://github.com/user-attachments/assets/f81c0751-0918-4df2-8c75-aa41be5e605e" />

  4.  /ingest/chunk
      Method Post
      Description: This will create chunks of the raw text generated.
      <img width="1685" height="981" alt="image" src="https://github.com/user-attachments/assets/7d0500fe-6e77-453f-995f-56ea1a67a6ac" />
  5.  /embed
      Method Post
      Description: This will create the embeddings for each chunks properly and store in our data folder.
      <img width="1570" height="956" alt="image" src="https://github.com/user-attachments/assets/531e870e-802b-4fd0-886e-730ede768a18" />
  6.  /graph/build
      Method Post
      Description: This build build graph nodes for the embedded chunks.
      <img width="1856" height="970" alt="image" src="https://github.com/user-attachments/assets/45362da4-2891-418e-9742-bd1b059a9744" />
  7.  /semantic/extract
      Method Post
      Description: This will extract semantic values for the graphs and divide into concepts, pre=reqs, definitions, examples for each graph nodes.
      <img width="1691" height="974" alt="image" src="https://github.com/user-attachments/assets/3587f6e0-7739-4f0c-8501-c58816236218" />
  8.  /kg/build
      Method Post
      Description: This will create the knowledge graph and store it in the neo4j database.
      <img width="1646" height="974" alt="image" src="https://github.com/user-attachments/assets/9663a7d3-a499-4bd1-9d62-fe4ee087439d" />
  9.  /kg/cluster
      Method Post
      Description: This will create knowledge graph cluster and display the results for this.
      <img width="1668" height="506" alt="image" src="https://github.com/user-attachments/assets/870d7cfe-c0ea-4407-b204-6eb5438a2974" />
  10. /ask
      Method Post
      Description: This is the ask API where we can ask questions and our Erica would reply.
      <img width="1763" height="982" alt="image" src="https://github.com/user-attachments/assets/1fbe2e21-1af2-431f-9182-a724a3d771fc" />
  11. /kg/subgraph
      Method Post
      Description: This will create a subgraph for any concepts.
      <img width="1439" height="857" alt="image" src="https://github.com/user-attachments/assets/4e0e6fb3-03df-4307-b848-886cb02ffdd6" />
  12. /pipeline/run
      Method Post
      Description: This is a pipeline which runs properly for single file or website, and will run for every API given above.
      <img width="1551" height="677" alt="image" src="https://github.com/user-attachments/assets/e811fe0e-cadd-47c5-8f2c-7e9ea2fdf99d" />
  13. /bulk/run
      Method Post
      Description: This can be used for small amount of multimodal files, although for bigger files, the pipeline required high computation resources.
      <img width="1607" height="972" alt="image" src="https://github.com/user-attachments/assets/6db476b0-f696-4e15-a85f-a4a4f059a5a2" />
  14. /job/submit
      Method Post
      Description: This can used to run multimodal multiple files and will schedule a job for each method and for each API. This will provide a job_id which can be checked in next API.
      <img width="1588" height="971" alt="image" src="https://github.com/user-attachments/assets/e29c1b1e-f3fd-4ee0-9f44-3912f7de8b4e" />
      <img width="1646" height="963" alt="image" src="https://github.com/user-attachments/assets/90edb6c8-a2bf-4e16-8a95-690fda616515" />
  15. /job/status
      Method Get
      Description: This can check the status of the job created in the API 14.
      <img width="1674" height="980" alt="image" src="https://github.com/user-attachments/assets/2a70be42-9d55-439b-aa7c-bb906eaa83b7" />
  16. /job/result
      Description: This will show the result obtained after the job completion
      <img width="983" height="827" alt="image" src="https://github.com/user-attachments/assets/af514d6a-13af-4e67-8a8a-07d575cd3077" />


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





 






     






  







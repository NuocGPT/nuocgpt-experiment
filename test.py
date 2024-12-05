from llama_index.core.llms import ChatMessage
from llama_index.llms.gemini import Gemini
from llama_index.embeddings.gemini import GeminiEmbedding
from llama_index.core import SimpleDirectoryReader
from llama_index.core import VectorStoreIndex
from llama_index.core import ServiceContext

documents=SimpleDirectoryReader("./data/Set_1")
doc=documents.load_data()

model=Gemini(models='gemini-pro')
gemini_embed_model=GeminiEmbedding(model_name="models/embedding-001")

service_context = ServiceContext.from_defaults(llm=model,embed_model=gemini_embed_model, chunk_size=800, chunk_overlap=20)

index = VectorStoreIndex.from_documents(doc,service_context=service_context)

index.storage_context.persist()

query_engine=index.as_query_engine()

response=query_engine.query("Theo nghiên cứu, cá tra có khả năng thích ứng như thế nào khi gặp phải tình trạng xâm nhập mặn?")

print(doc)

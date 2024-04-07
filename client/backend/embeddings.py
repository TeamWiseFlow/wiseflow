from BCEmbedding.tools.langchain import BCERerank
from langchain_community.embeddings import HuggingFaceEmbeddings
import os


embedding_model_name = os.environ.get('EMBEDDING_MODEL_PATH', "")
rerank_model_name = os.environ.get('RERANKER_MODEL_PATH', "")

if not embedding_model_name or not rerank_model_name:
    raise Exception("请设置 EMBEDDING_MODEL_PATH 和 RERANKER_MODEL_PATH")

device = os.environ.get('DEVICE', 'cpu')
embedding_model_kwargs = {'device': device}
embedding_encode_kwargs = {'batch_size': 32, 'normalize_embeddings': True, 'show_progress_bar': False}
reranker_args = {'model': rerank_model_name, 'top_n': 5, 'device': device}
embed_model = HuggingFaceEmbeddings(model_name=embedding_model_name, model_kwargs=embedding_model_kwargs, encode_kwargs=embedding_encode_kwargs)
reranker = BCERerank(**reranker_args)

import os
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

app = FastAPI(title="Writer Agent")

# Configura o LLM (Certifique-se que OPENAI_API_KEY está no .env)
# Se não tiver chave, usamos um mock simples para o lab não quebrar
api_key = os.getenv("OPENAI_API_KEY")

if api_key:
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
else:
    print("Warning: OPENAI_API_KEY not found. Using Mock LLM.")
    llm = None

class WriteRequest(BaseModel):
    topic: str
    context: str

@app.post("/write")
async def write_content(request: WriteRequest):
    print(f"[Writer] Escrevendo sobre: {request.topic}")
    
    if not llm:
        # Mock Response se não houver API Key
        return {
            "content": f"[MOCK GENERATION] Here is a report about {request.topic}. "
                       f"Context used: {request.context[:50]}..."
        }

    # Prompt Template
    prompt = ChatPromptTemplate.from_template(
        """You are a professional technical writer.
        Write a concise summary paragraph about the following topic: {topic}.
        
        Use the following context gathered by the researcher:
        {context}
        
        If the context is not relevant, mention that you are writing based on general knowledge.
        """
    )

    chain = prompt | llm | StrOutputParser()
    
    try:
        result = await chain.ainvoke({"topic": request.topic, "context": request.context})
        
        print(f"\n[Writer] --- Generated Content for '{request.topic}' ---\n{result}\n------------------------------------------")
        
        return {"content": result}
    except Exception as e:
        return {"content": f"Error generating text: {str(e)}"}

@app.get("/health")
def health():
    return {"status": "ok"}

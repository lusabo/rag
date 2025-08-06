# app_streamlit.py
# Streamlit UI para RAG com backend FastAPI
# Lê configurações da OpenAI a partir do .env automaticamente

import os
import json
from datetime import datetime

import pandas as pd
import requests
import streamlit as st

try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass

st.set_page_config(page_title="RAG • Documentos", page_icon="📄", layout="wide")

BACKEND_DEFAULT = os.getenv("BACKEND_URL", "http://localhost:8000")
OPENAI_API_KEY_ENV = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL_ENV = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

if "backend_url" not in st.session_state:
    st.session_state.backend_url = BACKEND_DEFAULT
if "chat" not in st.session_state:
    st.session_state.chat = []
if "offset" not in st.session_state:
    st.session_state.offset = 0

def api_url(path: str) -> str:
    return st.session_state.backend_url.rstrip("/") + path

def upload_pdf(file) -> dict:
    files = {"upload": (file.name, file.getvalue(), "application/pdf")}
    r = requests.post(api_url("/files/upload"), files=files, timeout=120)
    r.raise_for_status()
    return r.json()

def list_files(limit=20, offset=0) -> dict:
    r = requests.get(api_url("/files"), params={"limit": limit, "offset": offset}, timeout=30)
    r.raise_for_status()
    return r.json()

def search(q: str, k: int = 5) -> dict:
    r = requests.get(api_url("/search"), params={"q": q, "k": k}, timeout=60)
    r.raise_for_status()
    return r.json()

def get_openai_client():
    api_key = OPENAI_API_KEY_ENV
    if not api_key:
        return None

    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError("A biblioteca 'openai' não está instalada. Instale com: pip install openai>=1.0.0")

    return OpenAI(api_key=api_key)

st.sidebar.header("Configuração")
st.sidebar.text_input("Backend URL", key="backend_url", help="Ex.: http://localhost:8000")

st.sidebar.divider()
key_detected = bool(OPENAI_API_KEY_ENV)
st.sidebar.write(
    f"**OpenAI (.env):** {'✅ detectado' if key_detected else '❌ não encontrado'}"
)
use_openai = st.sidebar.toggle(
    "Gerar resposta com OpenAI (cliente)", value=key_detected,
    help="Se ativado, o resumo em linguagem natural será gerado no cliente usando as variáveis OPENAI_* do .env."
)
openai_model = st.sidebar.text_input(
    "Modelo (OPENAI_MODEL)", value=OPENAI_MODEL_ENV,
    help="Padrão vindo do .env. Ex.: gpt-4o-mini"
)

tab_up, tab_list, tab_chat = st.tabs([
    "📌 Anexar Documento", "📂 Listar Documentos", "💬 Consultar Documentos"
])

with tab_up:
    st.subheader("Anexar Documento (PDF)")
    st.caption("Envie PDFs; o backend armazena o arquivo bruto e gera chunks + embeddings.")

    files_upl = st.file_uploader(
        "Selecione PDFs",
        type=["pdf"],
        accept_multiple_files=True,
        help="Envia para /files/upload (campo 'upload').",
    )

    if st.button("Enviar", type="primary", disabled=not files_upl):
        results = []
        for f in files_upl or []:
            try:
                with st.spinner(f"Enviando {f.name}…"):
                    res = upload_pdf(f)
                st.success(f"{f.name}: OK ({res.get('id')})")
                results.append({"arquivo": f.name, **res})
            except requests.HTTPError as e:
                try:
                    detail = e.response.json().get("detail")
                except Exception:
                    detail = str(e)
                st.error(f"{f.name}: {detail}")
            except Exception as e:
                st.error(f"{f.name}: {e}")
        if results:
            st.dataframe(pd.DataFrame(results), use_container_width=True)

with tab_list:
    st.subheader("Arquivos cadastrados")

    col_a, col_b = st.columns([1, 6])
    with col_a:
        page_size = st.selectbox("Por página", [10, 20, 50], index=1)
    with col_b:
        if st.button("🔄 Atualizar"):
            st.session_state.offset = 0

    try:
        data = list_files(limit=page_size, offset=st.session_state.offset)
        items = data.get("items", [])
        total = int(data.get("total", 0))

        for it in items:
            try:
                it["created_at"] = (
                    datetime.fromisoformat(str(it["created_at"]).replace("Z", "+00:00"))
                    .astimezone()
                    .strftime("%Y-%m-%d %H:%M:%S")
                )
            except Exception:
                pass

        df = pd.DataFrame(items)
        if not df.empty:
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum arquivo encontrado.")

        col_p1, col_p2, col_p3 = st.columns([1, 1, 5])
        with col_p1:
            prev_disabled = st.session_state.offset <= 0
            if st.button("⬅️ Anterior", disabled=prev_disabled):
                st.session_state.offset = max(0, st.session_state.offset - page_size)
                st.experimental_rerun()
        with col_p2:
            next_disabled = st.session_state.offset + page_size >= total
            if st.button("Próxima ➡️", disabled=next_disabled):
                st.session_state.offset = st.session_state.offset + page_size
                st.experimental_rerun()
        with col_p3:
            st.caption(f"Total: {total} • Exibindo {len(items)} (offset {st.session_state.offset})")

    except Exception as e:
        st.error(f"Falha ao listar: {e}")

with tab_chat:
    st.subheader("Consultar Documentos")
    st.caption("Consulta semântica via /search. Se ativado na barra lateral, gera um resumo com OpenAI usando OPENAI_* do .env.")

    top_k = st.slider("Resultados (top-k)", 1, 20, 5)

    for msg in st.session_state.chat:
        with st.chat_message("user" if msg["role"] == "user" else "assistant"):
            st.markdown(msg["content"])
            if msg["role"] == "assistant" and msg.get("hits"):
                with st.expander("Trechos recuperados"):
                    for h in msg["hits"]:
                        st.code(json.dumps(h, ensure_ascii=False, indent=2), language="json")

    question = st.chat_input("Digite sua pergunta…")
    if question:
        st.session_state.chat.append({"role": "user", "content": question})

        try:
            with st.spinner("Buscando…"):
                res = search(question, k=top_k)
                hits = res.get("hits", [])
        except Exception as e:
            hits = []
            answer = f"Erro na busca: {e}"
            st.session_state.chat.append({"role": "assistant", "content": answer, "hits": []})
            st.rerun()

        def to_line(h: dict) -> str:
            content = h.get("content") or h.get("text") or h.get("chunk") or ""
            file_id = h.get("file_id") or h.get("fileId") or ""
            page = h.get("page") or h.get("page_number") or ""
            score = h.get("score") or h.get("dist") or h.get("distance") or ""
            return f"[file:{file_id} pág:{page} score:{score}] {content}"

        context_lines = [to_line(h) for h in hits[:top_k]]
        answer = (
            "Encontrei os trechos abaixo relacionados à sua pergunta. "
            "Ative a opção de OpenAI para gerar um resumo em linguagem natural."
        )

        if use_openai and OPENAI_API_KEY_ENV:
            try:
                client = get_openai_client()
                if client is None:
                    raise RuntimeError("OPENAI_API_KEY não encontrado no .env")
                context = "\n\n".join(context_lines)
                prompt = (
                    "Você é um assistente que responde apenas com base no CONTEXTO fornecido.\n"
                    "Responda em português, de forma direta e cite os tópicos-chave.\n"
                    "Se a resposta não estiver no contexto, diga que não sabe.\n\n"
                    f"PERGUNTA:\n{question}\n\nCONTEXTO:\n{context}\n\nRESPOSTA:"
                )
                print(f"Prompt enviado para OpenAI:\n{prompt}\n")
                with st.spinner("Gerando resposta…"):
                    resp = client.responses.create(model=openai_model, input=prompt)
                    answer = (resp.output_text or "").strip() or answer
                    print(f"Resposta recebida:\n{answer}\n")
            except Exception as e:
                print(f"Erro ao chamar OpenAI: {e}")
                answer = f"Falha ao gerar resposta com OpenAI: {e}"

        with st.chat_message("assistant"):
            st.markdown(answer)
            if context_lines:
                with st.expander("Trechos recuperados"):
                    for h in hits:
                        st.code(json.dumps(h, ensure_ascii=False, indent=2), language="json")

        st.session_state.chat.append({"role": "assistant", "content": answer, "hits": hits})
        st.rerun()

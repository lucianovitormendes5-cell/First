import streamlit as st
from openai import OpenAI
import base64

# Configuração visual da página (Você pode alterar título, ícone e cores depois)
st.set_page_config(page_title="Estúdio Raízes e Sonhos", page_icon="🎬", layout="centered")

st.title("🎬 Diretor de Arte — Raízes e Sonhos")
st.caption("Agente Oficial conectado à API da OpenAI (Geração 9:16)")

# Barra lateral para colocar suas chaves (ou carregar automático dos Secrets)
with st.sidebar:
    st.header("⚙️ Configurações da API")
    api_key = st.text_input("OpenAI API Key (sk-...)", value=st.secrets.get("OPENAI_API_KEY", ""), type="password")
    assistant_id = st.text_input("ID do Agente (asst_...)", value=st.secrets.get("ASSISTANT_ID", ""))
    
    st.divider()
    st.subheader("📸 Referências da Cena")
    uploaded_files = st.file_uploader(
        "Anexe as fotos de referência (Milena, Lúcia, Rosângela):", 
        type=["png", "jpg", "jpeg"], 
        accept_multiple_files=True
    )
    
    gerar_imagem = st.checkbox("Gerar Imagem Automaticamente (Vertical 9:16)", value=True)
    modelo_img = st.selectbox("Modelo de Imagem:", ["dall-e-3", "gpt-image-1"])
    qualidade_img = st.selectbox("Qualidade:", ["standard", "hd"])

# Inicializa histórico do Chat na tela
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostra mensagens antigas na tela (estilo ChatGPT)
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "image_url" in msg:
            st.image(msg["image_url"], use_container_width=True)

# Campo de digitação do Chat
if prompt := st.chat_input("Descreva a cena do episódio aqui..."):
    if not api_key or not assistant_id:
        st.error("Por favor, preencha sua API Key e o ID do Agente na barra lateral esquerda!")
        st.stop()

    client = OpenAI(api_key=api_key)

    # Mostra a sua mensagem na tela
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("O Agente está dirigindo a cena..."):
            try:
                # 1. Cria ou recupera a Thread do seu Agente na OpenAI
                if "thread_id" not in st.session_state:
                    thread = client.beta.threads.create()
                    st.session_state.thread_id = thread.id

                # Prepara o conteúdo (Texto + Fotos de referência se anexadas)
                content_payload = [{"type": "text", "text": prompt + "\n\nIMPORTANTE: Retorne APENAS o prompt visual final detalhado otimizado para geração da imagem em 9:16."}]
                
                if uploaded_files:
                    for file in uploaded_files:
                        file_bytes = file.getvalue()
                        uploaded_oai = client.files.create(file=(file.name, file_bytes), purpose="vision")
                        content_payload.append({
                            "type": "image_file",
                            "image_file": {"file_id": uploaded_oai.id}
                        })

                # 2. Envia para o seu Agente (Assistant)
                client.beta.threads.messages.create(
                    thread_id=st.session_state.thread_id,
                    role="user",
                    content=content_payload
                )

                # 3. Roda o Agente com as regras que você já salvou nele
                run = client.beta.threads.runs.create_and_poll(
                    thread_id=st.session_state.thread_id,
                    assistant_id=assistant_id
                )

                if run.status == 'completed':
                    messages = client.beta.threads.messages.list(thread_id=st.session_state.thread_id)
                    resposta_agente = messages.data[0].content[0].text.value
                    
                    with st.expander("Ver Prompt Técnico criado pelo Agente"):
                        st.write(resposta_agente)

                    # 4. Dispara a criação da imagem usando o prompt que o seu Agente montou
                    if gerar_imagem:
                        with st.spinner("Renderizando frame vertical 9:16..."):
                            img_response = client.images.generate(
                                model=modelo_img,
                                prompt=resposta_agente[:3900],
                                size="1024x1792",
                                quality=qualidade_img,
                                n=1,
                            )
                            image_url = img_response.data[0].url
                            st.image(image_url, caption="Frame Gerado (9:16)", use_container_width=True)
                            st.session_state.messages.append({
                                "role": "assistant", 
                                "content": "Frame gerado com sucesso!", 
                                "image_url": image_url
                            })
                    else:
                        st.markdown(resposta_agente)
                        st.session_state.messages.append({"role": "assistant", "content": resposta_agente})
                else:
                    st.error(f"Erro na execução do Agente: {run.status}")

            except Exception as e:
                st.error(f"Erro na API: {str(e)}")

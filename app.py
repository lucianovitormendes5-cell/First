import streamlit as st
from openai import OpenAI
import base64

st.set_page_config(page_title="ChatGPT - Raízes e Sonhos", page_icon="💬", layout="centered")

# Estilização visual para ficar idêntico ao ChatGPT
st.markdown("""
    <style>
    .stChatMessage { border-radius: 12px; padding: 10px; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

st.title("💬 ChatGPT • Diretor de Arte")
st.caption("Série: Raízes e Sonhos (Salvador, BA)")

DIRETRIZ_SERIE = """
Você é o Diretor de Arte Oficial da série dramática 'Raízes e Sonhos' (Salvador, Bahia).
Sua função é transformar o pedido do usuário num prompt visual cinematográfico vertical 9:16 (1024x1792) extremamente detalhado.
ESTILO OBRIGATÓRIO: Animação 3D semirrealista de altíssimo orçamento, texturas de pele humanas reais, iluminação dourada de Golden Hour de Salvador misturada com luz interna incandescente. PROIBIDO estilo cartoon infantil ou rostos plásticos.
PERSONAGENS PRINCIPAIS:
- Milena (17 anos): Jovem negra, pele morena quente, tranças box braids pretas longas com anéis prateados, regata amarela.
- Lúcia (14 anos): Irmã, pele morena quente, cabelo cacheado volumoso nos ombros, regata azul-marinho, colar de borboleta.
- Rosângela (40 anos): Mãe, mulher negra madura, expressão digna e cansada, cabelo cacheado preso em coque abacaxi, blusa floral, pano de prato.
Retorne APENAS o prompt visual final detalhado em inglês para o gerador de imagem, mantendo 100% de fidelidade às referências visuais enviadas.
"""

# Barra lateral limpa apenas para chave e configurações essenciais
with st.sidebar:
    st.header("⚙️ Configurações")
    api_key = st.text_input("OpenAI API Key (sk-...)", value=st.secrets.get("OPENAI_API_KEY", ""), type="password")
    
    st.divider()
    st.markdown("### 📎 Anexos e Referências")
    uploaded_files = st.file_uploader(
        "Envie fotos dos personagens ou referências de cena:", 
        type=["png", "jpg", "jpeg", "webp"], 
        accept_multiple_files=True
    )
    
    gerar_imagem = st.checkbox("Gerar Imagem Automaticamente (9:16)", value=True)
    qualidade_img = st.selectbox("Qualidade da Imagem:", ["standard", "hd"])

if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibe o histórico de conversas na tela estilo chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "image_url" in msg:
            st.image(msg["image_url"], use_container_width=True)

# Caixa de texto principal do chat (onde você digita como no ChatGPT)
if prompt := st.chat_input("Digite sua cena ou comando aqui..."):
    if not api_key:
        st.error("Por favor, insira sua chave da API OpenAI na barra lateral esquerda.")
        st.stop()

    client = OpenAI(api_key=api_key.strip())

    # Adiciona a mensagem do usuário no histórico
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Processando direção de arte..."):
            try:
                # Prepara o conteúdo multimodal (texto + imagens enviadas no uploader)
                user_content = [{"type": "text", "text": f"Pedido do usuário: {prompt}"}]
                
                if uploaded_files:
                    for file in uploaded_files:
                        b64_img = base64.b64encode(file.getvalue()).decode("utf-8")
                        user_content.append({
                            "type": "image_url",
                            "image_url": {"url": f"data:{file.type};base64,{b64_img}"}
                        })
                
                # Gera o prompt otimizado usando GPT-4o
                chat_resp = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": DIRETRIZ_SERIE},
                        {"role": "user", "content": user_content}
                    ]
                )
                resposta_agente = chat_resp.choices[0].message.content

                with st.expander("Ver Prompt Técnico Criado"):
                    st.write(resposta_agente)

                # Dispara a geração de imagem sem erros de incompatibilidade de modelo
                if gerar_imagem:
                    with st.spinner("Renderizando frame vertical 9:16..."):
                        img_response = client.images.generate(
                            model="dall-e-3",
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

            except Exception as e:
                st.error(f"Erro na API da OpenAI: {str(e)}")

import streamlit as st
from openai import OpenAI
import base64

st.set_page_config(page_title="Raízes e Sonhos - Estúdio", page_icon="🎬", layout="centered")

st.title("🎬 Raízes e Sonhos • Estúdio de Cenas")
st.caption("Ambiente Privado de Criação (9:16)")

with st.sidebar:
    st.header("⚙️ Painel de Controle")
    # Campo seguro para inserir a chave nova gerada no painel da OpenAI
    api_key_input = st.text_input("OpenAI API Key (sk-...):", type="password")
    
    st.divider()
    st.markdown("### 📎 Anexos e Referências")
    uploaded_files = st.file_uploader(
        "Envie fotos ou referências visuais:", 
        type=["png", "jpg", "jpeg", "webp"], 
        accept_multiple_files=True
    )
    
    gerar_imagem = st.checkbox("Gerar Imagem Automaticamente", value=True)
    qualidade_img = st.selectbox("Qualidade:", ["standard", "hd"])

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "image_url" in msg:
            st.image(msg["image_url"], use_container_width=True)

if prompt := st.chat_input("Digite o seu comando ou descrição da cena..."):
    if not api_key_input:
        st.error("Por favor, insira a sua nova chave de API da OpenAI na barra lateral esquerda.")
        st.stop()

    client = OpenAI(api_key=api_key_input.strip())

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Processando..."):
            try:
                user_content = [{"type": "text", "text": prompt}]
                
                if uploaded_files:
                    for file in uploaded_files:
                        b64_img = base64.b64encode(file.getvalue()).decode("utf-8")
                        user_content.append({
                            "type": "image_url",
                            "image_url": {"url": f"data:{file.type};base64,{b64_img}"}
                        })
                
                chat_resp = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "Você é um assistente de direção de arte criativo e flexível para webséries. Ajude o usuário a detalhar cenas visuais e gere comandos precisos para a criação de imagens verticais em 9:16 baseados estritamente no que o usuário solicitar."},
                        {"role": "user", "content": user_content}
                    ]
                )
                resposta_agente = chat_resp.choices[0].message.content

                with st.expander("Ver Descrição Técnica"):
                    st.write(resposta_agente)

                if gerar_imagem:
                    with st.spinner("Renderizando imagem vertical (9:16)..."):
                        img_response = client.images.generate(
                            model="dall-e-3",
                            prompt=resposta_agente[:3900],
                            size="1024x1792",
                            quality=qualidade_img,
                            n=1,
                        )
                        image_url = img_response.data[0].url
                        st.image(image_url, caption="Frame Gerado", use_container_width=True)
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": "Frame gerado com sucesso!", 
                            "image_url": image_url
                        })
                else:
                    st.markdown(resposta_agente)
                    st.session_state.messages.append({"role": "assistant", "content": resposta_agente})

            except Exception as e:
                st.error(f"Erro na API: {str(e)}")

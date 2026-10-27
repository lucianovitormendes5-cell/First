import streamlit as st
from openai import OpenAI
import base64

st.set_page_config(page_title="Estúdio Raízes e Sonhos", page_icon="🎬", layout="centered")

st.title("🎬 Diretor de Arte — Raízes e Sonhos")
st.caption("Agente Oficial conectado à API da OpenAI (Geração 9:16)")

DIRETRIZ_SERIE = """
Você é o Diretor de Arte Oficial da série 'Raízes e Sonhos' (Salvador, Bahia).
Sua função é transformar a descrição da cena em um prompt visual detalhado para gerar uma imagem vertical 9:16 (1024x1792).

ESTILO VISUAL OBRIGATÓRIO:
- Renderização 3D semirrealista cinematográfica de alto orçamento (texturas de pele reais, fios de cabelo detalhados).
- Iluminação dourada quente de fim de tarde em Salvador (Golden Hour) entrando pela janela + luz interna suave incandescente.
- PROIBIDO estilo cartoon infantil/Pixar, olhos esbugalhados ou rostos plásticos.

PERSONAGENS PRINCIPAIS (MANTENHA 100% DE FIDELIDADE ÀS FOTOS ANEXADAS):
- MILENA (17 anos): Jovem negra, pele morena quente, rosto delicado proporcional, longas tranças pretas (box braids) com pequenos anéis prateados, camiseta básica amarela.
- LÚCIA (14 anos): Irmã mais nova, pele morena quente, cabelo preto cacheado volumoso na altura dos ombros, regata azul-marinho e colar fino com pingente de borboleta.
- ROSÂNGELA (40 anos): Mãe, mulher negra madura com expressão digna e cansaço real do trabalho, cabelo cacheado volumoso preso no alto (coque abacaxi), blusa floral clara, calça jeans e pano de prato nas mãos.

Retorne APENAS o prompt final detalhado em inglês para o gerador de imagem, sem comentários extras.
"""

with st.sidebar:
    st.header("⚙️ Configurações da API")
    api_key = st.text_input("OpenAI API Key (sk-...)", value=st.secrets.get("OPENAI_API_KEY", ""), type="password")
    
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

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "image_url" in msg:
            st.image(msg["image_url"], use_container_width=True)

if prompt := st.chat_input("Descreva a cena do episódio aqui..."):
    if not api_key:
        st.error("Por favor, cole sua OpenAI API Key (sk-...) na barra lateral esquerda!")
        st.stop()

    client = OpenAI(api_key=api_key.strip())

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("O Diretor de Arte está montando a cena..."):
            try:
                user_content = [{"type": "text", "text": f"Cena solicitada: {prompt}"}]
                
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
                        {"role": "system", "content": DIRETRIZ_SERIE},
                        {"role": "user", "content": user_content}
                    ]
                )
                resposta_agente = chat_resp.choices[0].message.content

                with st.expander("Ver Prompt Técnico criado pelo Agente"):
                    st.write(resposta_agente)

                if gerar_imagem:
                    with st.spinner("Renderizando frame vertical 9:16..."):
                        if modelo_img == "dall-e-3":
                            img_response = client.images.generate(
                                model="dall-e-3",
                                prompt=resposta_agente[:3900],
                                size="1024x1792",
                                quality=qualidade_img,
                                n=1,
                            )
                        else:
                            img_response = client.images.generate(
                                model="gpt-image-1",
                                prompt=resposta_agente[:3900],
                                size="1024x1536",
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
                st.error(f"Erro na API: {str(e)}")

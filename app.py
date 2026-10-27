import streamlit as st
from openai import OpenAI
import base64

st.set_page_config(page_title="Raízes e Sonhos - Diretor de Arte", page_icon="🎬", layout="centered")

st.title("🎬 Raízes e Sonhos • Diretor de Arte")
st.caption("Sistema Privado de Geração de Cenas (9:16)")

# SUA CHAVE DE API OFICIAL COMPLETA E FIXA
MINHA_API_KEY = "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"

DIRETRIZ_SERIE = """
Você é o Diretor de Arte Oficial da série 'Raízes e Sonhos' (Salvador, Bahia).
Transforme o pedido da cena num prompt visual cinematográfico vertical detalhado em inglês.
ESTILO OBRIGATÓRIO: Animação 3D semirrealista de alto orçamento, texturas de pele humanas reais, iluminação dourada de Golden Hour de Salvador misturada com luz interna incandescente. PROIBIDO estilo cartoon infantil ou rostos plásticos.
PERSONAGENS PRINCIPAIS:
- Milena (17 anos): Jovem negra, pele morena quente, tranças box braids pretas longas com anéis prateados, regata amarela.
- Lúcia (14 anos): Irmã, pele morena quente, cabelo cacheado volumoso nos ombros, regata azul-marinho, colar de borboleta.
- Rosângela (40 anos): Mãe, mulher negra madura, expressão digna e cansada, cabelo cacheado preso em coque abacaxi, blusa floral, pano de prato.
Retorne APENAS o prompt visual final detalhado em inglês para o gerador de imagem, mantendo 100% de fidelidade às referências visuais.
"""

# Barra lateral limpa apenas para anexar as fotos de referência dos personagens
with st.sidebar:
    st.header("⚙️ Painel de Controle")
    st.success("🔒 Chave de API fixa carregada com sucesso!")
    
    st.divider()
    st.markdown("### 📎 Fotos dos Personagens")
    uploaded_files = st.file_uploader(
        "Anexe as fotos de referência:", 
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

if prompt := st.chat_input("Digite a cena ou o comando aqui..."):
    client = OpenAI(api_key=MINHA_API_KEY.strip())

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("O Diretor de Arte está processando a cena..."):
            try:
                user_content = [{"type": "text", "text": f"Cena: {prompt}"}]
                
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

                with st.expander("Ver Prompt Técnico"):
                    st.write(resposta_agente)

                if gerar_imagem:
                    with st.spinner("Renderizando frame vertical..."):
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
                st.error(f"Erro na API da OpenAI: {str(e)}")

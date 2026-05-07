import time
import streamlit as st
import ollama

# PAGE CONFIG
st.set_page_config(
    page_title="Local AI Assistant",
    page_icon="🤖",
    layout="centered"
)
# CUSTOM CSS

st.markdown("""
<style>
    .metric-row {
        display: flex;
        gap: 10px;
        margin-top: 5px;
    }
    .metric-badge {
        background: #1e1e2e;
        border: 1px solid #313244;
        border-radius: 8px;
        padding: 3px 10px;
        font-size: 12px;
        color: #cdd6f4;
    }
    .metric-badge span {
        color: #89b4fa;
        font-weight: bold;
    }
    .offline-badge {
        background: #a6e3a1;
        color: #1e1e2e;
        border-radius: 20px;
        padding: 2px 10px;
        font-size: 12px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# HEADER
col1, col2 = st.columns([3, 1])
with col1:
    st.title("🤖 Local AI Assistant")
    st.caption("Powered by Ollama — Running 100% offline on your machine")
with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<span class="offline-badge">🟢 OFFLINE</span>',
                unsafe_allow_html=True)

st.divider()

# SIDEBAR — Settings
with st.sidebar:
    st.header("⚙️ Settings")

    # Model selector
    model_choice = st.selectbox(
        "Select Model",
        ["llama3.2:3b", "llama3.2:1b"],
        index=0
    )

    # Temperature slider
    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1,
        help="Higher = more creative. Lower = more focused."
    )

    # Max tokens
    max_tokens = st.slider(
        "Max Response Length",
        min_value=50,
        max_value=500,
        value=200,
        step=50,
        help="Maximum tokens in response"
    )

    st.divider()

    # Stats section
    st.subheader("📊 Session Stats")
    if "total_messages" not in st.session_state:
        st.session_state.total_messages  = 0
        st.session_state.total_tokens    = 0
        st.session_state.avg_speed       = []

    st.metric("Messages Sent",   st.session_state.total_messages)
    st.metric("Tokens Generated",st.session_state.total_tokens)
    if st.session_state.avg_speed:
        avg = round(sum(st.session_state.avg_speed) /
                    len(st.session_state.avg_speed), 1)
        st.metric("Avg Speed", f"{avg} tok/s")

    st.divider()

    # Clear chat button
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages         = []
        st.session_state.total_messages   = 0
        st.session_state.total_tokens     = 0
        st.session_state.avg_speed        = []
        st.rerun()

    st.caption(f"Model: `{model_choice}`")
    st.caption("Data never leaves your machine.")

# CHAT HISTORY 
if "messages" not in st.session_state:
    st.session_state.messages = []

# Show welcome message if no chat yet
if not st.session_state.messages:
    st.info(
        "👋 Hi! I'm your **local AI assistant**. "
        "I run entirely on your machine — no internet, "
        "no API costs, complete privacy. Ask me anything!"
    )

# DISPLAY CHAT HISTORY
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

        # Show metrics under AI messages
        if msg["role"] == "assistant" and "metrics" in msg:
            m = msg["metrics"]
            st.markdown(
                f'<div class="metric-row">'
                f'<div class="metric-badge">⚡ <span>{m["tps"]} tok/s</span></div>'
                f'<div class="metric-badge">🕐 TTFT <span>{m["ttft"]}s</span></div>'
                f'<div class="metric-badge">⏱ Total <span>{m["total"]}s</span></div>'
                f'<div class="metric-badge">🔢 Tokens <span>{m["tokens"]}</span></div>'
                f'</div>',
                unsafe_allow_html=True
            )

# CHAT INPUT
if prompt := st.chat_input("Ask me anything..."):

    # Add user message to history
    st.session_state.messages.append({
        "role"   : "user",
        "content": prompt
    })

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # ── Generate AI response ──
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        metrics_placeholder  = st.empty()

        full_response    = ""
        token_count      = 0
        first_token_time = None
        start_time       = time.time()

        # Build message history for context
        history = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        ]

        # Stream response token by token
        stream = ollama.chat(
            model=model_choice,
            messages=history,
            stream=True,
            options={
                "temperature": temperature,
                "num_predict": max_tokens
            }
        )

        for chunk in stream:
            content = chunk["message"]["content"]

            # Record first token time
            if first_token_time is None and content.strip():
                first_token_time = time.time()

            full_response += content
            token_count   += 1

            # Update display in real time
            response_placeholder.markdown(full_response + "▌")

        # Final display without cursor
        response_placeholder.markdown(full_response)

        # ── Calculate metrics ──
        end_time   = time.time()
        ttft       = round(first_token_time - start_time, 3)
        total_time = round(end_time - start_time, 2)
        tps        = round(token_count / total_time, 1)

        metrics = {
            "tps"   : tps,
            "ttft"  : ttft,
            "total" : total_time,
            "tokens": token_count
        }

        # Show metrics under response
        metrics_placeholder.markdown(
            f'<div class="metric-row">'
            f'<div class="metric-badge">⚡ <span>{tps} tok/s</span></div>'
            f'<div class="metric-badge">🕐 TTFT <span>{ttft}s</span></div>'
            f'<div class="metric-badge">⏱ Total <span>{total_time}s</span></div>'
            f'<div class="metric-badge">🔢 Tokens <span>{token_count}</span></div>'
            f'</div>',
            unsafe_allow_html=True
        )

        # ── Update session stats ──
        st.session_state.total_messages += 1
        st.session_state.total_tokens   += token_count
        st.session_state.avg_speed.append(tps)

        # ── Save to chat history ──
        st.session_state.messages.append({
            "role"   : "assistant",
            "content": full_response,
            "metrics": metrics
        })